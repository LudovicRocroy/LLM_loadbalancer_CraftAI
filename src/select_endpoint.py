# Description du script :
#
# Ce script permet de sélectionner un endpoint parmi une liste d'URLs d'API disponibles, de lui envoyer une requête POST,
# et de gérer les erreurs en cas de réponse invalide ou d'exception. Les principales étapes sont les suivantes :
#
# 1. **Chargement des endpoints** : Le script récupère les URLs des endpoints à partir d'une variable d'environnement 
#    `ENDPOINT_LIST` à ajouter dans les Settings de l'environnement, qui doit être au format JSON, par exemple : 
#    {   "1": {     "endpoint_url": "https://soft-japet-magenta-xi-4.mlops-platform.craft.ai/endpoints/llm-gemma2-9b",     "ENDPOINT TOKEN"   },   "2": {     "endpoint_url": "https://proud-skoll-indigo-omicron-10.mlops-platform.craft.ai/endpoints/llm-gemma2-9b",     "endpoint_token": "ENDPOINT TOKEN"   }}
# 
# 2. **Mélange aléatoire** : Après avoir chargé les endpoints, le script les mélange aléatoirement pour éviter un biais 
#    lié à l'ordre de la liste.
# 
# 3. **Requête POST et gestion des erreurs** : Pour chaque endpoint (dans l'ordre mélangé), une requête POST est envoyée 
#    avec un message. Si le endpoint répond avec un code HTTP 200, la réponse est considérée comme valide. Sinon, une 
#    nouvelle tentative est effectuée avec le endpoint suivant dans la liste.
# 
# 4. **Enregistrement des métriques** : À chaque étape, des métriques sont enregistrées via `CraftAiSdk`, pour suivre 
#    le statut des requêtes et l'ordre d'essai des endpoints.
# 
# 5. **Retour de la réponse** : Si une réponse valide est obtenue, le résultat est retourné dans un format structuré. 
#    Si aucun endpoint n'est fonctionnel, une exception est levée.
# 
# Ce script est utile pour envoyer une requête à une série d'API disponibles, tout en gérant les erreurs et en collectant
# des métriques sur le processus.

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
        print("Liste brute des endpoints chargée.")
    except Exception as e:
        print(f"Erreur de parsing de ENDPOINT_LIST : {e}")
        raise ValueError("Variable d'environnement ENDPOINT_LIST invalide ou absente.")

    sdk = CraftAiSdk()

    print("\nEndpoints disponibles :")
    for ep in endpoint_list.values():
        print(ep["endpoint_url"])
    print("\n")

    endpoints = list(endpoint_list.values())
    random.shuffle(endpoints)
    
    for i, ep in enumerate(endpoints, start=1):
        print(f"⏳ Tentative {i} - {ep['endpoint_url']}")

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

            # ✅ Ajout : on vérifie que le statut HTTP est bien 200
            if response.status_code != 200:
                print(f"❌ Échec (status {response.status_code}) via {ep['endpoint_url']}")
                continue

            print(f"✅ Succès via {ep['endpoint_url']}")
            print(f"⏱ Temps requête POST : {request_duration:.3f} secondes")

            sdk.record_metric_value("requete-status", response.status_code)
            sdk.record_metric_value("endpoint-essai", i)
            print(f"Statut retour endpoint : {response.status_code}")

            results_content = response.json().get("outputs", {}).get("results", "Aucune réponse")

            end_total = time.time()
            total_duration = end_total - start_total
            print(f"⏱ Temps total fonction : {total_duration:.3f} secondes")

            return {"results": results_content}

        except Exception as e:
            print(f"❌ Échec avec {ep['endpoint_url']} : {e}")
            continue

    raise Exception("Tous les endpoints ont échoué.")
