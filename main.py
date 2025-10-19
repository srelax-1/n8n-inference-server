"""Main FastAPI application for n8n inference server."""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Global model and tokenizer storage
model = None
tokenizer = None


class InferenceRequest(BaseModel):
    """Request model for inference endpoint."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt for generation")
    max_length: Optional[int] = Field(None, ge=1, le=500, description="Maximum length of generated text")
    temperature: Optional[float] = Field(None, ge=0.1, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    num_return_sequences: Optional[int] = Field(1, ge=1, le=5, description="Number of sequences to generate")
    
    @validator('prompt')
    def prompt_not_empty(cls, v):
        """Validate that prompt is not just whitespace."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v


class InferenceResponse(BaseModel):
    """Response model for inference endpoint."""
    generated_text: List[str] = Field(..., description="Generated text sequences")
    prompt: str = Field(..., description="Original prompt")
    model: str = Field(..., description="Model used for generation")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the model is loaded")
    model_name: str = Field(..., description="Name of the loaded model")


@app.on_event("startup")
async def startup_event():
    """Load model and tokenizer on startup."""
    global model, tokenizer
    try:
        logger.info(f"Loading model: {settings.model_name}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            settings.model_name,
            cache_dir=settings.model_cache_dir
        )
        
        # Set pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            settings.model_name,
            cache_dir=settings.model_cache_dir,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        if not torch.cuda.is_available():
            model = model.to("cpu")
        
        model.eval()
        logger.info("Model loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global model, tokenizer
    logger.info("Shutting down inference server")
    model = None
    tokenizer = None


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        HealthResponse: Service status information
    """
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None and tokenizer is not None,
        model_name=settings.model_name
    )


@app.post("/inference", response_model=InferenceResponse, status_code=status.HTTP_200_OK)
async def generate_text(request: InferenceRequest):
    """
    Generate text based on the provided prompt.
    
    Args:
        request: InferenceRequest containing the prompt and generation parameters
        
    Returns:
        InferenceResponse: Generated text and metadata
        
    Raises:
        HTTPException: If model is not loaded or generation fails
    """
    global model, tokenizer
    
    # Check if model is loaded
    if model is None or tokenizer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please wait for model initialization."
        )
    
    try:
        # Get generation parameters with defaults
        max_length = request.max_length or settings.max_length
        temperature = request.temperature or settings.temperature
        top_p = request.top_p or settings.top_p
        
        logger.info(f"Generating text for prompt: {request.prompt[:50]}...")
        
        # Tokenize input
        inputs = tokenizer(
            request.prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Move to same device as model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=request.num_return_sequences,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode outputs
        generated_texts = [
            tokenizer.decode(output, skip_special_tokens=True)
            for output in outputs
        ]
        
        logger.info(f"Successfully generated {len(generated_texts)} sequences")
        
        return InferenceResponse(
            generated_text=generated_texts,
            prompt=request.prompt,
            model=settings.model_name
        )
        
    except Exception as e:
        logger.error(f"Error during text generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False
    )
