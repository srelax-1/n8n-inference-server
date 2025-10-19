# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/srelax-1/n8n-inference-server.git
cd n8n-inference-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
# Start the server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Text
```bash
curl -X POST http://localhost:8000/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!"}'
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Create a `.env` file to customize settings:

```env
MODEL_NAME=gpt2
MAX_LENGTH=100
TEMPERATURE=0.7
PORT=8000
```

## Project Structure

```
n8n-inference-server/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── requirements.txt     # Dependencies
├── .gitignore          # Git ignore patterns
├── README.md           # Full documentation
├── QUICKSTART.md       # This file
├── examples.py         # API usage examples
└── validate_server.py  # Validation script
```

## Validation

Before running, validate the server structure:

```bash
python validate_server.py
```

## Common Issues

**Model not loading**: Ensure you have enough disk space and internet connection for the first model download.

**Port already in use**: Change the PORT in .env file or use a different port.

**Out of memory**: Use a smaller model like `distilgpt2` in the MODEL_NAME configuration.

## Support

For more detailed information, see README.md or run:
```bash
python examples.py
```
