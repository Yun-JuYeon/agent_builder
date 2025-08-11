from fastapi import APIRouter
from app.model.test_models import TestRequest, TestResponse

test_router = APIRouter()


@test_router.post("/01")
def test_router_1(body: TestRequest):
    request_id = body.id
    request_message = body.query
    
    print(f"request_id: {request_id}\nrequest_message: {request_message}")

    return TestResponse(id=request_id, message="test1 api response")