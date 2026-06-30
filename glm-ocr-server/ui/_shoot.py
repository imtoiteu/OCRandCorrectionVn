"""Helper: drive the running UI with a sample file and screenshot the result.
Usage: python ui/_shoot.py <sample_path> <out_prefix>
"""
import sys, time, pathlib
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:7860"
sample = sys.argv[1] if len(sys.argv) > 1 else "examples/source/paper.png"
prefix = sys.argv[2] if len(sys.argv) > 2 else "shot"
shot_dir = pathlib.Path("ui/_evidence"); shot_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 1700})
    pg.goto(URL, wait_until="networkidle"); time.sleep(2)
    pg.set_input_files('input[type="file"]', sample); time.sleep(1.5)
    pg.get_by_role("button", name="Run OCR").click()
    print("running OCR on", sample, "...")
    done = False
    for _ in range(180):
        vals = pg.eval_on_selector_all("textarea", "els => els.map(e => e.value).join('\\n')")
        if "Done in" in vals:
            done = True; break
        if "❌" in pg.inner_text("body"):
            print("error in UI"); break
        time.sleep(1)
    time.sleep(2)
    # ensure rendered-markdown tab is active
    try:
        pg.get_by_role("tab", name="Markdown (rendered)").click(); time.sleep(1.5)
    except Exception:
        pass
    pg.screenshot(path=str(shot_dir / f"{prefix}_rendered.png"), full_page=True)
    print("saved", shot_dir / f"{prefix}_rendered.png", "done=", done)
    b.close()
