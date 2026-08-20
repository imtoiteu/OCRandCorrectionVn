# Report figures — OCRandCorrectionVn

Editable diagrams for `BAO_CAO_DE_TAI_OCR_DA_HIEU_CHINH.docx`, generated from the
source code of the repository (not from the report text).

```
report_figures/
├── FIGURE_INDEX.md        figure ↔ file ↔ source-file ↔ status table
├── MANUAL_COMPLETION.md   what still has to be supplied by hand, and how
├── diagram_engine.py      rendering engine (copy of the project's own generator)
├── build_ch2.py           figure definitions, Chapter 2
├── build_ch3.py           figure definitions, Chapter 3
├── build_ch4.py           figure definitions, Chapter 4
├── chapter2/   10 figures  (2.1 – 2.10)
├── chapter3/    6 figures  (3.1, 3.2, 3.6, 3.7, 3.8, 3.9)
└── chapter4/    5 figures  (4.1 – 4.5)
```

## Ground rules that were followed

* **The source code is the only authority.** `README.md` and `docs/` inside
  `glm-ocr-ui/` describe a larger product (RAG chat, translation, summarization,
  an LLM agent, a Tauri desktop app). Those modules are not in this build, so they
  are not in the diagrams — the figures say so explicitly instead.
* Nothing is invented: no component, API, table, engine, port, security mechanism,
  benchmark number or UI screen appears unless it exists in the code.
* Where the report asks for something the implementation does not have, the figure
  is marked `MANUAL COMPLETION REQUIRED` in-place, and `MANUAL_COMPLETION.md`
  explains exactly what to supply.
* No file inside `OCRandCorrectionVn/` was modified.

## Using the files

**draw.io / diagrams.net** — open any `.drawio` directly (File ▸ Open From ▸
Device, or drag it onto <https://app.diagrams.net>). Every box, arrow and label is
an individual, editable cell; containers are real swimlanes and the sequence
diagram uses native UML lifelines and an `alt` frame. There is no embedded image
anywhere.

**Microsoft Word** — Insert ▸ Pictures ▸ This Device ▸ select the `.svg`. The
diagrams are wide (roughly 1300–1440 px), so after inserting set the picture width
to the text-column width; being vector, they stay sharp at any size and when
printed. If your Word version rasterizes SVG on export, re-export the `.drawio`
from diagrams.net as PDF or as PNG at 300 dpi instead.

**After editing a `.drawio`**, re-export the SVG from diagrams.net
(File ▸ Export as ▸ SVG, uncheck "Include a copy of my diagram" if you want a
smaller file) so the two stay in sync — or edit the corresponding `build_ch*.py`
and regenerate both:

```bash
python3 build_ch2.py && python3 build_ch3.py && python3 build_ch4.py
```

## Visual conventions (consistent across all chapters)

| Colour | Meaning |
|---|---|
| Blue | presentation / browser tier |
| Indigo | Flask application layer, HTTP routes |
| Green | service layer (`services/`) |
| Teal | OCR engines and adapters |
| Orange | external processes and models (GLM-OCR SDK, MLX server) |
| Purple | Vietnamese correction pipeline and providers |
| Grey | data stores and persisted artifacts |
| Yellow | notes and decision points |
| Red outline on white | not implemented / manual completion required |

Solid arrows are calls or data flow; dashed arrows are optional, conditional or
informational relationships. Titles carry the report's own figure numbering in
Vietnamese; the diagram bodies use English so that the labels match the identifiers
in the source code.
