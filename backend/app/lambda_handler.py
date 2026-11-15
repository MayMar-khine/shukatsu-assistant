"""Entry point for AWS Lambda (see README "Deploying on AWS").
Mangum translates API Gateway / Lambda Function URL events into ASGI calls,
so the same FastAPI app runs unchanged. Install with: pip install mangum
"""
from mangum import Mangum

from .main import app

handler = Mangum(app)
