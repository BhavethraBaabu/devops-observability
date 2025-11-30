from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

app = FastAPI(title="DevOps Observability Demo")

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "HTTP request latency", ["endpoint"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        endpoint = request.url.path
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, http_status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(process_time)

        return response


app.add_middleware(MetricsMiddleware)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def root():
    return {
        "message": "DevOps Observability Demo is running",
        "endpoints": ["/health", "/hello", "/metrics"]
    }

