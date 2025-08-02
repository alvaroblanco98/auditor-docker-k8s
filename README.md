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

### Requisitos

    - [Docker](https://docs.docker.com/engine/install/) y [docker-compose](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually) instalados.

### Pasos

1. Clonar repositorio:
git clone https://github.com/alvaroblanco98/auditor-docker-k8s.git
cd auditor-docker-k8s
2. Construir y levantar los contenedores:
docker compose up --build
3. Acceder al dashboard:
http://localhost:3000

## Estructura del proyecto

├── backend/
│ ├── app/
│ │ ├── main.py           # Punto de entrada FastAPI
│ │ ├── routers/
│ │ │ ├── scan.py         # Endpoint principal de análisis
│ │ │ └── history.py      # Endpoint para historial
│ │ ├── utils/
│ │ │ ├── parsers.py      # Normalización de resultados
│ │ │ ├── suggestions.py  # Generación de remediaciones sugeridas
│ │ │ └── storage.py      # Persistencia (JSON local)
│ ├── Dockerfile          # Docker backend
│ └── requirements.txt    # Dependencias Python
├── frontend/
│ ├── Dockerfile          # Docker frontend
│ ├── package.json        # Dependencias React
│ ├── public/
│ │ └── index.html
│ └── src/
│ ├── App.tsx             # Componente principal del dashboard
│ └── index.tsx           # Renderización React
├── inputs/
│ ├── Dockerfile.insecure # Ejemplo vulnerable (pruebas)
│ ├── docker-compose.yaml # Ejemplo de docker-compose
│ └── deployment.yaml     # Ejemplo de manifiesto K8s
├── docker-compose.yml    # Orquestador para backend + frontend
├── .gitignore
├── LICENSE
└── README.md
