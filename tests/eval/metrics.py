import os
if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError
        try:
            google.auth.default()
        except DefaultCredentialsError:
            from google.auth.credentials import Credentials
            class DummyCredentials(Credentials):
                def __init__(self):
                    super().__init__()
                    self.token = "dummy-token"
                def refresh(self, request):
                    self.token = "dummy-token"
            google.auth.default = lambda *args, **kwargs: (DummyCredentials(), "dummy-project-id")
    except Exception:
        pass

    try:
        import google.cloud.storage as gcs
        from unittest.mock import MagicMock
        gcs.Client = lambda *args, **kwargs: MagicMock()
    except Exception:
        pass

from google import genai
from google.genai import types
from pydantic import BaseModel


class _Verdict(BaseModel):
    score: int  # 1-5
    explanation: str


def evaluate(instance):
    reference = instance.get("reference")
    rubric = (
        "Grade the agent's final response on a 1-5 scale (1 poor, 5 excellent) for "
        "accuracy, relevance, and clarity."
    )
    if reference:
        rubric += (
            " The response should agree with the expected answer below; penalize "
            "factual disagreement with it."
        )
    prompt = (
        f"You are an expert QA evaluator for an enterprise AI assistant. {rubric}\n"
        f"User Prompt: {instance.get('prompt', '')}\n"
        f"Final Response: {instance.get('response', '')}\n"
    )
    if reference:
        prompt += f"Expected Answer (ground truth): {reference}\n"
    prompt += f"Full Agent Trace: {instance.get('agent_data', '')}\n"

    if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

    client = genai.Client()  # AI Studio (GEMINI_API_KEY) or Vertex (ADC)
    response = client.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,  # deterministic grading
            response_mime_type="application/json",
            response_schema=_Verdict,  # guaranteed schema-valid JSON
        ),
    )
    verdict = response.parsed
    if verdict is None:  # model returned nothing usable
        return {"score": 0, "explanation": response.text or ""}
    return {"score": max(1, min(5, verdict.score)), "explanation": verdict.explanation}
