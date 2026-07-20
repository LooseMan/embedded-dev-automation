import pytest

@pytest.mark.asyncio
async def test_post_add(client):

    response = await client.post("/add", json={"a": 5, "b": 3})
    assert response.json() == {"result": 9}
    assert response.status_code == 200
