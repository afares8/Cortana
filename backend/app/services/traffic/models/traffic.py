from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

class TrafficSubmission(Base):
    """Model for tracking DMCE submissions."""
    __tablename__ = "traffic_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    submission_date = Column(DateTime, default=datetime.utcnow)
    movement_type = Column(String, index=True)  # "Exit" or "Transfer"
    client_name = Column(String, index=True)
    client_id = Column(String, index=True)
    total_value = Column(Float)
    total_weight = Column(Float)
    total_items = Column(Integer)
    dmce_number = Column(String, nullable=True)  # Will be null until successful submission
    status = Column(String)  # "Pending", "Submitted", "Failed"
    error_message = Column(Text, nullable=True)
    is_consolidated = Column(Boolean, default=False)
    original_invoice_ids = Column(JSON, nullable=True)  # Store IDs of original invoices if consolidated
    
    user = relationship("User", back_populates="traffic_submissions")
    
    invoice_records = relationship("InvoiceRecord", back_populates="submission")

class InvoiceRecord(Base):
    """Model for invoice records uploaded to the system."""
    __tablename__ = "traffic_invoice_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    submission_id = Column(Integer, ForeignKey("traffic_submissions.id"), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    invoice_number = Column(String, index=True)
    invoice_date = Column(DateTime)
    client_name = Column(String, index=True)
    client_id = Column(String, index=True)
    movement_type = Column(String, index=True)  # "Exit" or "Transfer"
    total_value = Column(Float)
    total_weight = Column(Float)
    status = Column(String)  # "Validated", "Error", "Consolidated", "Submitted"
    validation_errors = Column(JSON, nullable=True)
    ai_suggestions = Column(JSON, nullable=True)
    is_consolidated = Column(Boolean, default=False)
    consolidated_into_id = Column(Integer, nullable=True)  # ID of the consolidated record this was merged into
    
    user = relationship("User", back_populates="invoice_records")
    
    submission = relationship("TrafficSubmission", back_populates="invoice_records")
    
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    """Model for individual items in an invoice."""
    __tablename__ = "traffic_invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("traffic_invoice_records.id"))
    tariff_code = Column(String)
    description = Column(Text)
    quantity = Column(Float)
    unit = Column(String)
    weight = Column(Float)
    value = Column(Float)
    volume = Column(Float, nullable=True)
    
    invoice = relationship("InvoiceRecord", back_populates="items")
