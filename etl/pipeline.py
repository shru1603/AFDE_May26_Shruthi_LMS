"""
etl/pipeline.py

Orchestrates the full ETL pipeline: Extract -> Transform -> Load.

CSV data is cleaned and inserted into the operational tables
(books, borrowers, transactions). Analytics are computed live
from those tables — no separate analytics tables required.

Run from project root:
    python -m etl.pipeline
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import engine
from database import models
from etl import extract, transform, load


def run():
    start = datetime.now()
    print("\n" + "=" * 50)
    print("LMS ETL PIPELINE")
    print(f"Started : {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Ensure all tables exist
    models.Base.metadata.create_all(bind=engine)

    extracted  = extract.run()
    transformed = transform.run(extracted)
    load.run(transformed)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print("\n" + "=" * 50)
    print(f"Pipeline complete in {elapsed:.2f}s")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run()
