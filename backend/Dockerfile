FROM python:3.11-slim

# =========================================================
# WORK DIRECTORY
# =========================================================

WORKDIR /app

# =========================================================
# PYTHON SETTINGS
# =========================================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# =========================================================
# CHROME SETTINGS
# =========================================================

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# =========================================================
# SYSTEM DEPENDENCIES
# =========================================================

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    netcat-openbsd \
    xvfb \
    fonts-liberation \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libxss1 \
    libxtst6 \
    libu2f-udev \
    xdg-utils \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# =========================================================
# PIP
# =========================================================

RUN pip install --upgrade pip

# =========================================================
# REQUIREMENTS
# =========================================================

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# =========================================================
# PROJECT FILES
# =========================================================

COPY . .

# =========================================================
# STATIC / MEDIA / PROFILES
# =========================================================

RUN mkdir -p /app/browser_profiles

RUN mkdir -p /app/staticfiles

RUN mkdir -p /app/media

# =========================================================
# PORT
# =========================================================

EXPOSE 8000

# =========================================================
# DEFAULT COMMAND
# =========================================================

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]