# Script Description:
#
# This script selects an endpoint from a list of available API URLs, sends a POST request to it,
# and handles errors in case of invalid responses or exceptions. The main steps are:
#
# 1. **Loading endpoints**: The script retrieves the list of endpoints from an environment variable 
#    `ENDPOINT_LIST`, which must be set in the environment's Settings and formatted as JSON, e.g.:
#    { "1": { "endpoint_url": "https://soft-japet-magenta-xi-4.mlops-platform.craft.ai/endpoints/llm-gemma2-9b", "endpoint_token": "ENDPOINT TOKEN" }, "2": { "endpoint_url": "https://proud-skoll-indigo-omicron-10.mlops-platform.craft.ai/endpoints/llm-gemma2-9b", "endpoint_token": "ENDPOINT TOKEN" } }
#
# 2. **Random shuffling**: After loading, the endpoints are shuffled randomly to avoid order bias.
#
# 3. **POST request and error handling**: For each endpoint (in shuffled order), a POST request is sent
#    with a message. If the endpoint responds with HTTP 200, the response is considered valid.
#    Otherwise, the next endpoint in the list is attempted.
#
# 4. **Metrics recording**: At each step, metrics are recorded using `CraftAiSdk` to track
#    the status of requests and the order of endpoint attempts.
#
# 5. **Returning the response**: If a valid response is obtained, the result is returned in structured format.
#    If no endpoint succeeds, an exception is raised.
#
# This script is useful for sending a request to a sequence of available APIs, while handling
# errors and collecting metrics throughout the process.

import os
import json
import random
import time
import requests
from craft_ai_sdk import CraftAiSdk

def select_endpoint(message: str):
    start_total = time.time()

    try:
        endpoint_list = json.loads(os.environ["ENDPOINT_LIST"])
        print("Raw endpoint list loaded.")
    except Exception as e:
        print(f"Error parsing ENDPOINT_LIST: {e}")
        raise ValueError("Environment variable ENDPOINT_LIST is invalid or missing.")

    sdk = CraftAiSdk()

    print("\nAvailable endpoints:")
    for ep in endpoint_list.values():
        print(ep["endpoint_url"])
    print("\n")

    endpoints = list(endpoint_list.values())
    random.shuffle(endpoints)
    
    for i, ep in enumerate(endpoints, start=1):
        print(f"⏳ Attempt {i} - {ep['endpoint_url']}")

        try:
            start_request = time.time()
            response = requests.post(
                ep["endpoint_url"],
                json={"message": message},
                headers={"Authorization": f"EndpointToken {ep['endpoint_token']}"},
                timeout=120
            )
            end_request = time.time()
            request_duration = end_request - start_request

            if response.status_code != 200:
                print(f"❌ Failed (status {response.status_code}) via {ep['endpoint_url']}")
                continue

            print(f"✅ Success via {ep['endpoint_url']}")
            print(f"⏱ POST request time: {request_duration:.3f} seconds")

            sdk.record_metric_value("request-status", response.status_code)
            sdk.record_metric_value("endpoint-attempt", i)
            print(f"Endpoint response status: {response.status_code}")

            results_content = response.json().get("outputs", {}).get("results", "No response")

            end_total = time.time()
            total_duration = end_total - start_total
            print(f"⏱ Total function time: {total_duration:.3f} seconds")

            return {"results": results_content}

        except Exception as e:
            print(f"❌ Exception with {ep['endpoint_url']}: {e}")
            continue

    raise Exception("All endpoints failed.")