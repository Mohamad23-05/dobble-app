from fastapi import APIRouter, Query
from pydantic import BaseModel
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
    n: int


class GenerateResponse(BaseModel):
    cards_idx: List[List[int]]
    symbols_per_card: int
    num_cards: int


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    cards = gen_plane(req.n)
    return {
        "cards_idx": cards,
        "symbols_per_card": req.n + 1,
        "num_cards": req.n ** 2 + req.n + 1,
    }
