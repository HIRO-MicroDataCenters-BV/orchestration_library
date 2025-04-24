from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, crud

router = APIRouter(prefix="/workload_request_decision")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create(data: schemas.WorkloadRequestDecisionCreate, db: Session = Depends(get_db)):
    return crud.create_workload_request_decision(db, data)

