from src import app
with app.app_context():
    client = app.test_client()
    resp1 = client.get('/api/analytics')
    print("Default Metrics:")
    print(resp1.get_json())
    resp2 = client.get('/api/analytics?date=2024-05-18')
    print("Filtered by Date (2024-05-18):")
    print(resp2.get_json())
