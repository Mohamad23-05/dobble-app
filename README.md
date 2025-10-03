# Dobble/Spot It! Card Generator

## Introduction: Why Dobble works — finite projective planes

Dobble/Spot It! decks follow one elegant rule: any two cards share exactly one symbol. You get this “for free” if you
model a deck as a finite projective plane of order n.

## [Projective plane (order n)][projective-plane]

- There are exactly n² + n + 1 points and the same number of lines.
- Each line contains n + 1 points; each point lies on n + 1 lines.
- Any two distinct lines intersect in exactly one point.

## Mapping to Dobble

- Cards ↔ lines
- Symbols ↔ points

Therefore:

- Each card has n + 1 symbols.
- Any two cards share exactly one symbol (their unique intersection point).

## Deck consequences

- Number of cards: k = n² + n + 1
- Symbols per card: sc = n + 1
- Total distinct symbols: n² + n + 1

## Example: Fano plane (n = 2)

- k = 7 cards, sc = 3 symbols per card.
- Every pair of cards overlaps in exactly one symbol.

## Which orders n are allowed?

- For readability and practicality in this generator, the allowed values are: n ∈ {2, 3, 4, 5, 7}.
- For some other values (e.g., 6 or 10) no projective plane exists — the generator disables those.

## Quick reference

| n | Cards n²+n+1 | Symbols per card n+1 |
|---|--------------|----------------------|
| 2 | 7            | 3                    |
| 3 | 13           | 4                    |
| 4 | 21           | 5                    |
| 5 | 31           | 6                    |
| 7 | 57           | 8                    |

## Implementation note

This generator builds decks from a PG(2, n) incidence structure and assigns real symbols (text/icons/images) to points.
The resulting decks automatically satisfy the Dobble property.

Generate mathematically-correct Dobble/Spot It!-style card sets and export them as printable PDFs. The project includes:

- A FastAPI backend that validates parameters, generates card layouts, and renders PDFs.
- A Vue 3 + Vite + TypeScript frontend for an interactive UI.

<strong style='color: red'>Trademark</strong>: Dobble is a trademark of [Asmodee][asmodee]. This project is an
educational, open-source tool and is not
affiliated with Asmodee.

## Features

- Validate inputs by:
    - n (order of the projective plane)
    - k (number of cards)
    - sc (symbols per card)

- Generate the full card set for a given n, using provided symbol IDs.
- Export a high-quality, print-ready PDF with customizable page, card, and randomization settings.
- Deterministic layout support via a randomization seed.

## Tech Stack

- Backend: FastAPI (Python 3.13+)
- Frontend: Vue 3, Vite, TypeScript
- Package managers: pip (Python), npm (Node.js)

## Getting Started

### Prerequisites

- Python 3.13+ and virtualenv
- Node.js 22+ and npm
- Make sure ports 8000 (backend) and 5173 (frontend) are available locally

### 1) Backend Setup

- Create and activate a virtual environment:
     ```Bash
    #macOS/Linux:
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    ```Bash
     #Windows (PowerShell):
     py -m venv .venv
    ```
- Install dependencies:
  ```Bash
  pip install -r backend/requirements.txt
  ```
- Start the backend:
  ```Bash 
  #Linux/macOS
  uvicorn backend.main:app --reload --port 8000
  
  #Windows (PowerShell)
  python -m uvicorn backend.main:app --reload --port 8000 
  ```

#### Notes:

- The backend will serve at [http://localhost:8000](http://localhost:8000)
- API docs (if enabled) are usually at:
    - [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
    - [http://localhost:8000/redoc](http://localhost:8000/redoc) (Redoc)

### 2) Frontend Setup

- Install dependencies:
    ````Bash
    cd frontend 
    npm install
    ````
- Configure API base URL for the frontend:
    - Create a file named `.env.local` in the frontend root with:
    ````Bash
    VITE_API_BASE=http://localhost:8000
   ````
- Start the dev server:
    ```Bash
    npm run dev
    ```

The app will run at the URL printed by Vite (commonly [http://localhost:5173](http://localhost:5173)).

### 3) Verify Everything

- With the backend running on 8000 and the frontend on 5173, open the frontend URL in your browser and try generating
  cards.
- If your frontend uses an HTTP proxy instead of VITE_API_BASE, ensure the proxy config points
  to [http://localhost:8000](http://localhost:8000).

## API Quick Reference

- Base path: /dobble
- Validate parameters
    - GET /dobble/validate
    - Query params:
        - mode: "n" | "k" | "sc"
        - how_many: number

    - Example:
      ```Bash
       curl "http://localhost:8000/dobble/validate?mode=n&how_many=2"
      ```
    - Generate card indices mapped to provided symbols
        - POST /dobble/generate
        - Body:
       ```JSON
       {
          "n": 2,
          "symbols": [
              "S1",
              "S2",
              "S3",
              "S4",
              "S5",
              "S6",
              "S7"
          ]
       }
      ```
- Export a printable PDF
    - POST /dobble/export/pdf
    - Content-Type: application/json
    - Body shape (simplified):
  ```JSON
    {
      "n": 2,
      "symbolsPerCard": 3,
      "numCards": 7,
      "cards": [
        [ "S1", "S2", "S3"],
        [ "S1", "S4", "S5"],
        [ "S1", "S6", "S7"],
        [ "S2", "S4", "S6" ],
        [ "S2", "S5", "S7" ],
        [ "S3", "S4", "S7" ],
        [ "S3", "S5", "S6" ]
    ],
      "symbols": [
        { "id": "S0", "type": "text", "text": "S0", "fontFamily": "Helvetica-Bold", "fontWeight": 700 },
        { "id": "S1", "type": "text", "text": "S1", "fontFamily": "Helvetica-Bold", "fontWeight": 700 },
        { "id": "S2", "type": "text", "text": "S2", "fontFamily": "Helvetica-Bold", "fontWeight": 700 },
        { "id": "S3", "type": "text", "text": "S3", "fontFamily": "Helvetica-Bold", "fontWeight": 700 },
        { "id": "S4", "type": "text", "text": "S4", "fontFamily": "Helvetica-Bold", "fontWeight": 700 },
        { "id": "S5", "type": "text", "text": "S5", "fontFamily": "Helvetica-Bold", "fontWeight": 700 },
        { "id": "S6", "type": "text", "text": "S6", "fontFamily": "Helvetica-Bold", "fontWeight": 700 }
      ],
      "page": {
        "size": "A4",
        "orientation": "portrait",
        "marginMm": 10
      },
      "card": {
        "diameterMm": 80,
        "strokeMm": 0.4,
        "bleedMm": 0,
        "perPage": 2,
        "cutMarks": true
      },
      "randomization": {
        "seed": 42,
        "rotationDeg": { "min": 0, "max": 360 },
        "scale": { "min": 0.8, "max": 1.1 },
        "angularJitterDeg": 6,
        "radialJitterMm": 1.5,
        "ringStrategy": "single",
        "rotationMode": "bounded",
        "stepsDeg": null
      },
      "options": {}
   }
    ```
- Example for generating and exporting a PDF:
    1. Create a file named `payload.json` (already included in `backend` directory) in your working directory with your
       request body, like the one above.
    2. Run the following command:
    ```Bash
    #Linux/MacOS
    curl -X POST http://localhost:8000/dobble/export/pdf \
        -H "Content-Type: application/json" \
        -d @backend/payload.json \
        -o dobble_cards.pdf
    ```
   ```Bash
    #Windows (PowerShell)
    Invoke-WebRequest -Uri "http://localhost:8000/dobble/export/pdf" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -InFile "payload.json" `
    -OutFile "dobble_cards.pdf" 
    ```
- The response is a PDF file with Content-Disposition set to attachment.
- The PDF will be generated in the current working directory.
- The PDF will be named `"dobble_cards.pdf"`. if it fails to open, the `payload.json` file has error/s.

## Common Troubleshooting

- 404 from the frontend while calling the API:
    - Ensure VITE_API_BASE (or proxy) points to the correct backend URL and port.

- PDF export errors about images:
    - Image symbols must use data: URLs (e.g., data:image/png;base64,...).

- Card length mismatch:
    - Each card must contain exactly symbolsPerCard items.

- Invalid input on validation:
    - Some combinations of n, k, sc are mathematically invalid. Use the /validate endpoint first.

[asmodee]: https://www.asmodee.com/

[projective-plane]: https://en.wikipedia.org/wiki/Projective_plane