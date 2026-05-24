FROM python:3.11-slim

WORKDIR /app

# =========================================================
# PYTHON
# =========================================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# =========================================================
# SYSTEM DEPENDENCIES
# =========================================================

RUN apt-get update && apt-get install -y \
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
# CHROME ENV
# =========================================================

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# =========================================================
# PYTHON REQUIREMENTS
# =========================================================

COPY app/requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# =========================================================
# PROJECT FILES
# =========================================================

COPY app/ .

# =========================================================
# BROWSER PROFILE STORAGE
# =========================================================

RUN mkdir -p /app/browser_profiles

# =========================================================
# PORT
# =========================================================

EXPOSE 8000