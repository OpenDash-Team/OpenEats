def test_health_endpoint_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200