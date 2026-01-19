#Base image -  m1 dev environment
FROM python:3.12-slim 

#env variable to ensure logs appear on render dashboard
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Setup App Directory
WORKDIR /app

# 5. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Code
COPY src/ ./src/

# 7. Start the Server
# Render expects apps to listen on port 10000 by default
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "10000"]