# Description:
#
# This script is used to manage the deployment of a Craft.AI pipeline.
# It performs the following actions:
#
# 1. Deletes the existing pipeline (if it exists) using the name `selectendpointpipeline`.
# 2. Defines the input and output structure for the pipeline function `select_endpoint`.
# 3. Creates a new pipeline using a Python function located at `src/select_endpoint.py`.
# 4. Runs a test execution of the pipeline with a sample input message to ensure it works.
# 5. Deploys the pipeline as an API endpoint named `selectendpointapi` in low-latency mode.
#    The deployment is configured to allow parallel executions (up to 8 per pod).
#
# This is especially useful for production-ready scenarios where you want high-throughput,
# non-blocking endpoint access for dynamic routing or load-balanced logic inside the `select_endpoint` function.

import os
from craft_ai_sdk import CraftAiSdk
from craft_ai_sdk.io import Input, Output
from dotenv import load_dotenv

load_dotenv()
sdk = CraftAiSdk()

try:
    sdk.delete_pipeline("selectendpointpipeline", force_deployments_deletion=True)
except Exception as e:
    print(f"Ignored deletion: {e}")

# Define pipeline input
input_param = Input(
    name="message",
    data_type="string",
    description="Message to send"
)

# Define pipeline output
output_param = Output(
    name="results",
    data_type="string",  # or "json" if needed
    description="Response from the selected model"
)

# Create pipeline
print("Starting pipeline creation")
sdk.create_pipeline(
    pipeline_name="selectendpointpipeline",
    function_name="select_endpoint",
    function_path="src/select_endpoint.py",
    container_config={
        "local_folder": os.getcwd(),
        "requirements_path": "requirements.txt",
        "included_folders": ["src"]
    },
    inputs=[input_param],
    outputs=[output_param]
)

print("Pipeline created successfully")

# Test run created pipeline
print("Testing pipeline execution")

execution_result = sdk.run_pipeline(pipeline_name="selectendpointpipeline", inputs={"message": "test"})
print("Test execution result:", execution_result)

# Deploy as API
print("Starting deployment (API)")

sdk.create_deployment(
    pipeline_name="selectendpointpipeline",
    deployment_name="selectendpointapi",
    execution_rule="endpoint",
    mode="low_latency",
    enable_parallel_executions=True,
    max_parallel_executions_per_pod=8 # Your can change this parameter
)

print("Deployment completed.")
