from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch

# ---------------------------
# Request and Response Models
# ---------------------------
class ClassificationRequest(BaseModel):
    text: str
    labels: list[str]


class ClassificationResponse(BaseModel):
    text: str
    best_label: str
    confidence: float
    labels: list[str]
    scores: list[float]


# ---------------------------
# App Initialization
# ---------------------------
app = FastAPI(
    title="Local Hugging Face Classifier API",
    description="A lightweight local API for zero-shot text classification using Hugging Face transformers.",
    version="1.0.0"
)


@app.on_event("startup")
def load_model():
    """Load the model once when the app starts."""
    global classifier
    device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=device
    )


# ---------------------------
# Routes
# ---------------------------
@app.post("/classify", response_model=ClassificationResponse)
async def classify(req: ClassificationRequest):
    """Classify input text into one of the provided labels."""
    if not req.text.strip() or not req.labels:
        raise HTTPException(status_code=400, detail="Both text and labels are required.")

    result = classifier(req.text, req.labels)

    return ClassificationResponse(
        text=req.text,
        labels=result["labels"],
        scores=result["scores"],
        best_label=result["labels"][0],
        confidence=result["scores"][0],
    )


@app.get("/")
def root():
    return {"status": "ok", "message": "Classifier API is running."}
