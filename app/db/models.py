import enum
import uuid
from typing import List, Optional, Any, Dict
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base, UUIDMixin, TimestampMixin

class SessionStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ResearchSession(Base, UUIDMixin, TimestampMixin):
    """
    Represents a Synthetic User Research Session containing input parameters and target goals.
    """
    __tablename__ = "research_sessions"

    # Core Research Parameters
    product_description: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    research_objective: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Session Configuration
    requested_persona_count: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="gemini", nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[SessionStatusEnum] = mapped_column(
        SQLEnum(SessionStatusEnum),
        default=SessionStatusEnum.PENDING,
        nullable=False,
        index=True
    )
    
    # Metadata & Error Tracking
    cohort_diversity_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    personas: Mapped[List["Persona"]] = relationship(
        "Persona",
        back_populates="research_session",
        cascade="all, delete-orphan"
    )
    generated_responses: Mapped[List["GeneratedResponse"]] = relationship(
        "GeneratedResponse",
        back_populates="research_session",
        cascade="all, delete-orphan"
    )


class Persona(Base, UUIDMixin, TimestampMixin):
    """
    Represents an individual synthetic user persona generated within a research session.
    """
    __tablename__ = "personas"

    # Foreign Keys
    research_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Quick Lookup Indexable Fields
    persona_id_slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    archetype_title: Mapped[str] = mapped_column(String(200), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)
    occupation: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    quote: Mapped[str] = mapped_column(Text, nullable=False)

    # Complete Structured Persona Payload (PostgreSQL JSONB)
    full_persona_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Overall Quality & Validation Status Summary
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    overall_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    research_session: Mapped["ResearchSession"] = relationship(
        "ResearchSession",
        back_populates="personas"
    )
    validation_statuses: Mapped[List["ValidationStatus"]] = relationship(
        "ValidationStatus",
        back_populates="persona",
        cascade="all, delete-orphan"
    )
    generated_responses: Mapped[List["GeneratedResponse"]] = relationship(
        "GeneratedResponse",
        back_populates="persona",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_persona_session_archetype", "research_session_id", "archetype_title"),
    )


class ValidationStatus(Base, UUIDMixin, TimestampMixin):
    """
    Tracks detailed validation results, rule checks, and quality scores for a synthetic persona.
    """
    __tablename__ = "validation_statuses"

    # Foreign Keys
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Validation Results
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Detailed Errors & Warnings Payload (JSONB)
    errors_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    warnings_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    
    # Audit Metadata
    validator_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)

    # Relationships
    persona: Mapped["Persona"] = relationship(
        "Persona",
        back_populates="validation_statuses"
    )


class GeneratedResponse(Base, UUIDMixin, TimestampMixin):
    """
    Stores synthetic user interview responses, survey answers, or usability task feedback
    simulated by a persona during user research testing.
    """
    __tablename__ = "generated_responses"

    # Foreign Keys
    research_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Synthetic Interview / Survey Content
    prompt_question: Mapped[str] = mapped_column(Text, nullable=False)
    simulated_response: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Sentiment & Analytical Metrics
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Positive, Negative, Neutral, Skeptical
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # -1.0 to +1.0
    perceived_friction_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Low, Medium, High
    
    # Raw Metadata Payload (Tokens, Model used, latency)
    execution_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    research_session: Mapped["ResearchSession"] = relationship(
        "ResearchSession",
        back_populates="generated_responses"
    )
    persona: Mapped["Persona"] = relationship(
        "Persona",
        back_populates="generated_responses"
    )

    __table_args__ = (
        Index("idx_responses_session_persona", "research_session_id", "persona_id"),
    )
