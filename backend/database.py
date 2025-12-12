from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, Boolean, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables
user_team_association = Table(
    'user_teams',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('team_id', Integer, ForeignKey('teams.id'))
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    teams = relationship("Team", secondary=user_team_association, back_populates="members")
    api_keys = relationship("APIKey", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    members = relationship("User", secondary=user_team_association, back_populates="teams")
    owner = relationship("User", foreign_keys=[owner_id])


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_used = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="api_keys")


class APISecurityTest(Base):
    __tablename__ = "api_security_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    test_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    results = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
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
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    scheduled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DependencyScan(Base):
    __tablename__ = "dependency_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    ecosystem = Column(String, default="npm")
    risk_score = Column(Float)
    vulnerabilities = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SBOMDocument(Base):
    __tablename__ = "sbom_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    format = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    attestation = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")


class ScheduledScan(Base):
    __tablename__ = "scheduled_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    scan_type = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    config = Column(JSON)
    enabled = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)
    secret = Column(String)
    active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class ContainerScan(Base):
    __tablename__ = "container_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String, nullable=False)
    image_tag = Column(String, nullable=False)
    digest = Column(String)
    vulnerabilities = Column(JSON)
    risk_score = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class InfrastructureScan(Base):
    __tablename__ = "infrastructure_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String, nullable=False)
    target = Column(String, nullable=False)
    findings = Column(JSON)
    risk_score = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class PolicyTemplate(Base):
    __tablename__ = "policy_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    framework = Column(String, nullable=False)
    description = Column(Text)
    policy_content = Column(JSON, nullable=False)
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


