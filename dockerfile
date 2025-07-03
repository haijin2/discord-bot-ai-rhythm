# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy your requirements.txt first (for caching dependencies)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your bot’s code into the container
COPY . .

# Set environment variable for the Discord token (optional, can also use .env)
# ENV DISCORD_TOKEN=your_token_here

# Expose ports if needed (usually not needed for a Discord bot)
# EXPOSE 8080

# Install FFmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Run your bot
CMD ["python3", "rhythm.py"]
