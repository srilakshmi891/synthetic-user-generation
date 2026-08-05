from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ValidationIssue(BaseModel):
    category: Literal[
        "AGE_OCCUPATION_MISMATCH",
        "SKILL_EDUCATION_MISMATCH",
        "UNREALISTIC_INCOME",
        "MISSING_REQUIRED_FIELD",
        "CONTRADICTION",
        "SCHEMA_FORMAT_ERROR",
        "COHORT_UNIQUENESS"
    ] = Field(..., description="Category of the validation issue.")
    severity: Literal["ERROR", "WARNING"] = Field(..., description="Error blocks adoption; Warning flags potential inconsistency.")
    field_path: str = Field(..., description="JSON field path (e.g. 'demographics.age', 'occupation.job_title').", example="demographics.age")
    message: str = Field(..., description="Detailed explanation of why the validation failed.")
    suggested_fix: Optional[str] = Field(None, description="Suggested correction or adjustment.")

class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="True if no ERROR severity issues were found.")
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Overall consistency score out of 100.")
    errors: List[ValidationIssue] = Field(default_factory=list, description="List of blocking errors.")
    warnings: List[ValidationIssue] = Field(default_factory=list, description="List of non-blocking warnings.")
