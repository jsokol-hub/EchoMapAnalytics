FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends cron curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first (avoids ~2GB+ CUDA/Triton, prevents "no space left" on small servers)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data .streamlit

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8501

# No HEALTHCHECK — avoids Docker restarting the container when Streamlit is busy on first request.
# CapRover/nginx may still do a quick connect; we listen on 8501 immediately (preload runs in background).
ENTRYPOINT ["/entrypoint.sh"]
