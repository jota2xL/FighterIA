"""
Module: routers.nlp
Description: NLP feedback endpoint — stateless, no DB access, no auth required.
             Prefix: /nlp | Tags: ["NLP"]
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field, ConfigDict

from app.services.nlp_service import generate_nlp_feedback

router = APIRouter(prefix="/nlp", tags=["NLP"])


class FeedbackRequest(BaseModel):
    """Input scores for NLP feedback generation. All values must be in range [0, 100]."""
    model_config = ConfigDict(from_attributes=True)

    potencia:   float = Field(..., ge=0.0, le=100.0, description="Puntuación de potencia (0-100)")
    equilibrio: float = Field(..., ge=0.0, le=100.0, description="Puntuación de equilibrio (0-100)")
    alineacion: float = Field(..., ge=0.0, le=100.0, description="Puntuación de alineación corporal (0-100)")
    velocidad:  float = Field(..., ge=0.0, le=100.0, description="Puntuación de velocidad de ejecución (0-100)")


class FeedbackResponse(BaseModel):
    """Generated NLP feedback paragraph."""
    feedback: str


@router.post("/feedback", response_model=FeedbackResponse)
def get_nlp_feedback(payload: FeedbackRequest):
    """
    Generate a personalized feedback paragraph from performance scores.
    No authentication required — stateless endpoint, no DB access.
    All scores must be floats in [0, 100]; values outside this range return HTTP 422.
    """
    scores = {
        "potencia":   payload.potencia,
        "equilibrio": payload.equilibrio,
        "alineacion": payload.alineacion,
        "velocidad":  payload.velocidad,
    }
    feedback_text = generate_nlp_feedback(scores)
    return FeedbackResponse(feedback=feedback_text)
