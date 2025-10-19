#!/usr/bin/env python3
"""
Example usage script for the n8n Inference Server API.
This demonstrates how to interact with the server endpoints.
"""
import json


def print_section(title):
    """Print a formatted section title."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def show_health_check():
    """Show health check endpoint example."""
    print_section("Health Check Endpoint")
    
    print("Endpoint: GET /health")
    print("\nDescription:")
    print("  Check if the server is running and the model is loaded.")
    
    print("\nCURL Example:")
    print("  curl http://localhost:8000/health")
    
    print("\nExpected Response:")
    response = {
        "status": "healthy",
        "model_loaded": True,
        "model_name": "gpt2"
    }
    print("  " + json.dumps(response, indent=2).replace("\n", "\n  "))
    
    print("\nPython Example:")
    print("""
  import requests
  
  response = requests.get("http://localhost:8000/health")
  data = response.json()
  
  if data["status"] == "healthy" and data["model_loaded"]:
      print(f"Server is healthy! Model: {data['model_name']}")
  """)


def show_inference_basic():
    """Show basic inference endpoint example."""
    print_section("Basic Inference Endpoint")
    
    print("Endpoint: POST /inference")
    print("\nDescription:")
    print("  Generate text based on a prompt using default parameters.")
    
    request = {
        "prompt": "Once upon a time"
    }
    
    print("\nMinimal Request Body:")
    print("  " + json.dumps(request, indent=2).replace("\n", "\n  "))
    
    print("\nCURL Example:")
    curl_cmd = f"""curl -X POST http://localhost:8000/inference \\
    -H "Content-Type: application/json" \\
    -d '{json.dumps(request)}'"""
    print("  " + curl_cmd.replace("\n", "\n  "))
    
    print("\nExpected Response:")
    response = {
        "generated_text": [
            "Once upon a time, there was a beautiful princess who lived in a magical castle."
        ],
        "prompt": "Once upon a time",
        "model": "gpt2"
    }
    print("  " + json.dumps(response, indent=2).replace("\n", "\n  "))


def show_inference_advanced():
    """Show advanced inference endpoint example."""
    print_section("Advanced Inference with Parameters")
    
    print("Endpoint: POST /inference")
    print("\nDescription:")
    print("  Generate text with custom parameters for fine-tuned control.")
    
    request = {
        "prompt": "The future of artificial intelligence is",
        "max_length": 100,
        "temperature": 0.8,
        "top_p": 0.9,
        "num_return_sequences": 2
    }
    
    print("\nRequest Body with Parameters:")
    print("  " + json.dumps(request, indent=2).replace("\n", "\n  "))
    
    print("\nParameter Descriptions:")
    params = [
        ("prompt", "Text prompt for generation (required, 1-1000 chars)"),
        ("max_length", "Maximum length of generated text (optional, 1-500, default: 100)"),
        ("temperature", "Controls randomness (optional, 0.1-2.0, default: 0.7)"),
        ("top_p", "Nucleus sampling threshold (optional, 0.0-1.0, default: 0.9)"),
        ("num_return_sequences", "Number of sequences to generate (optional, 1-5, default: 1)")
    ]
    for param, desc in params:
        print(f"  • {param}: {desc}")
    
    print("\nCURL Example:")
    curl_cmd = f"""curl -X POST http://localhost:8000/inference \\
    -H "Content-Type: application/json" \\
    -d '{json.dumps(request)}'"""
    print("  " + curl_cmd.replace("\n", "\n  "))
    
    print("\nExpected Response:")
    response = {
        "generated_text": [
            "The future of artificial intelligence is bright and full of possibilities...",
            "The future of artificial intelligence is transforming how we work and live..."
        ],
        "prompt": "The future of artificial intelligence is",
        "model": "gpt2"
    }
    print("  " + json.dumps(response, indent=2).replace("\n", "\n  "))


def show_error_handling():
    """Show error handling examples."""
    print_section("Error Handling")
    
    print("The server includes comprehensive error handling:\n")
    
    errors = [
        ("400 Bad Request", "Invalid request parameters", {
            "error": "Empty prompt",
            "request": {"prompt": ""},
            "response": {"detail": "Validation error: Prompt cannot be empty or whitespace only"}
        }),
        ("503 Service Unavailable", "Model not loaded", {
            "error": "Called before model initialization",
            "response": {"detail": "Model not loaded. Please wait for model initialization."}
        }),
        ("500 Internal Server Error", "Generation failure", {
            "error": "Error during text generation",
            "response": {"detail": "Text generation failed: <error details>"}
        })
    ]
    
    for status, description, example in errors:
        print(f"{status}: {description}")
        print(f"  Example: {example['error']}")
        print(f"  Response: {json.dumps(example['response'], indent=2).replace(chr(10), chr(10) + '    ')}")
        print()


def show_n8n_integration():
    """Show n8n integration example."""
    print_section("Integration with n8n")
    
    print("To use this server in n8n workflows:")
    print()
    print("1. Add an HTTP Request node to your workflow")
    print()
    print("2. Configure the node:")
    print("   • Method: POST")
    print("   • URL: http://your-server:8000/inference")
    print("   • Authentication: None (or as configured)")
    print()
    print("3. Set the request body (JSON):")
    request = {
        "prompt": "{{ $json.prompt }}",
        "max_length": 100,
        "temperature": 0.7
    }
    print("   " + json.dumps(request, indent=2).replace("\n", "\n   "))
    print()
    print("4. Use the response in subsequent nodes:")
    print("   • Access generated text: {{ $json.generated_text[0] }}")
    print("   • Access the prompt used: {{ $json.prompt }}")
    print("   • Access the model name: {{ $json.model }}")
    print()
    print("5. Add error handling:")
    print("   • Check response status code")
    print("   • Handle 503 errors (model loading)")
    print("   • Implement retry logic if needed")


def show_configuration():
    """Show configuration examples."""
    print_section("Server Configuration")
    
    print("Environment Variables (.env file):\n")
    
    env_vars = [
        ("HOST", "0.0.0.0", "Server host address"),
        ("PORT", "8000", "Server port"),
        ("MODEL_NAME", "gpt2", "Hugging Face model identifier"),
        ("MODEL_CACHE_DIR", "./cache", "Directory for model cache"),
        ("MAX_LENGTH", "100", "Default maximum generation length"),
        ("TEMPERATURE", "0.7", "Default sampling temperature"),
        ("TOP_P", "0.9", "Default nucleus sampling parameter")
    ]
    
    for var, default, description in env_vars:
        print(f"  {var}={default}")
        print(f"    # {description}\n")
    
    print("\nSupported Models:")
    models = [
        ("gpt2", "Default, lightweight (124M parameters)"),
        ("gpt2-medium", "Larger model (355M parameters)"),
        ("distilgpt2", "Faster, smaller version"),
        ("microsoft/DialoGPT-small", "Conversational model"),
        ("EleutherAI/gpt-neo-125M", "Alternative architecture")
    ]
    
    for model, description in models:
        print(f"  • {model}: {description}")


def main():
    """Main function to show all examples."""
    print("\n" + "=" * 70)
    print("  n8n Inference Server - API Usage Examples")
    print("=" * 70)
    
    show_health_check()
    show_inference_basic()
    show_inference_advanced()
    show_error_handling()
    show_n8n_integration()
    show_configuration()
    
    print("\n" + "=" * 70)
    print("  For more information, visit: http://localhost:8000/docs")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
