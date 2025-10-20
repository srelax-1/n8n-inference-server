# N8N Inference Server

A FastAPI-based inference server for text classification using transformer models. This server provides a simple REST API for running inference on language models, designed to integrate seamlessly with n8n workflows.

## Features

- Fast and efficient text classifier using Hugging Face transformers
- Configurable via environment variables
- Health check endpoint for monitoring
- Proper error handling and logging


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
venv\Scripts\activate
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
MODEL_NAME=facebook/bart-large-mnli

# API settings
API_TITLE=n8n Inference Server
API_VERSION=1.0.0
API_DESCRIPTION=A lightweight local Zero-shot text classifier that uses subject + body and label descriptions with Hugging Face transformers
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `HOST` | Server host address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `MODEL_NAME` | Hugging Face model identifier | `facebook/bart-large-mnli` |

## Usage

### Starting the Server

Run the server using uvicorn:

```bash
uvicorn inference_server:app --host 0.0.0.0 --port 8000 --reload
```

The server will start and load the model. You should see logs indicating successful model loading.

### API Endpoints

#### Health Check

Check if the server is running and the model is loaded.

**Endpoint:** `GET /status`

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "message": "Classifier API is running."
}
```

#### Text Generation

Generate text based on a prompt.

**Endpoint:** `POST /classify`

**Request Body:**
```json
{
  "subject": "Access needed",
  "body": "Dear team, Kindly help unlock my access",
  "labels": [
    "team_1": "the team that helps with access to resource in the organisation",
    "team_2": "The teams handles issue that are to be resolve by thirdparty",
    "others": "Issues that are not resolve by team_1 and team_2"
  ],
  "ticket_id": 13654277,
  "reference_id": 1
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | Yes | Subject of the ticket to be classified |
| `body` | string | Yes | Body of the ticket to be classified |
| `labels` | dict | Yes | Atleast one labels |
| `ticket_id` | integer | No | ticket id |
| `reference_id` | integer | No | A reference number of the ticket |

**Response:**
```json
{
  "text": "This contain the subject and body of the ticket",
  "best_label": "team_1",
  "confidence": 0.3769250810146332,
  "labels": [
    "team_1": "the team that helps with access to resource in the organisation",
    "team_2": "The teams handles issue that are to be resolve by thirdparty",
    "others": "Issues that are not resolve by team_1 and team_2"
  ],
  "scores": [
    0.3769250810146332,
    0.3403571844100952,
    0.2827177047729492
  ],
  "ticket_id": 13654277,
  "reference_id": 1
}
```

## Error Handling

The server includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **503 Service Unavailable**: Model not loaded yet
- **500 Internal Server Error**: Generation or server errors

All errors return JSON responses with a `detail` field explaining the issue.

## Model Support

The server supports any Hugging Face model compatible with `zero-shot-classification`. Some recommended models:

- `facebook/bart-large-mnli` (lightweight)
- `facebook/bart-large-mnli`

To use a different model, set the `MODEL_NAME` environment variable.

## Development

### Project Structure

```
n8n-inference-server/
├── inference_server.py            
├── requirements.txt   
├── .gitignore         
├── .env                
└── README.md           
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
2. Configure it to POST to `http://your-server:8000/classify`
3. Set the request body with your prompt and parameters
4. Process the returned generated text in subsequent nodes

## Performance Considerations

- **GPU Support**: The server automatically uses GPU if available (via PyTorch CUDA)
- **Model Loading**: Models are loaded once on startup to minimize latency
- **Memory**: Model size varies
- **First Request**: May be slower due to model warmup

## Troubleshooting

### Model Not Loading

If the model fails to load:
- Check available disk space for model download
- Verify internet connection for first-time model download
- Check logs for specific error messages


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.