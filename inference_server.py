from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch

# ---------------------------
# Request and Response Models
# ---------------------------
class ClassificationRequest(BaseModel):
    subject: str
    body: str
    labels: dict[str, str]  # {label: description}
    ticket_id: int | None = None
    reference_id: int | None = None



class ClassificationResponse(BaseModel):
    text: str
    best_label: str
    confidence: float
    labels: list[str]
    scores: list[float]
    ticket_id: int | None = None
    reference_id: int | None = None


# ---------------------------
# App Initialization
# ---------------------------
app = FastAPI(
    title="Local Classifier API using Hugging Face Model",
    description="A lightweight local Zero-shot text classifier that uses subject + body and label descriptions with Hugging Face transformers.",
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
    """Classify input subject + body using descriptive labels."""
    if not req.subject.strip() and not req.body.strip():
        raise HTTPException(status_code=400, detail="Either subject or body is required.")
    if not req.labels:
        raise HTTPException(status_code=400, detail="At least one label with description is required.")

    # Combine subject and body for better understanding
    full_text = f"Subject: {req.subject}\n\nBody: {req.body}"

    # Convert labels dict into descriptive list
    descriptive_labels = [f"{label}: {desc}" for label, desc in req.labels.items()]

    # Run classification
    result = classifier(full_text, descriptive_labels)

    # Map back best label (without description)
    best_label_full = result["labels"][0]
    best_label = best_label_full.split(":")[0]

    return ClassificationResponse(
        text=full_text,
        labels=result["labels"],
        scores=result["scores"],
        best_label=best_label,
        confidence=result["scores"][0],
        ticket_id=req.ticket_id,
        reference_id=req.reference_id,
    )


@app.get("/status")
def status():
    return {"status": "ok", "message": "Classifier API is running."}