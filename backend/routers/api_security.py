from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import httpx
import asyncio
import json
import time

from database import get_db, APISecurityTest
from modules.api_security import APISecurityTester

router = APIRouter()


class APITestRequest(BaseModel):
    endpoint: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    test_types: List[str] = ["contract", "fuzzing", "rate_limit"]
    contract_schema: Optional[Dict[str, Any]] = None
    rate_limit_threshold: Optional[int] = 100


class APITestResponse(BaseModel):
    test_id: int
    endpoint: str
    method: str
    status: str
    results: Dict[str, Any]
    created_at: str


@router.post("/api-security/test", response_model=APITestResponse)
async def test_api_security(
    request: APITestRequest,
    db: Session = Depends(get_db)
):
    try:
        tester = APISecurityTester()
        results = await tester.run_tests(
            endpoint=request.endpoint,
            method=request.method,
            headers=request.headers or {},
            body=request.body,
            test_types=request.test_types,
            contract_schema=request.contract_schema,
            rate_limit_threshold=request.rate_limit_threshold
        )
        
        overall_status = "passed" if all(r.get("passed", False) for r in results.values()) else "failed"
        
        db_test = APISecurityTest(
            endpoint=request.endpoint,
            method=request.method,
            test_type=",".join(request.test_types),
            status=overall_status,
            results=results
        )
        db.add(db_test)
        db.commit()
        db.refresh(db_test)
        
        return APITestResponse(
            test_id=db_test.id,
            endpoint=db_test.endpoint,
            method=db_test.method,
            status=db_test.status,
            results=db_test.results,
            created_at=db_test.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API security test failed: {str(e)}")


@router.get("/api-security/tests")
async def list_tests(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    tests = db.query(APISecurityTest).offset(offset).limit(limit).all()
    return {
        "tests": [
            {
                "id": test.id,
                "endpoint": test.endpoint,
                "method": test.method,
                "status": test.status,
                "created_at": test.created_at.isoformat()
            }
            for test in tests
        ],
        "total": db.query(APISecurityTest).count()
    }


@router.get("/api-security/tests/{test_id}")
async def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(APISecurityTest).filter(APISecurityTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return {
        "id": test.id,
        "endpoint": test.endpoint,
        "method": test.method,
        "test_type": test.test_type,
        "status": test.status,
        "results": test.results,
        "created_at": test.created_at.isoformat()
    }


