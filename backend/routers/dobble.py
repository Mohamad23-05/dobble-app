from fastapi import APIRouter, Query, HTTPException, Response
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Literal, Optional, Dict, Union

from ..services.dobble_logic import get_params, generate_projective_plane as gen_plane
from ..services.export_pdf import (PageSpec, CardSpec, RandomSpec, RangeSpec, create_pdf, _decode_data_url)
from ..variables.varsForApiExamples import (symbol, cards, symbols)

router = APIRouter(prefix="/dobble", tags=["dobble"])


# Common base to keep alias handling and future shared config in one place
class ApiResponse(BaseModel):
    model_config = {
        "populate_by_name": True
    }


class ValidateResponse(ApiResponse):
    valid: bool = True
    message: str = "Valid input"
    n: Optional[int] = None
    symbols_per_card: Optional[int] = None
    num_cards: Optional[int] = None
    total_symbols: Optional[int] = None

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "valid": True,
                "message": "Valid input",
                "n": 2,
                "symbolsPerCard": 3,
                "numCards": 7,
                "totalSymbols": 7
            }
        }
    }


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
        # Return a proper error status instead of 200
        raise HTTPException(status_code=400, detail="you entered an invalid parameter")

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
    symbols: List[str] = Field(default=symbol)  # length must be n^2 + n + 1


class GenerateResponse(ApiResponse):
    symbols_per_card: int = Field(default=3, alias="symbolsPerCard")
    num_cards: int = Field(default=7, alias="numCards")
    cards: List[List[str]] = Field(default=cards, alias="cards")


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
    font_family: Optional[str] = Field(default="Helvetica-Bold", alias="fontFamily")
    font_weight: Optional[int] = Field(default=700, alias="fontWeight")

    model_config = {
        "populate_by_name": True
    }


class SymbolImage(BaseModel):
    id: str
    type: Literal["image"]
    src: str  # data: URL


SymbolDef = Union[SymbolText, SymbolImage]


class PageOpts(BaseModel):
    size: Union[Literal["A4", "Letter"], Dict[str, float]] = "A4"
    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_mm: float = Field(default=10.0, alias="marginMm")

    model_config = {
        "populate_by_name": True
    }


class CardOpts(BaseModel):
    diameter_mm: float = Field(default=80.0, alias="diameterMm")
    stroke_mm: float = Field(default=0.4, alias="strokeMm")
    bleed_mm: float = Field(default=0.0, alias="bleedMm")
    per_page: int = Field(default=2, alias="perPage")
    cut_marks: bool = Field(default=True, alias="cutMarks")

    model_config = {
        "populate_by_name": True
    }


class RangeModel(BaseModel):
    min: float
    max: float


class RandomOpts(BaseModel):
    seed: Optional[int] = None
    rotation_deg: RangeModel = Field(default_factory=lambda: RangeModel(min=0, max=360), alias="rotationDeg")
    scale: RangeModel = RangeModel(min=0.8, max=1.1)
    angular_jitter_deg: float = Field(default=6.0, alias="angularJitterDeg")
    radial_jitter_mm: float = Field(default=1.5, alias="radialJitterMm")
    ring_strategy: Literal["single"] = Field(default="single", alias="ringStrategy")
    rotation_mode: Literal["bounded"] = Field(default="bounded", alias="rotationMode")
    steps_deg: Optional[float] = Field(default=None, alias="stepsDeg")

    model_config = {
        "populate_by_name": True
    }

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
    n: int = Field(default=2, alias="n")
    symbols_per_card: int = Field(default=3, alias="symbolsPerCard")
    num_cards: int = Field(default=7, alias="numCards")
    cards: List[List[str]] = Field(default=cards, alias="cards")
    symbols: List[SymbolDef] = Field(
        default=symbols, alias="symbols")  # for educational purposes, we keep the original symbol list of texts
    page: PageOpts = PageOpts()
    card: CardOpts = CardOpts()
    randomization: RandomOpts = RandomOpts()
    options: Dict[str, Union[bool, int]] = {}

    model_config = {
        "populate_by_name": True
    }


class ExportError(ApiResponse):
    error: str
    message: str

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "error": "Bad Request",
                "message": "Symbol 'S42' referenced on card 3 but not provided"
            }
        }
    }


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
        # Accept multiple key styles for custom size
        size_dict = req.page.size
        # common variants
        w = (
                size_dict.get("w_mm")
                or size_dict.get("w")
                or size_dict.get("width_mm")
                or size_dict.get("width")
                or size_dict.get("wMm")
                or size_dict.get("widthMm")
        )
        h = (
                size_dict.get("h_mm")
                or size_dict.get("h")
                or size_dict.get("height_mm")
                or size_dict.get("height")
                or size_dict.get("hMm")
                or size_dict.get("heightMm")
        )
        if w is None or h is None:
            raise HTTPException(status_code=400, detail="Custom page.size must include width/height in mm")
        # custom size tuple (w_mm, h_mm)
        page_size = (float(w), float(h))

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
