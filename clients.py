import httpx
from config import settings

async def get_airalo_client():
    if settings.USE_AIRALO_MOCK:
        
        class MockResponse:
            def __init__(self):
                self.status_code = 200
            def json(self):
                return {
                    "data": [
                        {"package": "Global 1GB", "price": 9.00, "validity": "7 days"},
                        {"package": "Europe 3GB", "price": 15.00, "validity": "30 days"}
                    ],
                    "message": "MOCKED_DATA_FOR_STUDENT_PROJECT"
                }
        
        class MockClient:
            async def get(self, url, **kwargs):
                return MockResponse()
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass

        yield MockClient()
    else:
        async with httpx.AsyncClient(
            base_url="https://sandbox-api.airalo.com/v2",
            headers={
                "client-id": settings.AIRALO_API_KEY,
                "client-secret": settings.AIRALO_API_SECRET
            }
        ) as client:
            yield client