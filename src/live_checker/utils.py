from httpx import AsyncClient, TimeoutException, RequestError
from typing import Dict, Union

async def check_link(url: str) -> Dict[str, Union[int, float]]:
    async with AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10)
            return {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
        except TimeoutException:
            return {
                "status_code": 408,
                "response_time": 10.0
            }
        except RequestError:
            return {
                "status_code": 500,
                "response_time": 0.0
            }
