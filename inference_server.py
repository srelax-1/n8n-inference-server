from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch
import uvicorn
import logging
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager


load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/bart-large-mnli")

# ---------------------------
# Logging configuration
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------
# Request and Response Models
# ---------------------------
class ClassificationRequest(BaseModel):
    subject: str
    body: str
    labels: dict[str, str]
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


classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events using the new lifespan API."""
    global classifier
    try:
        device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Loading model '{MODEL_NAME}' (device={'GPU' if device == 0 else 'CPU'}) ...")
        classifier = pipeline(
            "zero-shot-classification",
            model=MODEL_NAME,
            device=device
        )
        logger.info("✅ Model loaded successfully.")
    except Exception as e:
        logger.exception("❌ Failed to load model.")
        raise RuntimeError(f"Model loading failed: {e}")

    # Startup complete
    yield

    # Shutdown
    logger.info("Shutting down n8n Inference Server...")

# ---------------------------
# App Initialization
# ---------------------------
app = FastAPI(
    title="Local Classifier API using Hugging Face Model",
    description="A lightweight local Zero-shot text classifier that uses subject + body and label descriptions with Hugging Face transformers.",
    version="1.0.0",
    lifespan=lifespan
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
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet. Please try again later.")

    # Combine subject and body for better understanding
    full_text = f"Subject: {req.subject}\n\nBody: {req.body}"

    # Convert labels dict into descriptive list
    descriptive_labels = [f"{label}: {desc}" for label, desc in req.labels.items()]

    logger.info(f"Classifying ticket (ID={req.ticket_id}, Ref={req.reference_id}) with {len(descriptive_labels)} labels.")

    # Run classification
    try:
        result = classifier(full_text, descriptive_labels)
    except Exception as e:
        logger.exception("Classification failed.")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    # Map back best label (without description)
    best_label_full = result["labels"][0]
    best_label = best_label_full.split(":")[0]

    logger.info(f"Classification complete — Best label: {best_label}, Confidence: {result['scores'][0]:.4f}")

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
    """Health check endpoint."""
    model_loaded = classifier is not None
    return {
        "status": "ok" if model_loaded else "error",
        "model_loaded": model_loaded,
        "message": "Classifier API is running." if model_loaded else "Model not loaded."
    }

# ---------------------------
# Main entry point (optional)
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("inference_server:app", host=HOST, port=PORT, reload=True)