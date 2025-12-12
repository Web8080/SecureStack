from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class API SecurityTest(Base):
    __tablename__ = "api_security_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    test_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    framework = Column(String, nullable=False)
    policy_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    details = Column(JSON)
    evidence = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class DependencyScan(Base):
    __tablename__ = "dependency_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    risk_score = Column(Float)
    vulnerabilities = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class SBOMDocument(Base):
    __tablename__ = "sbom_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    format = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    attestation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


