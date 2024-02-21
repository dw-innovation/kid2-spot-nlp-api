from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

response = client.post("/transform-sentence-to-imr", headers={"X-Token": "coneofsilence"},
                       json={"sentence": "Find bars in Berlin"})

assert response.status_code == 200

response = client.post("/transform-sentence-to-imr", headers={"X-Token": "coneofsilence"},
                       json={"sentence": "find me a wind turbine"})

print(response)

