# Craft.AI Smart Endpoint Selector

This project provides a flexible and resilient API system designed to dynamically route requests to multiple machine learning model endpoints deployed on the [Craft.AI MLOps platform](https://mlops-platform-documentation.craft.ai/).

## 🚀 What It Does

The `select_endpoint` function:
- Loads a list of available model endpoints from an environment variable (`ENDPOINT_LIST`).
- Randomly shuffles the list to avoid bias.
- Tries to send a POST request to each endpoint in order until it receives a valid (HTTP 200) response.
- Tracks and logs key execution metrics using Craft.AI's native SDK tools.

## 🧩 Components

### `src/select_endpoint.py`
This is the core Python function that:
- Chooses and queries an available endpoint.
- Handles failures gracefully with retries.
- Records metrics such as selected endpoints, response times, HTTP status codes, and more.

### `deploy_select_endpoint.py`
This deployment script:
- Deletes any existing pipeline and deployment named `selectendpointpipeline` / `selectendpointapi`.
- Recreates a pipeline using the `select_endpoint.py` function.
- Tests it locally.
- Deploys it as a low-latency API with parallel execution support.

### `.env`
This file stores your Craft.AI SDK credentials and environment URL:
```
CRAFT_AI_SDK_TOKEN="your-token"
CRAFT_AI_ENVIRONMENT_URL="https://your-environment-url.craft.ai"
```

### `requirements.txt`
Dependencies used in the project:
- `craft_ai_sdk`
- `requests`

## 📦 Usage

1. Define the `ENDPOINT_LIST` environment variable in your Craft.AI environment settings.  
   Format (JSON string):
   ```json
   {
     "1": {
       "endpoint_url": "https://your-craft-ai-endpoint/llm-model-1",
       "endpoint_token": "ENDPOINT_TOKEN_1"
     },
     "2": {
       "endpoint_url": "https://your-craft-ai-endpoint/llm-model-2",
       "endpoint_token": "ENDPOINT_TOKEN_2"
     }
   }
   ```

2. Deploy the function using:
   ```bash
   python deploy_select_endpoint.py
   ```

3. Call the endpoint with a message:
   ```json
   {
     "inputs": {
       "message": "Hello, AI!"
     }
   }
   ```

## 📊 Metrics Tracked

- `request-status` — HTTP status of the final response.
- `endpoint-attempt` — Index of the endpoint that succeeded.
- `endpoint-candidate-X` — Endpoint URLs attempted in order.
- `statut-endpoint-X` — HTTP status for each attempted endpoint (or -1 if unreachable).
- Timing (POST duration and total function time) via printed logs.

## 🧠 Ideal Use Case

This project is perfect for:
- Load balancing across multiple LLM backends.
- Fallback logic between models of varying capabilities or availability.
- Monitoring endpoint health and performance over time.

## 🛠️ Maintainers

Built with ❤️ by the Craft.AI automation team.

For questions or support, contact us via [Craft.AI Support](https://craft.ai).
