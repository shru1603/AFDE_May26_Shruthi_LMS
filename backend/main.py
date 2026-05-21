from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import engine
from database import models
from backend.routers import books, borrowers, transactions, analytics

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"message": "Library Management System API"}
