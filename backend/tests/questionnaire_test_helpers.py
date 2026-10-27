"""Reusable setup for the required non-scoring questionnaire entry steps."""


def complete_questionnaire_entry_steps(client, session_id: str) -> None:
    for step_id, answer_id in (("loan_type", "shahab"), ("entity_type", "person")):
        response = client.put(
            f"/api/v1/questionnaire/sessions/{session_id}/flow-answers/{step_id}",
            json={"answerId": answer_id},
        )
        if response.status_code != 200:
            raise AssertionError(f"entry step {step_id} failed: {response.status_code}")
