from http.client import HTTPException

from fastapi import APIRouter, Query, HTTPException, Response
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Literal, Optional, Dict, Union

from ..services.dobble_logic import get_params, generate_projective_plane as gen_plane
from ..services.export_pdf import (
    PageSpec, CardSpec, RandomSpec, RangeSpec, create_pdf, _decode_data_url
)

router = APIRouter(prefix="/dobble", tags=["dobble"])


class ValidateResponse(BaseModel):
    valid: bool
    message: str
    n: Optional[int] = None
    symbols_per_card: Optional[int] = None
    num_cards: Optional[int] = None
    total_symbols: Optional[int] = None


@router.get("/validate", response_model=ValidateResponse)
def validate(
        mode: Literal["n", "k", "sc"] = Query(...),
        how_many: int = Query(...)
):
    if mode == "n":
        params = get_params(n=how_many)
    elif mode == "k":
        params = get_params(num_cards=how_many)
    else:
        params = get_params(symbols_per_card=how_many)

    if params is None:
        return ValidateResponse(valid=False, message="Invalid input")

    return ValidateResponse(
        valid=True,
        message="Valid input",
        n=params["n"],
        symbols_per_card=params["symbols_per_card"],
        num_cards=params["num_cards"],
        total_symbols=params["num_cards"],
    )


class GenerateRequest(BaseModel):
    n: int = Field(..., ge=2)
    symbols: List[str]  # length must be n^2 + n + 1


class GenerateResponse(BaseModel):
    symbols_per_card: int
    num_cards: int
    cards: List[List[str]]


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    expected = req.n ** 2 + req.n + 1
    if len(req.symbols) != expected:
        raise ValueError(f"Expected {expected} symbols, got {len(req.symbols)}")

    card_idx = gen_plane(req.n)

    cards = [[req.symbols[i] for i in card] for card in card_idx]

    return {
        "symbols_per_card": req.n + 1,
        "num_cards": expected,
        "cards": cards,
    }


# -- Export PDF --

class SymbolText(BaseModel):
    id: str
    type: Literal["text"]
    text: str
    font_family: Optional[str] = "Helvetica-Bold"
    font_weight: Optional[int] = 700


class SymbolImage(BaseModel):
    id: str
    type: Literal["image"]
    src: str  # data: URL


SymbolDef = Union[SymbolText, SymbolImage]


class PageOpts(BaseModel):
    size: Union[Literal["A4", "Letter"], Dict[str, float]] = "A4"
    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_mm: float = 10.0


class CardOpts(BaseModel):
    diameter_mm: float = 120.0
    stroke_mm: float = 0.4
    bleed_mm: float = 0.0
    per_page: int = 2
    cut_marks: bool = True


class RangeModel(BaseModel):
    min: float
    max: float


class RandomOpts(BaseModel):
    seed: Optional[int] = None
    rotation_deg: RangeModel = RangeModel(min=0, max=360)
    scale: RangeModel = RangeModel(min=0.8, max=1.1)
    angular_jitter_deg: float = 6.0
    radial_jitter_mm: float = 1.5
    ring_strategy: Literal["auto", "single", "two_rings"] = "auto"
    rotation_mode: Literal["any", "bounded", "steps90", "steps"] = "any"
    steps_deg: Optional[float] = None

    @model_validator(mode="after")
    def check_rotation(cls, values):
        mode = values.rotation_mode
        steps = values.steps_deg
        rot: RangeModel = values.rotation_deg

        if mode in ("any", "bounded"):
            if rot.min > rot.max:
                raise ValueError("rotation_deg.min must be <= rotation_deg.max")
        elif mode == "steps":
            if not steps or steps <= 0:
                raise ValueError("steps_deg must be > 0 when rotation_mode='steps'")
        return values


class ExportRequest(BaseModel):
    n: int
    symbols_per_card: int
    num_cards: int
    cards: List[List[str]]  # <-- keep as strings
    symbols: List[SymbolDef]  # <-- objects defined as SymbolText / SymbolImage
    page: PageOpts = PageOpts()
    card: CardOpts = CardOpts()
    randomization: RandomOpts = RandomOpts()
    options: Dict[str, Union[bool, int]] = {}


class ExportError(BaseModel):
    error: str
    message: str


def _build_symbol_lookup(symbols: List[SymbolDef]) -> Dict[str, Dict]:
    lut: Dict[str, Dict] = {}
    for symbol in symbols:
        if isinstance(symbol, SymbolText):
            lut[symbol.id] = {"type": "text", "text": symbol.text, "font_family": symbol.font_family}
        else:
            try:
                img = _decode_data_url(symbol.src)
            except Exception:
                raise HTTPException(status_code=400,
                                    detail=f"Invalid or unsupported image for symbol '{symbol.id}' (expect data: URL)")
            lut[symbol.id] = {"type": "image", "image": img}
    return lut


@router.post("/export/pdf", responses={400: {"model": ExportError}})
def export_pdf(req: ExportRequest):
    # 1) Build symbol lookup (id -> resolved dict)
    lut = _build_symbol_lookup(req.symbols)

    # 2) Validate & resolve cards (ids -> symbol dicts)
    resolved_cards: List[List[Dict]] = []
    for ci, card_ids in enumerate(req.cards):
        if len(card_ids) != req.symbols_per_card:
            raise HTTPException(status_code=400, detail=f"Card {ci} length mismatch")
        resolved = []
        for sid in card_ids:
            if sid not in lut:
                raise HTTPException(
                    status_code=400,
                    detail=f"Symbol '{sid}' referenced on card {ci} but not provided"
                )
            resolved.append(lut[sid])
        resolved_cards.append(resolved)

    # 3) Convert PageOpts -> PageSpec
    if isinstance(req.page.size, str):
        page_size = req.page.size  # "A4" | "Letter"
    else:
        # custom size object { w_mm, h_mm }
        page_size = (req.page.size.w_mm, req.page.size.h_mm)

    page = PageSpec(
        size=page_size,
        orientation=req.page.orientation,
        margin_mm=req.page.margin_mm,
    )

    # 4) Convert CardOpts -> CardSpec
    card = CardSpec(
        diameter_mm=req.card.diameter_mm,
        stroke_mm=req.card.stroke_mm,
        bleed_mm=req.card.bleed_mm,
        per_page=req.card.per_page,
        cut_marks=req.card.cut_marks,
    )

    # 5) Convert RandomOpts (Pydantic) -> RandomSpec (dataclass)
    rnd = RandomSpec(
        seed=req.randomization.seed,
        rotation_deg=RangeSpec(
            min=req.randomization.rotation_deg.min,
            max=req.randomization.rotation_deg.max
        ),
        scale=RangeSpec(
            min=req.randomization.scale.min,
            max=req.randomization.scale.max
        ),
        angular_jitter_deg=req.randomization.angular_jitter_deg,
        radial_jitter_mm=req.randomization.radial_jitter_mm,
        ring_strategy=req.randomization.ring_strategy,
        rotation_mode=req.randomization.rotation_mode,  # "any" | "bounded" | "steps90" | "steps"
        steps_deg=req.randomization.steps_deg,
    )

    # 6) Render PDF
    pdf_bytes = create_pdf(
        cards=resolved_cards,
        page=page,
        card=card,
        rconf=rnd,
        fonts=None,
    )

    # 7) Return file
    headers = {
        "Content-Disposition": 'attachment; filename="dobble_cards.pdf"',
        # Optionally echo seed for reproducibility:
        "X-Seed": str(rnd.seed or 0),
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
