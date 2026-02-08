FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install reportlab for PDF generation inside container (optional but useful)
RUN pip install reportlab

# Copy the rest of the application
COPY . .

# Default command (can be overridden)
CMD ["python", "src/chat.py"]
