import re
from typing import List, Optional
from app.models.persona import ComprehensivePersona
from app.validation.models import ValidationResult, ValidationIssue
from app.core.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class SemanticAuditResult(BaseModel):
    has_contradictions: bool = Field(..., description="True if logical self-contradictions are found.")
    issues: List[ValidationIssue] = Field(default_factory=list, description="Detailed list of contradiction issues.")

class PersonaValidator:
    """
    Comprehensive Persona Validation Engine.
    Combines fast deterministic rule-based validation with LLM semantic consistency auditing.
    """
    
    SENIOR_TITLES = ["senior", "lead", "principal", "director", "vp", "vice president", "head of", "chief", "cto", "ceo", "cpo"]
    EXECUTIVE_TITLES = ["director", "vp", "vice president", "head of", "chief", "cto", "ceo", "cpo", "founder"]
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm_provider = llm_provider

    def validate_deterministic(self, persona: ComprehensivePersona) -> List[ValidationIssue]:
        """
        Runs deterministic rule-based validation checks.
        """
        issues: List[ValidationIssue] = []

        # 1. Required Fields & Non-Empty Checks
        if not persona.basic_info.full_name or persona.basic_info.full_name.strip() == "":
            issues.append(ValidationIssue(
                category="MISSING_REQUIRED_FIELD",
                severity="ERROR",
                field_path="basic_info.full_name",
                message="Persona full_name is required and cannot be empty."
            ))

        if not persona.quote or persona.quote.strip() == "":
            issues.append(ValidationIssue(
                category="MISSING_REQUIRED_FIELD",
                severity="ERROR",
                field_path="quote",
                message="Persona quote is required and cannot be empty."
            ))

        if not persona.goals.primary_goals or len(persona.goals.primary_goals) == 0:
            issues.append(ValidationIssue(
                category="MISSING_REQUIRED_FIELD",
                severity="ERROR",
                field_path="goals.primary_goals",
                message="At least one primary goal must be specified."
            ))

        if not persona.challenges.pain_points or len(persona.challenges.pain_points) == 0:
            issues.append(ValidationIssue(
                category="MISSING_REQUIRED_FIELD",
                severity="ERROR",
                field_path="challenges.pain_points",
                message="At least one pain point must be specified."
            ))

        # 2. Age vs Occupation Checks
        age = persona.demographics.age
        job_title_lower = persona.occupation.job_title.lower()

        if age < 18 and any(title in job_title_lower for title in self.SENIOR_TITLES + ["manager", "engineer", "consultant"]):
            issues.append(ValidationIssue(
                category="AGE_OCCUPATION_MISMATCH",
                severity="ERROR",
                field_path="demographics.age",
                message=f"Persona age ({age}) is under 18 but holds a professional title ('{persona.occupation.job_title}').",
                suggested_fix="Adjust age to 22+ or modify job title to student/intern."
            ))

        if age < 24 and any(title in job_title_lower for title in self.EXECUTIVE_TITLES):
            issues.append(ValidationIssue(
                category="AGE_OCCUPATION_MISMATCH",
                severity="ERROR",
                field_path="demographics.age",
                message=f"Persona age ({age}) is unrealistically young for an executive role ('{persona.occupation.job_title}').",
                suggested_fix="Increase age to 30+ or adjust job title to junior/mid-level."
            ))

        # 3. Skills vs Education Alignment Checks
        degree_lower = persona.education.degree_level.lower()
        if "high school" in degree_lower or "secondary" in degree_lower:
            if persona.technical_skills.overall_proficiency.lower() in ["expert", "master"] and not any(
                term in persona.basic_info.bio.lower() for term in ["self-taught", "prodigy", "bootcamp", "hacker"]
            ):
                issues.append(ValidationIssue(
                    category="SKILL_EDUCATION_MISMATCH",
                    severity="WARNING",
                    field_path="technical_skills.overall_proficiency",
                    message="High school education with 'Expert' tech proficiency without explicit self-taught/bootcamp context in bio.",
                    suggested_fix="Add self-taught background context to bio or adjust proficiency level."
                ))

        # 4. Income Realism Checks
        income_str = persona.demographics.household_income.lower()
        # Parse numeric digits from income string if present
        income_numbers = [int(n) for n in re.findall(r'\b\d+\b', income_str.replace(',', ''))]
        if income_numbers:
            avg_income = sum(income_numbers) / len(income_numbers)
            
            # Check for student/intern claiming exorbitant income
            if ("student" in job_title_lower or "intern" in job_title_lower) and avg_income > 150000:
                issues.append(ValidationIssue(
                    category="UNREALISTIC_INCOME",
                    severity="WARNING",
                    field_path="demographics.household_income",
                    message=f"Job title '{persona.occupation.job_title}' usually does not command income tier '{persona.demographics.household_income}'.",
                    suggested_fix="Clarify if household income includes family support or lower income tier."
                ))

            # Executive claiming sub-minimum wage income
            if any(title in job_title_lower for title in self.EXECUTIVE_TITLES) and avg_income < 20000 and "usd" in income_str:
                issues.append(ValidationIssue(
                    category="UNREALISTIC_INCOME",
                    severity="ERROR",
                    field_path="demographics.household_income",
                    message=f"Executive role '{persona.occupation.job_title}' has unrealistically low reported income ('{persona.demographics.household_income}').",
                    suggested_fix="Update income tier to match executive industry benchmarks."
                ))

        return issues

    async def audit_semantic_consistency(self, persona: ComprehensivePersona) -> List[ValidationIssue]:
        """
        Uses LLM with structured output to detect subtle logical self-contradictions across fields.
        """
        if not self.llm_provider:
            return []

        try:
            llm = get_llm(provider=self.llm_provider)
            structured_llm = llm.with_structured_output(SemanticAuditResult)

            prompt = ChatPromptTemplate.from_messages([
                ("system", 
                 "You are an expert QA Auditor for Synthetic User Research. "
                 "Inspect the persona JSON for subtle self-contradictions across age, job, devices, personality, and quote. "
                 "For example: 'Claims tech-savviness is Expert but uses zero smart devices', 'Claims remote worker but has 2-hour subway commute', 'Quote contradicts key frustrations'."),
                ("human", "Audit this persona payload for logical self-contradictions:\n\n{persona_json}")
            ])

            chain = prompt | structured_llm
            result: SemanticAuditResult = await chain.ainvoke({
                "persona_json": persona.model_dump_json(indent=2)
            })

            return result.issues
        except Exception:
            # Fallback gracefully if LLM semantic audit fails or network is unavailable
            return []

    def validate_cohort_uniqueness(self, personas: List[ComprehensivePersona]) -> List[ValidationIssue]:
        """
        Ensures persona_id and full_name values are unique across a generated cohort.
        """
        issues: List[ValidationIssue] = []
        seen_ids = {}
        seen_names = {}

        for index, persona in enumerate(personas):
            persona_id = (persona.basic_info.persona_id or "").strip().lower()
            full_name = (persona.basic_info.full_name or "").strip().lower()

            if persona_id:
                if persona_id in seen_ids:
                    issues.append(ValidationIssue(
                        category="COHORT_UNIQUENESS",
                        severity="ERROR",
                        field_path=f"personas[{index}].basic_info.persona_id",
                        message=f"Duplicate persona_id '{persona.basic_info.persona_id}' also used by personas[{seen_ids[persona_id]}].",
                        suggested_fix="Assign a unique persona_id to each persona in the cohort."
                    ))
                else:
                    seen_ids[persona_id] = index

            if full_name:
                if full_name in seen_names:
                    issues.append(ValidationIssue(
                        category="COHORT_UNIQUENESS",
                        severity="ERROR",
                        field_path=f"personas[{index}].basic_info.full_name",
                        message=f"Duplicate full_name '{persona.basic_info.full_name}' also used by personas[{seen_names[full_name]}].",
                        suggested_fix="Assign a unique full_name to each persona in the cohort."
                    ))
                else:
                    seen_names[full_name] = index

        return issues

    def _build_validation_result(self, issues: List[ValidationIssue]) -> ValidationResult:
        errors = [i for i in issues if i.severity == "ERROR"]
        warnings = [i for i in issues if i.severity == "WARNING"]
        is_valid = len(errors) == 0
        quality_score = max(0.0, 100.0 - (len(errors) * 25.0 + len(warnings) * 10.0))
        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )

    async def validate(self, persona: ComprehensivePersona, include_semantic_audit: bool = True) -> ValidationResult:
        """
        Executes full validation suite (deterministic + optional semantic audit) and returns ValidationResult.
        """
        issues = self.validate_deterministic(persona)

        if include_semantic_audit and self.llm_provider:
            semantic_issues = await self.audit_semantic_consistency(persona)
            issues.extend(semantic_issues)

        return self._build_validation_result(issues)

    async def validate_personas(
        self,
        personas: List[ComprehensivePersona],
        include_semantic_audit: bool = True
    ) -> ValidationResult:
        """
        Validates a list of personas and aggregates issues, including cohort uniqueness checks.
        """
        if not personas:
            return ValidationResult(
                is_valid=False,
                quality_score=0.0,
                errors=[ValidationIssue(
                    category="MISSING_REQUIRED_FIELD",
                    severity="ERROR",
                    field_path="personas",
                    message="At least one persona is required.",
                    suggested_fix="Generate one or more ComprehensivePersona objects."
                )],
                warnings=[]
            )

        issues: List[ValidationIssue] = []
        for index, persona in enumerate(personas):
            persona_issues = self.validate_deterministic(persona)
            for issue in persona_issues:
                issues.append(issue.model_copy(
                    update={"field_path": f"personas[{index}].{issue.field_path}"}
                ))

            if include_semantic_audit and self.llm_provider:
                semantic_issues = await self.audit_semantic_consistency(persona)
                for issue in semantic_issues:
                    issues.append(issue.model_copy(
                        update={"field_path": f"personas[{index}].{issue.field_path}"}
                    ))

        issues.extend(self.validate_cohort_uniqueness(personas))
        return self._build_validation_result(issues)
