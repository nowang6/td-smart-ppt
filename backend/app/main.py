from fastapi import FastAPI
from app.api.v1 import api_router
from fastapi.middleware.cors import CORSMiddleware
from langfuse import get_client
from app.core.config import settings
 
from pydantic_ai.agent import Agent
 
from langfuse import Langfuse

langfuse = Langfuse(
  secret_key=settings.LANGFUSE_SECRET_KEY,
  public_key=settings.LANGFUSE_PUBLIC_KEY,
  host="https://hipaa.cloud.langfuse.com"
)
 
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")
    
# Initialize Pydantic AI instrumentation
Agent.instrument_all()


app = FastAPI(
    title="TD Smart PPT Backend",
    version="1.0.0",
    docs_url="/swagger",     # 改 Swagger 文档路径
    openapi_url="/openapi.json"  # OpenAPI schema 地址
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 v1 API
app.include_router(api_router, prefix="/api/v1")


def main():
    """主函数入口"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

