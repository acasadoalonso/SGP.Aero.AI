FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SGP_MCP_TRANSPORT=http \
    SGP_MCP_HOST=0.0.0.0 \
    SGP_MCP_PORT=9010 \
    SGP_MCP_PATH=/soaringspot\
    SGP_API_URL=http://localhost:8000 \
    SGP_HTTP_TIMEOUT_SEC=60 \
    SGP_VERIFY_TLS=true

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sgp_server.py ./
COPY sgp_api.py ./
COPY .env        ./

EXPOSE 9010

CMD ["python3", "sgp_server.py"]

