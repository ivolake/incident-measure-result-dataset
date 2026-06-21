from __future__ import annotations

import sys

from incident_measure_result.cli import main

if __name__ == "__main__":
    sys.argv.insert(1, "evaluate")
    main()
