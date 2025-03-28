import os
from craft_ai_sdk import CraftAiSdk
from craft_ai_sdk.io import Input, Output
from dotenv import load_dotenv

load_dotenv()
sdk = CraftAiSdk()

try:
    sdk.delete_pipeline("selectendpointpipeline", force_deployments_deletion=True)
except Exception as e:
    print(f"Suppression ignorée : {e}")

# Définition de l'entrée
input_param = Input(
    name="message",
    data_type="string",
    description="Message à envoyer"
)

# Définition de la sortie (ajustée ici)
output_param = Output(
    name="results",
    data_type="string",  # ou "json" si nécessaire
    description="Réponse du modèle sélectionné"
)

# Création du pipeline
print("Création du pipeline")
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

print("Création du pipeline terminée")
print("Test du pipeline")

execution_result = sdk.run_pipeline(pipeline_name="selectendpointpipeline", inputs={"message": "test"})
print("Exécution de test terminée :", execution_result)

# Déploiement
print("Création du déploiement (api)")

sdk.create_deployment(
    pipeline_name="selectendpointpipeline",
    deployment_name="selectendpointapi",
    execution_rule="endpoint",
    mode="low_latency",
    enable_parallel_executions=True,
    max_parallel_executions_per_pod=8
)

print("Déploiement terminé.")
