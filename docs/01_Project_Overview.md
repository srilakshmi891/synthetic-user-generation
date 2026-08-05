# 01. Project Overview

## 1. Executive Summary

The **AI-Powered Synthetic User Research Platform** automates the synthesis, validation, and persistence of multi-dimensional synthetic user personas. Product management and UX research teams use this platform to conduct qualitative user discovery, simulate usability friction, and evaluate value propositions without spending weeks recruiting human candidates.

## 2. Problem Statement

Product discovery for software products (especially those targeting technical demographics like **aspiring software engineers**) encounters severe operational bottlenecks:
- **Recruitment Friction & Cost**: Scheduling qualitative interviews with diverse candidate pools takes weeks and requires high financial incentives.
- **Sampling Bias & Homogeneity**: User research frequently over-indexes on privileged urban candidates while neglecting Tier-2/Tier-3 city developers and self-taught bootcamp candidates.
- **Superficial LLM Personas**: Naive LLM prompts yield generic caricatures (e.g. assuming every candidate is an elite CS student grinding 10 hours of LeetCode a day).
- **Logical Self-Contradictions**: Unconstrained generation yields field inconsistencies (e.g. claiming an age of 16 holding a Vice President title).

## 3. The Solution

The **Persona Generation Subsystem** combines:
1. **LangGraph State Machines**: Autonomous 6-node graphs with self-correction retry loops.
2. **Pydantic Type Enforcement**: Structured JSON schema validation using `with_structured_output`.
3. **Anti-Stereotype Prompt Directives**: Prompts explicitly enforcing college tier, economic, and regional diversity.
4. **Hybrid Persona Validation Engine**: Rule-based age/seniority and income checks combined with LLM semantic auditing.
5. **PostgreSQL Relational Storage**: Native `JSONB` columns paired with relational UUID session tracking.
