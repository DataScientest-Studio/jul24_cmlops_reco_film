import requests
import pytest
import time

@pytest.fixture(scope="session")
def api_url():
    # URL de base de l'API
    base_url = "http://localhost:8002"
    
    # Attendre que l'API soit prête
    max_retries = 30
    for _ in range(max_retries):
        try:
            response = requests.get(f"{base_url}/model_info")
            if response.status_code == 200:
                return base_url
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    
    raise Exception("L'API n'est pas disponible après 30 secondes")

def test_model_info(api_url):
    response = requests.get(f"{api_url}/model_info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "model_version" in data
    assert "source" in data

def test_recommend(api_url):
    # Test avec un vecteur de genres valide
    genres = "0.0,0.28,0.28,0.04,0.1,0.34,0.14,0.0,0.38,0.1,0.0,0.04,0.0,0.04,0.06,0.18,0.1,0.4,0.0,0.0"
    response = requests.post(
        f"{api_url}/recommend",
        json={"genres": genres}
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 1
    assert len(data["recommendations"][0]) == 20 
