from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incident_measure_result.cli import main

if __name__ == "__main__":
    sys.argv.insert(1, "rank-bm25")
    main()
