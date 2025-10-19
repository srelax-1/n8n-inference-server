# n8n Inference Server

A FastAPI-based inference server for text generation using transformer models. This server provides a simple REST API for running inference on language models, designed to integrate seamlessly with n8n workflows.

## Features

- 🚀 Fast and efficient text generation using Hugging Face transformers
- 🔧 Configurable via environment variables
- 📝 Comprehensive request validation with Pydantic
- 🏥 Health check endpoint for monitoring
- 🛡️ Proper error handling and logging
- 📊 Support for multiple generation parameters (temperature, top_p, etc.)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/srelax-1/n8n-inference-server.git
cd n8n-inference-server
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The server can be configured using environment variables. Create a `.env` file in the project root:

```env
# Server settings
HOST=0.0.0.0
PORT=8000

# Model settings
MODEL_NAME=gpt2
MODEL_CACHE_DIR=./cache
MAX_LENGTH=100
TEMPERATURE=0.7
TOP_P=0.9

# API settings
API_TITLE=n8n Inference Server
API_VERSION=1.0.0
API_DESCRIPTION=FastAPI-based inference server for text generation
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `MODEL_NAME` | Hugging Face model identifier | `gpt2` |
| `MODEL_CACHE_DIR` | Directory for model cache | `None` |
| `MAX_LENGTH` | Default maximum generation length | `100` |
| `TEMPERATURE` | Default sampling temperature | `0.7` |
| `TOP_P` | Default nucleus sampling parameter | `0.9` |

## Usage

### Starting the Server

Run the server using uvicorn:

```bash
python main.py
```

Or directly with uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start and load the model. You should see logs indicating successful model loading.

### API Endpoints

#### Health Check

Check if the server is running and the model is loaded.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "gpt2"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

#### Text Generation

Generate text based on a prompt.

**Endpoint:** `POST /inference`

**Request Body:**
```json
{
  "prompt": "Once upon a time",
  "max_length": 50,
  "temperature": 0.7,
  "top_p": 0.9,
  "num_return_sequences": 1
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text prompt for generation (1-1000 chars) |
| `max_length` | integer | No | Maximum length of generated text (1-500) |
| `temperature` | float | No | Sampling temperature (0.1-2.0) |
| `top_p` | float | No | Nucleus sampling parameter (0.0-1.0) |
| `num_return_sequences` | integer | No | Number of sequences to generate (1-5) |

**Response:**
```json
{
  "generated_text": [
    "Once upon a time, there was a beautiful princess who lived in a castle."
  ],
  "prompt": "Once upon a time",
  "model": "gpt2"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/inference \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The future of AI is",
    "max_length": 50,
    "temperature": 0.8
  }'
```

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The server includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **503 Service Unavailable**: Model not loaded yet
- **500 Internal Server Error**: Generation or server errors

All errors return JSON responses with a `detail` field explaining the issue.

## Model Support

The server supports any Hugging Face model compatible with `AutoModelForCausalLM`. Some recommended models:

- `gpt2` (default, lightweight)
- `gpt2-medium`
- `gpt2-large`
- `distilgpt2` (faster, smaller)
- `microsoft/DialoGPT-small`
- `EleutherAI/gpt-neo-125M`

To use a different model, set the `MODEL_NAME` environment variable.

## Development

### Project Structure

```
n8n-inference-server/
├── main.py              # FastAPI application and endpoints
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore patterns
├── .env                # Environment variables (not in repo)
└── README.md           # This file
```

### Logging

The server uses Python's built-in logging module. Logs include:
- Model loading status
- Inference requests
- Errors and exceptions

Logs are output to stdout with the format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Integration with n8n

This server is designed to work seamlessly with n8n workflows:

1. Add an HTTP Request node in your n8n workflow
2. Configure it to POST to `http://your-server:8000/inference`
3. Set the request body with your prompt and parameters
4. Process the returned generated text in subsequent nodes

## Performance Considerations

- **GPU Support**: The server automatically uses GPU if available (via PyTorch CUDA)
- **Model Loading**: Models are loaded once on startup to minimize latency
- **Memory**: Model size varies; GPT-2 requires ~500MB, larger models need more
- **First Request**: May be slower due to model warmup

## Troubleshooting

### Model Not Loading

If the model fails to load:
- Check available disk space for model download
- Verify internet connection for first-time model download
- Check logs for specific error messages

### Out of Memory

For large models:
- Use a smaller model (e.g., `distilgpt2`)
- Reduce `max_length` parameter
- Ensure sufficient RAM/VRAM

### Slow Generation

To improve speed:
- Use GPU if available
- Reduce `max_length`
- Use smaller models
- Decrease `num_return_sequences`

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.