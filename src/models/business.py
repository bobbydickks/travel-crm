"""
Модели для организаций, клиентов и заявок
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class OrganizationType(enum.Enum):
    TRAVEL_AGENCY = "travel_agency"
    TOUR_OPERATOR = "tour_operator" 
    HOTEL = "hotel"
    AIRLINE = "airline"
    OTHER = "other"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(Enum(OrganizationType), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=True)
    tax_number = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    clients = relationship("Client", back_populates="organization")
    applications = relationship("Application", back_populates="organization")
    users = relationship("User", back_populates="organization")


class ClientStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    VIP = "vip"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Персональная информация
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # Документы
    passport_number = Column(String(20), nullable=True)
    passport_issued_date = Column(DateTime, nullable=True)
    passport_expires_date = Column(DateTime, nullable=True)
    
    # Статус и метаданные
    status = Column(Enum(ClientStatus), default=ClientStatus.ACTIVE, nullable=False)
    notes = Column(Text, nullable=True)
    preferences = Column(Text, nullable=True)  # JSON строка с предпочтениями
    
    # Служебные поля
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    organization = relationship("Organization", back_populates="clients")
    creator = relationship("User", foreign_keys=[created_by])
    applications = relationship("Application", back_populates="client")


class ApplicationStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ApplicationType(enum.Enum):
    TOUR_PACKAGE = "tour_package"
    FLIGHT = "flight"
    HOTEL = "hotel"
    TRANSFER = "transfer"
    EXCURSION = "excursion"
    INSURANCE = "insurance"
    VISA = "visa"
    OTHER = "other"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Основная информация
    application_number = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(Enum(ApplicationType), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT, nullable=False)
    
    # Детали заявки
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    destination = Column(String(255), nullable=True)
    departure_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)
    adults_count = Column(Integer, default=1, nullable=False)
    children_count = Column(Integer, default=0, nullable=False)
    
    # Финансовая информация
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    final_cost = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="RUB", nullable=False)
    
    # Дополнительная информация
    special_requirements = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Заметки для внутреннего использования
    
    # Служебные поля
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Ответственный менеджер
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    organization = relationship("Organization", back_populates="applications")
    client = relationship("Client", back_populates="applications")
    assigned_manager = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
