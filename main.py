"""
GuiXiaoXiRag FastAPI 服务主入口
重构版本 - 模块化设计，清晰的职责分离
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from common.config import settings
from initialize import create_app
from routers import (
    query_router, document_router, knowledge_base_router,
    knowledge_graph_router, system_router, intent_recogition_router,
    cache_management_router
)

# 创建应用实例
app = create_app()

# 添加路由（路由器已经包含了prefix，不需要重复添加）
app.include_router(query_router, tags=["查询"])
app.include_router(document_router, tags=["文档管理"])
app.include_router(knowledge_base_router, tags=["知识库管理"])
app.include_router(knowledge_graph_router, tags=["知识图谱"])
app.include_router(system_router, tags=["系统管理"])
app.include_router(intent_recogition_router, tags=["意图识别"])
app.include_router(cache_management_router, tags=["缓存管理"])


# 全局异常处理器
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "请求参数验证失败",
            "error_code": "VALIDATION_ERROR",
            "details": exc.errors(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": "INTERNAL_ERROR",
            "path": str(request.url.path)
        }
    )


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """服务根路径"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health():
    """简单健康检查"""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
