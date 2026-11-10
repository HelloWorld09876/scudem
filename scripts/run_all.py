import runpy
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

steps = sorted(p for p in HERE.glob("[0-9][0-9]_*.py"))
if len(sys.argv) > 1:
    steps = [p for p in steps if any(p.name.startswith(a) for a in sys.argv[1:])]

start = time.time()
for step in steps:
    t0 = time.time()
    print(f"\n[{step.stem}]")
    runpy.run_path(str(step), run_name="__main__")
    print(f"  done in {time.time() - t0:.1f} s")
runpy.run_path(str(HERE / "export_numbers.py"), run_name="__main__")
print(f"\nPipeline finished in {time.time() - start:.0f} s")
