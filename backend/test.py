from starlette.testclient import TestClient

from app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200



if __name__ == "__main__":
    test_read_main()