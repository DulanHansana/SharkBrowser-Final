FROM debian:bullseye-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libxrandr2 \
    xdg-utils \
    wget \
    curl \
    unzip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Run Chrome as non-root
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome && \
    mkdir -p /home/chrome && chown -R chrome:chrome /home/chrome

USER chrome
WORKDIR /home/chrome

# Expose CDP port
EXPOSE 9222

# Default command: headless Chromium with CDP
CMD ["chromium", \
    "--headless", \
    "--no-sandbox", \
    "--disable-gpu", \
    "--remote-debugging-address=0.0.0.0", \
    "--remote-debugging-port=9222"]
