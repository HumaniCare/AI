import asyncio

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager

from app.controller.RecordController import router
# from app.service.subscribe import subscribe_schedule

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     task = asyncio.create_task(subscribe_schedule())
#     yield
#     task.cancel()
#     try:
#         await task
#     except asyncio.CancelledError:
#         print("Redis task cancelled")


app = FastAPI(lifespan = lifespan)

auth_scheme = HTTPBearer()


def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return token


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="HumaniCare API Documentation",
        version="1.0",
        description="HumaniCare API documentation for the application",
        routes=app.routes,
    )
    # Add the security scheme for Bearer token
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# # Swagger UI 경로 설정
# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html(req: Request):
#     root_path = req.scope.get("root_path", "").rstrip("/")
#     openapi_url = root_path + "/openapi.json"  # OpenAPI 경로 설정
#     return get_swagger_ui_html(
#         openapi_url=openapi_url,
#         title="Peach API Documentation",
#     )
#
# # OpenAPI JSON 경로 설정
# @app.get("/openapi.json", include_in_schema=False)
# async def custom_openapi_json():
#     return app.openapi()

origins = [
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# before_script, statistics_filler_json, statistics_silence_json = startSTT(
#     "https://peachmentor-bucket.s3.ap-northeast-2.amazonaws.com/record/%E1%84%82%E1%85%A9%E1%86%A8%E1%84%8B%E1%85%B3%E1%86%B7.m4a")
# self_feedback = "그래도 주어진 시간동안 말을 이어나가긴 했는데 말을 자연스럽게 연결하지 못한 것 같아"
# feedbackAss = FeedbackAssistant(before_script, statistics_filler_json, statistics_silence_json)
# feedback = feedbackAss.get_feedback()
# print(feedback)
