# Dockerfile — tailored for Render (headless pygame + ffmpeg)
FROM python:3.11-slim

# Install system deps (ffmpeg + fonts + libs needed by pygame)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libportmidi0 \
    build-essential \
    pkg-config \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set envs for headless pygame and port
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy
ENV PORT=8080

# Copy requirements (create this file with your deps)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY . /app

EXPOSE 8080

# Run uvicorn (Render will map port)
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
