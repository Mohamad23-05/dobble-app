from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

from ..services.dobble_logic import get_params, generate_projective_plane as gen_plane

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
