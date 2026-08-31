FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        mkvtoolnix \
        python3 \
        python3-pip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY extractor.py .

EXPOSE 9870

CMD ["uvicorn", "extractor:app", "--host", "0.0.0.0", "--port", "9870"]
