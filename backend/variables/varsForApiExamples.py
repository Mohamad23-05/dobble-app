from typing import List, Literal, TypedDict


class SymbolSpec(TypedDict):
    id: str
    type: Literal["text"]
    text: str
    fontFamily: str
    fontWeight: int


symbol: List[str] = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]

cards: List[List[str]] = [
    ["S1", "S2", "S3"],
    ["S1", "S4", "S5"],
    ["S1", "S6", "S7"],
    ["S2", "S4", "S6"],
    ["S2", "S5", "S7"],
    ["S3", "S4", "S7"],
    ["S3", "S5", "S6"]
]

symbols: List[SymbolSpec] = [
    {
        "id": "S1",
        "type": "text",
        "text": "S1",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    },
    {
        "id": "S2",
        "type": "text",
        "text": "S2",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    },
    {
        "id": "S3",
        "type": "text",
        "text": "S3",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    },
    {
        "id": "S4",
        "type": "text",
        "text": "S4",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    },
    {
        "id": "S5",
        "type": "text",
        "text": "S5",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    },
    {
        "id": "S6",
        "type": "text",
        "text": "S6",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    },
    {
        "id": "S7",
        "type": "text",
        "text": "S7",
        "fontFamily": "Helvetica-Bold",
        "fontWeight": 700
    }
]
