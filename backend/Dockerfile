FROM python:3.11-slim

WORKDIR /app

# Instalar herramientas: Node.js 20.x manual + hadolint + trivy + dclint
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    lsb-release \
    git \
    xz-utils \
    # instalar Node.js 20.x (binario)
 && curl -fsSL https://nodejs.org/dist/v20.19.0/node-v20.19.0-linux-x64.tar.xz -o node.tar.xz \
 && tar -xf node.tar.xz -C /usr/local --strip-components=1 \
 && rm node.tar.xz \
 # verificar que node y npm están disponibles
 && node -v && npm -v \
 # instalar hadolint
 && wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 \
 && chmod +x /usr/local/bin/hadolint \
 # instalar trivy
 && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
 # instalar dclint
 && npm install -g dclint \
 # instalar kube-linter
 && curl -sSL https://github.com/stackrox/kube-linter/releases/latest/download/kube-linter-linux.tar.gz | tar -xz -C /usr/local/bin kube-linter \
 && chmod +x /usr/local/bin/kube-linter \
 # limpieza
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
