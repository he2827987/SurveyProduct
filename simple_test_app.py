#!/usr/bin/env python3
"""
简单的测试应用，用于验证Render部署是否工作
"""

from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Survey Product is running!", "environment": os.getenv("ENVIRONMENT", "unknown")}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)