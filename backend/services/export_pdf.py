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
        rconf: RandomSpec,
) -> List[Tuple[float, float, float, float]]:
    """
    Berechnet die Symbol-Positionen für genau einen Ring (max. 8 Symbole pro Karte).

    Rückgabe: Liste von Tupeln (x_mm, y_mm, rot_deg, scale) relativ zur Kartenmitte.
    - x_mm, y_mm: Position in Millimetern (relativ zum Kartenmittelpunkt)
    - rot_deg: Rotation des Symbols in Grad
    - scale: Skalierungsfaktor (dimensionlos)

    Verwendete rconf-Felder:
      - angular_jitter_deg: max. Winkeljitter (+/-)
      - radial_jitter_mm:  max. radialer Jitter (+/-)
      - rotation_deg:      Optional RangeSpec(min, max) für Symbolrotation
      - scale:             RangeSpec(min, max) als Basisskalierung
      - seed:              Optional Seed für rnd (hier nicht neu gesetzt)
      - (optional) mix:            Gewichte (small, medium, large), default (0.4, 0.4, 0.2)
      - (optional) mul_small:      (lo, hi) Multiplikatorbereich für "small",  default (0.80, 0.95)
      - (optional) mul_medium:     (lo, hi) Multiplikatorbereich für "medium", default (0.95, 1.10)
      - (optional) mul_large:      (lo, hi) Multiplikatorbereich für "large",  default (1.15, 1.50)
      - (optional) ring_radius_ratio: Verhältnis Ringradius/Kartenradius, default 0.75
    """
    base_angle = 360.0 / n_slots
    positions: List[Tuple[float, float, float, float]] = []

    # Fester Ein-Ring-Ansatz
    ring_radius_ratio = getattr(rconf, "ring_radius_ratio", 0.75)
    ring_r = max(0.0, card_radius_mm * float(ring_radius_ratio))

    # Größenkategorien (einheitlich für den Ring)
    mix = getattr(rconf, "mix", (0.60, 0.30, 0.10))  # (small, medium, large)
    mul_small = getattr(rconf, "mul_small", (0.80, 0.95))
    mul_medium = getattr(rconf, "mul_medium", (0.95, 1.10))
    mul_large = getattr(rconf, "mul_large", (1.15, 1.50))

    def _choose_size_category() -> str:
        r = rnd.random()
        a, b, c = mix
        # numerisch robust clampen
        a = max(0.0, min(1.0, a))
        b = max(0.0, min(1.0 - a, b))
        # c implizit = 1 - (a+b); bei kleiner Rundungsabweichung tolerieren
        # small, medium, large
        if r < a:
            return "small"
        if r < a + b:
            return "medium"
        return "large"

    def _mul_range(cat: str) -> Tuple[float, float]:
        return {"small": mul_small, "medium": mul_medium, "large": mul_large}[cat]

    # Rotationseinstellungen
    rot_min = rconf.rotation_deg.min if getattr(rconf, "rotation_deg", None) else 0.0
    rot_max = rconf.rotation_deg.max if getattr(rconf, "rotation_deg", None) else 0.0

    # Basisskalierung
    base_scale_min = float(rconf.scale.min)
    base_scale_max = float(rconf.scale.max)

    for i in range(n_slots):
        # Winkel gleichmäßig + Jitter
        angle = base_angle * i
        angle += _rand_between(rnd, -rconf.angular_jitter_deg, rconf.angular_jitter_deg)

        # Radius + radialer Jitter
        rj = _rand_between(rnd, -rconf.radial_jitter_mm, rconf.radial_jitter_mm)
        rr = max(0.0, ring_r + rj)

        # Polarkoordinaten -> kartesisch (mm)
        theta = math.radians(angle)
        x = rr * math.cos(theta)
        y = rr * math.sin(theta)

        # Symbolrotation
        rot = _rand_between(rnd, float(rot_min), float(rot_max))

        # Basisscale * größenkategorie
        base_sc = _rand_between(rnd, base_scale_min, base_scale_max)
        cat = _choose_size_category()
        lo, hi = _mul_range(cat)
        sc = base_sc * _rand_between(rnd, float(lo), float(hi))

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
    # Use radius, not diameter
    p.circle(cx, cy, _mm(radius_mm))
    canvas.saveState()
    canvas.clipPath(p, stroke=0, fill=0)

    # layout position
    rnd = random.Random(rconf.seed or random.randrange(1 << 30))
    positions = layout_card(len(card), radius_mm, rnd, rconf)

    # draw card
    for sys, pos in zip(card, positions):
        x_mm, y_mm, rot_degrees, scale = pos
        canvas.saveState()
        canvas.translate(cx + _mm(x_mm), cy + _mm(y_mm))
        canvas.rotate(rot_degrees)

        if sys["type"] == "image":
            img: ImageReader = sys["image"]
            base = _mm(diameter_mm * 0.2) * scale
            canvas.drawImage(img, -base / 2, -base / 2, width=base, height=base, mask='auto')
        else:
            txt = str(sys["text"])
            # honor 'font_family' if present
            font = str(sys.get("font_family") or font_fallback)
            size_pt = _mm(diameter_mm * 0.16) * scale
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
    # usable area inside margins
    inner_w = page_w - 2 * _mm(margin_mm)
    inner_h = page_h - 2 * _mm(margin_mm)

    # required size per card (in points)
    need_w = _mm(diameter_mm)
    need_h = _mm(diameter_mm)

    # Find a cols x rows layout that fits without overlap
    best_cols = 1
    best_rows = per_page
    for cols in range(1, per_page + 1):
        rows = math.ceil(per_page / cols)
        if cols * need_w <= inner_w and rows * need_h <= inner_h:
            best_cols = cols
            best_rows = rows
        else:
            # keep searching; we want the largest cols that still fit
            continue

    cols = best_cols
    rows = best_rows

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
    # set the page size correctly
    c = canvas.Canvas(buf, pagesize=(w, h))

    centers = paginate_cards(c, w, h, page.margin_mm, card.diameter_mm, card.per_page)
    # draw cards, paginating to fit page size
    idx = 0
    while idx < len(cards):
        for cx, cy in centers:
            if idx >= len(cards):
                break

            # draw card
            draw_card(
                canvas=c,
                cx=cx,
                cy=cy,
                card=cards[idx],
                diameter_mm=card.diameter_mm,
                stroke_mm=card.stroke_mm,
                rconf=rconf,
            )

            # cut marks optional
            if card.cut_marks:
                r = _mm(card.diameter_mm / 2)
                c.setLineWidth(0.5)  # thin lines
                for ang in (0, 90, 180, 270):
                    th = _deg2rad(ang)
                    ox = math.cos(th) * (r + _mm(3))
                    oy = math.sin(th) * (r + _mm(3))
                    c.line(cx + ox - 6, cy + oy, cx + ox + 6, cy + oy)
            # advance to next card after drawing each one
            idx += 1
        c.showPage()

    c.save()
    return buf.getvalue()
