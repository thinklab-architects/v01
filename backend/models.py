from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(String, unique=True, nullable=False)
    rule_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
