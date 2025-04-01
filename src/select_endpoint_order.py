import os
import json
import requests
import time
from craft_ai_sdk import CraftAiSdk

# Nom du fichier dans le Datastore
DATASTORE_OBJECT_PATH = "last_endpoint_index.txt"
TMP_PATH = "/tmp/last_endpoint_index.txt"

def select_endpoint(message: str):
    start_total = time.time()
    sdk = CraftAiSdk()

    try:
        endpoint_list = json.loads(os.environ["ENDPOINT_LIST"])
        print("✅ Raw endpoint list loaded.")
    except Exception as e:
        print(f"❌ Error parsing ENDPOINT_LIST: {e}")
        raise ValueError("Environment variable ENDPOINT_LIST is invalid or missing.")

    endpoints = list(endpoint_list.values())
    num_endpoints = len(endpoints)
    print("num_endpoints:", num_endpoints)

    # Lecture de l’index depuis le datastore
    try:
        sdk.download_data_store_object(DATASTORE_OBJECT_PATH, TMP_PATH)
        with open(TMP_PATH, "r") as f:
            last_endpoint_index = int(f.read().strip())
            print(f"📥 Loaded last_endpoint_index from datastore: {last_endpoint_index}")
    except Exception as e:
        print(f"⚠️ Could not load index from datastore, defaulting to 0: {e}")
        last_endpoint_index = 0

    print("\nAvailable endpoints:")
    for ep in endpoints:
        print(ep["endpoint_url"])
    print()

    for attempt in range(num_endpoints):
        index = (last_endpoint_index + attempt) % num_endpoints
        ep = endpoints[index]
        print(f"⏳ Attempt {attempt + 1} - {ep['endpoint_url']}")

        try:
            start_request = time.time()
            response = requests.post(
                ep["endpoint_url"],
                json={"message": message},
                headers={"Authorization": f"EndpointToken {ep['endpoint_token']}"},
                timeout=120
            )
            request_duration = time.time() - start_request

            if response.status_code != 200:
                print(f"❌ Failed (status {response.status_code}) via {ep['endpoint_url']}")
                continue

            print(f"✅ Success via {ep['endpoint_url']}")
            print(f"⏱ POST request time: {request_duration:.3f} seconds")

            sdk.record_metric_value("request-status", response.status_code)
            sdk.record_metric_value("endpoint-index-used", index)

            next_index = (index + 1) % num_endpoints
            print(f"💾 Saving next index to datastore: {next_index}")
            try:
                with open(TMP_PATH, "w") as f:
                    f.write(str(next_index))
                with open(TMP_PATH, "rb") as binary_file:
                    sdk.upload_data_store_object(binary_file, DATASTORE_OBJECT_PATH)
            except Exception as e:
                print(f"❌ Failed to save index to datastore: {e}")

            results_content = response.json().get("outputs", {}).get("results", "No response")
            total_duration = time.time() - start_total
            print(f"⏱ Total function time: {total_duration:.3f} seconds")

            return {"results": results_content}

        except Exception as e:
            print(f"❌ Exception with {ep['endpoint_url']}: {e}")
            continue

    raise Exception("All endpoints failed.")
