from fastapi import APIRouter, UploadFile, File
from typing import Optional
import shutil, os

router = APIRouter(prefix="/etl", tags=["ETL"])

DATASETS_DIR = "datasets"


@router.post("/upload")
async def upload_and_run(
    books_csv: Optional[UploadFile] = File(None),
    borrowers_csv: Optional[UploadFile] = File(None),
    transactions_csv: Optional[UploadFile] = File(None),
):
    os.makedirs(DATASETS_DIR, exist_ok=True)

    uploaded = []
    for upload, filename in [
        (books_csv, "books.csv"),
        (borrowers_csv, "borrowers.csv"),
        (transactions_csv, "transactions.csv"),
    ]:
        if upload and upload.filename:
            dest = os.path.join(DATASETS_DIR, filename)
            with open(dest, "wb") as f:
                shutil.copyfileobj(upload.file, f)
            uploaded.append(filename)

    if not uploaded:
        return {"status": "error", "message": "No CSV files uploaded."}

    # Run ETL pipeline
    try:
        from etl import extract, transform, load
        from database.database import engine
        from database import models

        models.Base.metadata.create_all(bind=engine)

        extracted = extract.run()
        transformed = transform.run(extracted)
        load.run(transformed)

        from database.database import SessionLocal
        from backend.services import analytics_service
        db = SessionLocal()
        try:
            summary = analytics_service.get_summary(db)
        finally:
            db.close()

        return {
            "status": "success",
            "uploaded": uploaded,
            "summary": {
                "books":        summary["total_books"],
                "borrowers":    summary["total_borrowers"],
                "transactions": summary["total_transactions"],
                "overdue":      summary["overdue_count"],
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
