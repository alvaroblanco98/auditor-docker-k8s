# Auditor de Seguridad para Docker y Kubernetes

Proyecto de Trabajo de Fin de Máster de Formación Permanente en Ciberseguridad y Seguridad de la Información (UCLM)

## Descripción

Esta aplicación permite a los usuarios subir archivos de configuración (Dockerfile, docker-compose.yml o manifiestos de Kubernetes)
y recibir un análisis de seguridad automatizado que incluye:

- Detección de vulnerabilidades.
- Identificación de CVEs asociados.
- Sugerencias de remediación.
- Visualización comparativa entre configuración original y recomendada.

El objetivo es mejorar la seguridad y cumplimiento de buenas prácticas en entornos de contenedores.

## Stack tecnológico

- **Frontend**: React + Typescript + TailwindCSS
- **Backend**: FastAPI
- **Herraminetas de análisis**:
    - [hadolint](https://github.com/hadolint/hadolint) (Dockerfile)
    - [trivy](https://github.com/aquasecurity/trivy) (análisis de imágenes)
    - [kube-linter](https://github.com/stackrox/kube-linter) (Kubernetes)
    - [dclint](https://github.com/zavoloklom/docker-compose-linter) (docker-compose) 

## Funcionalidades

    - Subida de archivos de configuración.
    - Análisis de seguridad con múltiples herramientas.
    - Normalización de resultados.
    - Remediación.
    - Comparación visual entre archivo original y sugerido.
    - Exportación de resultados.
    - Histórico de análisis previos.

## Instalación y ejecución

- **Requisitos**:

    - [Docker](https://docs.docker.com/engine/install/)
    - [docker-compose](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually)

- **Pasos**:
    - Clonar repositorio:
        - git clone https://github.com/alvaroblanco98/auditor-docker-k8s.git
        - cd auditor-docker-k8s
    - Construir y levantar los contenedores:
        - docker compose up --build
    - Acceder al dashboard:
        - http://localhost:3000

## Estructura del proyecto

```text
AUDITOR-DOCKER-K8S
├── backend/
│   ├── app/
│   │   ├── main.py                   # Punto de entrada FastAPI
│   │   ├── routers/
│   │   │   ├── scan.py               # Endpoint de análisis
│   │   │   └── history.py            # Endpoint para historial
│   │   ├── utils/
│   │   │   ├── parsers.py            # Normalización de resultados
│   │   │   ├── suggestions.py        # Remediaciones sugeridas
│   │   │   └── storage.py            # Persistencia en JSON
│   ├── Dockerfile                    # Dockerfile del backend
│   └── requirements.txt              # Dependencias de Python
├── frontend/
│   ├── Dockerfile                    # Dockerfile del frontend React
│   ├── package.json                  # Dependencias y scripts de React
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.tsx                   # Componente principal del dashboard
│       └── index.tsx                 # Punto de entrada React
├── inputs/
│   ├── Dockerfile.insecure           # Dockerfile vulnerable para pruebas
│   ├── docker-compose.yaml           # Ejemplo docker-compose vulnerable
│   └── deployment.yaml               # Manifiesto de Kubernetes
├── docker-compose.yml               # Orquestador de backend + frontend
├── .gitignore
├── LICENSE
└── 
```