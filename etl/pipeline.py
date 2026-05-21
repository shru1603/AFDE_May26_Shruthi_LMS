"""
etl/pipeline.py

Orchestrates the full ETL pipeline: Extract → Transform → Load.

Run from project root:
    python -m etl.pipeline

The analytics tables are recreated fresh on every run.
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

    # Drop and recreate analytics tables so schema changes are always applied
    analytics_tables = [
        models.AnalyticsPopularBooks.__table__,
        models.AnalyticsCategoryStats.__table__,
        models.AnalyticsMonthlyTrends.__table__,
        models.AnalyticsOverdue.__table__,
    ]
    for table in analytics_tables:
        table.drop(bind=engine, checkfirst=True)
    models.Base.metadata.create_all(bind=engine)

    # Step 1 — Extract
    extracted = extract.run()

    # Step 2 — Transform
    transformed = transform.run(extracted)

    # Step 3 — Load
    load.run(transformed)

    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print("\n" + "=" * 50)
    print(f"Pipeline complete in {elapsed:.2f}s")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run()
