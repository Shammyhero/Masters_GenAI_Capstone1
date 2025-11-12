# Lightweight Python runtime
FROM python:3.11-slim

# Prevents Python from writing .pyc files to disk and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies (if needed) and cleanup apt lists
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create and use a non-root user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Expose a common port (adjust if your app uses a different port)
EXPOSE 8080

# Default command — run Streamlit app on port 8080 and listen on all interfaces
# Adjust the port if you'd like to use Streamlit's default 8501 instead.
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
