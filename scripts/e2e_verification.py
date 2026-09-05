import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["PYTHONUNBUFFERED"] = "1"
sys.path.insert(0, os.path.abspath("."))

_old_print = print
def print(*args, **kwargs):
    kwargs["flush"] = True
    _old_print(*args, **kwargs)

import json

from typing import List, Dict, Any
from fastapi.testclient import TestClient
from app.main import app
from app.models.persona import ComprehensivePersona
from app.memory.json_memory import JSONPersonaMemory, memory_service


def run_e2e_verification():
    print("=================================================================")
    print("  MILESTONE 3: COMPREHENSIVE END-TO-END VERIFICATION & DEMO")
    print("=================================================================\n")

    client = TestClient(app)

    # -------------------------------------------------------------------
    # STEP 2 — VERIFY BACKEND & API ROUTES ON FASTAPI
    # -------------------------------------------------------------------
    print("[STEP 2] Verifying FastAPI Server & Endpoint Availability...")
    health_res = client.get("/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.status_code}"
    print(f"  ✓ Health Status 200: {health_res.json()}")

    openapi_res = client.get("/openapi.json")
    assert openapi_res.status_code == 200
    paths = openapi_res.json().get("paths", {})

    target_routes = [
        "/api/v1/interviews/start",
        "/api/v1/interviews/{interview_id}/message",
        "/api/v1/interviews/{interview_id}",
        "/api/v1/insights/extract",
        "/api/v1/insights/scoring"
    ]

    for route in target_routes:
        assert route in paths, f"Route {route} missing from OpenAPI spec"
        print(f"  ✓ Route registered: {route}")

    print("✓ STEP 2 Passed: Server online & all Milestone 3 routes verified in OpenAPI schema.\n")

    # -------------------------------------------------------------------
    # STEP 4 — GENERATE SYNTHETIC PERSONAS FOR "ONLINE FOOD DELIVERY APP"
    # -------------------------------------------------------------------
    print("[STEP 4] Generating Synthetic Personas for 'Online Food Delivery Application'...")
    product_desc = "An online food delivery application that allows users to discover restaurants, browse menus, order food, make online payments, track deliveries, and provide ratings and reviews."
    target_aud = "College students, working professionals, families, and frequent food-delivery customers."
    research_obj = "Users want fast delivery, affordable prices, discounts, multiple payment options, and reliable order tracking."

    gen_payload = {
        "product_description": product_desc,
        "target_audience": target_aud,
        "research_objective": research_obj,
        "number_of_personas": 4,
        "provider": "mock"
    }

    gen_res = client.post("/api/v1/generate-persona", json=gen_payload)
    assert gen_res.status_code == 201, f"Generation failed: {gen_res.text}"
    raw_personas = gen_res.json().get("personas", [])
    assert len(raw_personas) >= 4, "Expected at least 4 personas"

    personas = [ComprehensivePersona(**p) for p in raw_personas]
    print(f"  ✓ Generated {len(personas)} unique synthetic personas:")
    for p in personas:
        print(f"    - {p.basic_info.full_name} ({p.occupation.job_title}): \"{p.quote}\"")

    print("✓ STEP 4 Passed: 4 distinct synthetic personas generated.\n")

    # -------------------------------------------------------------------
    # STEP 5 & 6 — TEST INTERVIEW MODE & MEMORY RETENTION
    # -------------------------------------------------------------------
    print("[STEP 5 & 6] Testing Interview Mode & Memory Retention for Persona 1...")
    p1 = personas[0]
    p1_id = p1.basic_info.persona_id or p1.basic_info.full_name.lower().replace(" ", "_")
    session_id = f"e2e_session_{p1_id}"

    # Clear existing session memory first for clean test idempotency
    memory_service.clear_memory(persona_id=p1_id, session_id=session_id)

    # Start Session Endpoint
    start_res = client.post("/api/v1/interviews/start", json={
        "persona": p1.model_dump(),
        "session_id": session_id,
        "product_context": product_desc
    })

    assert start_res.status_code == 201, f"Start session failed: {start_res.text}"
    print(f"  ✓ Session Started Endpoint HTTP 201: {start_res.json()['interview_id']}")

    test_questions = [
        "How often do you order food online?",
        "What is the most important factor when choosing a food delivery app?",
        "How important are discounts to you?",
        "What frustrates you about existing food delivery applications?",
        "Would you pay extra for faster delivery?",
        "Would you use this product? Why or why not?"
    ]

    all_responses = []
    for q in test_questions:
        msg_res = client.post(f"/api/v1/interviews/{session_id}/message", json={
            "persona": p1.model_dump(),
            "user_question": q,
            "product_context": product_desc,
            "provider": "mock"
        })
        assert msg_res.status_code == 200, f"Message failed: {msg_res.text}"
        reply = msg_res.json()["reply"]
        all_responses.append((q, reply))
        print(f"    Q: {q}")
        print(f"    A ({p1.basic_info.full_name}): {reply[:100]}...\n")

    # Verify Memory Retrieval Endpoint
    get_sess_res = client.get(f"/api/v1/interviews/{session_id}?persona_id={p1_id}")
    assert get_sess_res.status_code == 200, f"Get session failed: {get_sess_res.text}"
    msgs = get_sess_res.json()["messages"]
    assert len(msgs) == len(test_questions) * 2, f"Expected {len(test_questions)*2} messages in session memory, got {len(msgs)}"
    print(f"  ✓ GET /api/v1/interviews/{session_id} HTTP 200: {len(msgs)} messages retrieved.")

    # Verify Disk File Persistence (JSONPersonaMemory)
    disk_memory_path = memory_service._get_file_path(persona_id=p1_id, session_id=session_id)
    assert os.path.exists(disk_memory_path), f"Memory file should exist at {disk_memory_path}"
    with open(disk_memory_path, "r", encoding="utf-8") as f:
        disk_data = json.load(f)
    assert len(disk_data) == len(test_questions) * 2
    print(f"  ✓ JSONPersonaMemory disk persistence verified at: {disk_memory_path}")

    print("✓ STEP 5 & 6 Passed: Multi-turn interview execution and memory persistence verified.\n")

    # -------------------------------------------------------------------
    # STEP 7 — TEST MULTIPLE PERSONAS
    # -------------------------------------------------------------------
    print("[STEP 7] Conducting Interviews Across All 4 Personas...")
    transcripts_list = []
    for persona in personas:
        pid = persona.basic_info.persona_id or persona.basic_info.full_name.lower().replace(" ", "_")
        s_id = f"e2e_session_{pid}"
        memory_service.clear_memory(persona_id=pid, session_id=s_id)

        for q in test_questions[:3]:

            client.post(f"/api/v1/interviews/{s_id}/message", json={
                "persona": persona.model_dump(),
                "user_question": q,
                "product_context": product_desc,
                "provider": "mock"
            })

        history_data = memory_service.get_history(persona_id=pid, session_id=s_id, limit=50)
        transcripts_list.append({
            "persona_id": pid,
            "persona_name": persona.basic_info.full_name,
            "messages": history_data
        })
        print(f"  ✓ Completed multi-turn interview for {persona.basic_info.full_name} ({len(history_data)} turns in memory)")

    print("✓ STEP 7 Passed: Multiple persona interviews conducted & collected.\n")

    # -------------------------------------------------------------------
    # STEP 8 — EXTRACT RESEARCH INSIGHTS (POST /api/v1/insights/extract)
    # -------------------------------------------------------------------
    print("[STEP 8] Extracting Qualitative Research Insights...")
    extract_res = client.post("/api/v1/insights/extract", json={
        "personas": [p.model_dump() for p in personas],
        "interview_transcripts": transcripts_list,
        "product_context": product_desc,
        "provider": "mock"
    })
    assert extract_res.status_code == 200, f"Extract failed: {extract_res.text}"
    insights_data = extract_res.json()

    print(f"  ✓ HTTP 200 Response Received.")
    print(f"  ✓ Executive Summary: {insights_data['summary'][:120]}...")
    print(f"  ✓ Recurring Themes ({len(insights_data['recurring_themes'])}):")
    for t in insights_data['recurring_themes']:
        print(f"    - '{t['theme']}' ({t['percentage']}% of cohort): {t['description']}")

    sent = insights_data['sentiment']
    print(f"  ✓ Sentiment Distribution: Positive {sent['positive']}%, Neutral {sent['neutral']}%, Negative {sent['negative']}%")
    print(f"  ✓ Agreement Patterns ({len(insights_data['agreement_patterns'])}): Majority View: '{insights_data['agreement_patterns'][0]['majority_response']}'")
    print(f"  ✓ Behavioral Trends ({len(insights_data['behavioral_trends'])}): {[b['trend'] for b in insights_data['behavioral_trends']]}")

    print("✓ STEP 8 Passed: Qualitative research insights extracted.\n")

    # -------------------------------------------------------------------
    # STEP 9 & 10 & 11 — PRODUCT USAGE SCORING & MATHEMATICAL VERIFICATION
    # -------------------------------------------------------------------
    print("[STEP 9, 10 & 11] Product Usage Scoring & Segment/Aggregate Mathematical Verification...")
    scoring_res = client.post("/api/v1/insights/scoring", json={
        "personas": [p.model_dump() for p in personas],
        "product_context": product_desc,
        "provider": "mock"
    })
    assert scoring_res.status_code == 200, f"Scoring failed: {scoring_res.text}"
    scores_data = scoring_res.json()

    persona_scores = scores_data["persona_scores"]
    print("\n--- Persona Level Scores (0-10) ---")
    sum_individual = 0.0
    for ps in persona_scores:
        sum_individual += ps["score"]
        print(f"  • {ps['persona_name']}: Score {ps['score']}/10 ({ps['decision']}) | Reason: {ps['reasoning'][:70]}...")

    expected_avg = round(sum_individual / len(persona_scores), 2)
    reported_avg = scores_data["aggregate_score"]["overall_score"]

    print("\n--- Segment Level Scores ---")
    for seg in scores_data["segment_scores"]:
        print(f"  • Segment '{seg['segment_name']}': Average Score {seg['average_score']}/10 ({seg['persona_count']} personas)")

    print("\n--- Aggregate Score Mathematical Verification ---")
    print(f"  Sum of individual scores: {sum_individual}")
    print(f"  Expected average: {expected_avg}")
    print(f"  Reported aggregate overall_score: {reported_avg}")
    assert abs(expected_avg - reported_avg) < 0.01, f"Aggregate score mismatch! Expected {expected_avg}, got {reported_avg}"
    print("  ✓ Mathematical verification PASSED: Aggregate score equals individual persona score average!")

    print("✓ STEP 9, 10 & 11 Passed: Scoring and aggregate calculations verified.\n")

    print("=================================================================")
    print("  🎉 ALL END-TO-END VERIFICATION STEPS PASSED SUCCESSFULLY!     ")
    print("=================================================================")

if __name__ == "__main__":
    run_e2e_verification()
