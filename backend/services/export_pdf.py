import io
import math
import random
import re
import base64
import sys
from dataclasses import dataclass, field
from os import scandir
from typing import Dict, List, Optional, Tuple, Union, Literal

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# -- Model --
@dataclass
class PageSpec:
    size: Union[int, Tuple[float, float]]
    orientation: str
    margin_mm: float


@dataclass
class CardSpec:
    diameter_mm: float
    stroke_mm: float
    bleed_mm: float
    per_page: int
    cut_marks: bool


@dataclass
class RangeSpec:
    min: float
    max: float


@dataclass
class RandomSpec:
    seed: Optional[int] = None
    rotation_mode: str = "any"  # "any", "bounded", "steps90", "steps"
    steps_deg: Optional[float] = None
    rotation_deg: Optional[RangeSpec] = None
    scale: RangeSpec = field(default_factory=lambda: RangeSpec(1.0, 1.0))
    angular_jitter_deg: float = 0.0
    radial_jitter_mm: float = 0.0
    ring_strategy: str = "auto"


# -- Utilities --
_DATA_URL_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<b64>.+)$")


def _mm(val: float) -> float:
    return val * mm


def _page_size_mm(spec: PageSpec) -> Tuple[float, float]:
    if isinstance(spec.size, str):
        if spec.size.lower() == "a4":
            w, h = A4
        else:
            raise ValueError(f"Invalid size specification: {spec.size}")
    else:
        w, h = _mm(spec.size[0]), _mm(spec.size[1])
    if spec.orientation == "landscape":
        w, h = max(w, h), min(w, h)
    else:
        w, h = min(w, h), max(w, h)
    return w, h


def _decode_data_url(url: str) -> ImageReader:
    match = _DATA_URL_RE.match(url)
    if not match:
        raise ValueError(f"Invalid data URL: {url}")
    base = base64.b64decode(match.group("b64"))
    return ImageReader(io.BytesIO(base))


def _ensure_font(name: str, path: Optional[str] = None):
    # You can register extra fonts here if needed
    if name not in pdfmetrics.getRegisteredFontNames():
        if path:
            pdfmetrics.registerFont(TTFont(name, path))
        else:
            # Will fallback to built-ins (Helvetica, Times, Courier)
            pass


# placement helpers
def _rand_between(rng: random.Random, lo: float, hi: float) -> float:
    return rng.uniform(lo, hi)


def _deg2rad(deg: float) -> float:
    return deg * math.pi / 180


# layout: return list of (x_mm, y_mm, angle_deg, scale) for each symbol slot
def layout_card(
        n_slots: int,
        card_radius_mm: float,
        rnd: random.Random,
        rconf: RandomSpec
) -> list[tuple[float, float, float, float]]:
    base_angle = 360 / n_slots
    positions: List[Tuple[float, float, float, float]] = []

    # ring strategy
    if rconf.ring_strategy == "twp_rings" and n_slots >= 8:
        inner = round(n_slots * 0.45)
        outer = n_slots - inner
        ring_break = inner
        inner_r = card_radius_mm * 0.55
        outer_r = card_radius_mm * 0.90
    elif rconf.ring_strategy == "single":
        ring_break = n_slots
        inner_r = outer_r = card_radius_mm * 0.75
    else:
        if n_slots >= 8:
            ring_break = math.floor(n_slots / 2)
            inner_r = card_radius_mm * 0.58
            outer_r = card_radius_mm * 0.88
        else:
            ring_break = n_slots
            inner_r = outer_r = card_radius_mm * 0.75

    for i in range(n_slots):
        angle = base_angle + i
        angle += _rand_between(rnd, -rconf.angular_jitter_deg, rconf.angular_jitter_deg)
        ring_r = inner_r if i < ring_break else outer_r
        rj = _rand_between(rnd, -rconf.radial_jitter_mm, rconf.radial_jitter_mm)
        rr = max(0, ring_r + rj)
        th = _deg2rad(angle)
        x = rr * math.cos(th)
        y = rr * math.sin(th)
        rot = _rand_between(rnd, -rconf.rotation_deg.min, rconf.rotation_deg.max)
        sc = _rand_between(rnd, -rconf.scale.min, rconf.scale.max)
        positions.append((x, y, rot, sc))
    return positions


# draw one circular card at (cx, cy) center; diameter in mm
def draw_card(
        canvas: canvas.Canvas,
        cx: float, cy: float,
        card: List[Dict[str, Union[str, int]]],
        diameter_mm: float,
        stroke_mm: float,
        rconf: RandomSpec,
        font_fallback: str = "Helvetica-Bold"
):
    radius_mm = diameter_mm / 2
    p = canvas.beginPath()
    p.circle(cx, cy, _mm(diameter_mm))
    canvas.saveState()
    canvas.clipPath(p, stroke=0, fill=0)

    # layout position
    rnd = random.Random(rconf.seed or random.randrange(1 << 30))
    positions = layout_card(len(card), radius_mm, rnd, rconf)

    # draw card
    for (sys, pos) in zip(card, positions):
        x_mm, y_mm, rot_degrees, scale = pos
        canvas.saveState()
        canvas.translate(cx + _mm(x_mm), cy + _mm(y_mm))
        canvas.rotate(rot_degrees)

        if sys["type"] == "image":
            img: ImageReader = sys["image"]
            base = _mm(diameter_mm * 0.2) * scale
            canvas.drawImage(img, -base / 2, -base / 2, width=base, height=base, mask='auto')
        else:
            # text symbol
            txt = str(sys["text"])
            font = str(sys.get("font") or font_fallback)
            size_pt = _mm(diameter_mm * 0.16) * scale  # _mm converts mm to points
            canvas.setFont(font, size_pt)
            canvas.setFillGray(0)
            w = canvas.stringWidth(txt, font, size_pt)
            canvas.drawString(-w / 2, -w / 2.8, txt)

        canvas.restoreState()

    canvas.restoreState()

    if stroke_mm > 0:
        canvas.setLineWidth(_mm(stroke_mm))
        canvas.circle(cx, cy, _mm(radius_mm))


def paginate_cards(
        canvas: canvas.Canvas,
        page_w: float, page_h: float,
        margin_mm: float,
        diameter_mm: float,
        per_page: int,

) -> list[tuple[float, float]]:
    # 2 x 3 Grid
    inner_w = page_w * _mm(margin_mm)
    inner_h = page_h * _mm(margin_mm)

    # layout
    cols = 3 if per_page >= 3 else per_page
    rows = math.ceil(per_page / cols)

    cell_w = inner_w / cols
    cell_h = inner_h / rows

    centers: List[tuple[float, float]] = []
    for row in range(rows):
        for col in range(cols):
            if len(centers) >= per_page: break
            cx = _mm(margin_mm) + cell_w * (col + 0.5)
            cy = page_h - (_mm(margin_mm) + cell_h * (row + 0.5))
            centers.append((cx, cy))
    return centers


def create_pdf(
        cards: List[List[Dict]],
        page: PageSpec,
        card: CardSpec,
        rconf: RandomSpec,
        fonts: Optional[Dict[str, str]] = None  # { "Inter": "/path/Inter-Bold.ttf" }
) -> bytes:
    # register fonts
    if fonts:
        for fname, fpath in fonts.items():
            _ensure_font(fname, fpath)
    w, h = _page_size_mm(page)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagenumbers=(w, h))

    centers = paginate_cards(c, w, h, page.margin_mm, card.diameter_mm, card.per_page)

    idx = 0
    while idx < len(cards):
        for cx, cy in centers:
            if idx >= len(cards):
                break
            draw_card(
                canvas=c,
                cx=cx, cy=cy,
                card=cards[idx],
                diameter_mm=card.diameter_mm,
                stroke_mm=card.stroke_mm,
                rconf=rconf,
            )
            # cut marks optional
            if card.cut_marks:
                r = _mm(card.diameter_mm / 2)
                c.setLineWidth(0.5)
                for ang in (0, 90, 180, 270):
                    th = _deg2rad(ang)
                    ox = math.cos(th) * (r + _mm(3))
                    oy = math.sin(th) * (r + _mm(3))
                    c.line(cx + ox - 6, cy + oy, cx + ox + 6, cy + oy)
        c.showPage()
        idx += len(centers)

    c.save()
    return buf.getvalue()
