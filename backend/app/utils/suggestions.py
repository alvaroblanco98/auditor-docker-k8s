import re
import yaml

def suggest_remediations_dockerfile(content: str) -> str:
    """
    Genera sugerencias de remediación para ficheros Dockerfile.

    Reglas implementadas:
    - Evitar uso de la etiqueta latest en FROM y reemplazar por <TAG>.
    - Evitar uso de USER root y reemplazar por `USER appuser.
    - Recomendar usar COPY en lugar de ADD (si no se necesita funcionalidad avanzada).
    - Evitar apt-get upgrade para garantizar imágenes reproducibles.
    - Añadir USER no root si no está presente.
    - Añadir WORKDIR explícito si no está presente.
    - Añadir HEALTHCHECK si no está definido.

    Args:
        content (str): Contenido del Dockerfile en texto plano.

    Returns:
        str: Contenido modificado con sugerencias comentadas.
    """

    lines = content.splitlines()
    suggested = []
    has_user = any(line.strip().startswith("USER") for line in lines)
    has_workdir = any(line.strip().startswith("WORKDIR") for line in lines)
    has_healthcheck = any(line.strip().startswith("HEALTHCHECK") for line in lines)

    for line in lines:
        stripped = line.strip()
     
        if stripped.startswith("FROM") and ":latest" in stripped:
            new_line = re.sub(r':latest', ':<TAG>', line)
            suggested.append("# SUGERENCIA: evita usar 'latest'")
            suggested.append(new_line)
            continue

        if stripped.startswith("USER") and "root" in stripped:
            suggested.append("# SUGERENCIA: evita usar 'root'")
            suggested.append("USER appuser")
            continue


        if stripped.startswith("ADD "):
            suggested.append("# SUGERENCIA: reemplaza ADD por COPY si no necesitas funcionalidades avanzadas")
            suggested.append(line.replace("ADD", "COPY", 1))
            continue

        if "apt-get upgrade" in stripped:
            suggested.append("# SUGERENCIA: evita 'apt-get upgrade', genera imágenes reproducibles")
            suggested.append(f"# {line}")
            continue

        suggested.append(line)

    if not has_user:
        suggested.append("# SUGERENCIA: añade un usuario no root")
        suggested.append("USER appuser")

    if not has_workdir:
        suggested.append("# SUGERENCIA: define un directorio de trabajo explícito")
        suggested.append("WORKDIR /app")

    if not has_healthcheck:
        suggested.append("# SUGERENCIA: considera añadir un HEALTHCHECK")
        suggested.append("HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1")

    return "\n".join(suggested)

def suggest_remediations_docker_compose(content: str) -> str:
    """
    Genera sugerencias de remediaciones para un archivo docker-compose.yaml.

    Reglas implementadas:
    - Evitar :latest en imágenes y reemplazar por <TAG>.
    - Añadir restart: unless-stopped si no está definido.
    - Añadir read_only: true si no está definido.
    - Añadir usuario no root (user: 1000:1000) si no está definido.
    - Definir límites y reservas de recursos si no existen.

    Args:
        content (str): Contenido del docker-compose.yaml.

    Returns:
        str: Contenido modificado con sugerencias aplicadas.
    """

    try:
        parsed = yaml.safe_load(content)
    except Exception:
        return content

    if not isinstance(parsed, dict):
        return content

    services = parsed.get("services", {})
    for service in services.items():
        
        image = service.get("image", "")
        if ":latest" in image:
            service["image"] = image.replace(":latest", ":<TAG>")
            service.setdefault("x-suggestions", []).append("Evita usar latest, usa una versión fija.")

        if "restart" not in service:
            service["restart"] = "unless-stopped"

        if "read_only" not in service:
            service["read_only"] = True

        if "user" not in service:
            service["user"] = "1000:1000"

        deploy_cfg = service.get("deploy", {})
        if "resources" not in deploy_cfg:
            deploy_cfg["resources"] = {
                "limits": {"cpus": "0.50", "memory": "256M"},
                "reservations": {"cpus": "0.25", "memory": "128M"}
            }
        service["deploy"] = deploy_cfg

    parsed["services"] = services
    return yaml.dump(parsed, default_flow_style=False)



def suggest_remediations_kubernetes_yaml(content: str) -> str:
    """
    Genera sugerencias de remediaciones para manifiestos Kubernetes.

    Reglas implementadas:
    - Añadir readOnlyRootFilesystem: true si no está presente.
    - Añadir runAsNonRoot: true si no está presente.
    - Añadir allowPrivilegeEscalation: false si no está presente.
    - Definir límites y requests de CPU y memoria si no existen.

    Args:
        content (str): Contenido YAML de Kubernetes.

    Returns:
        str: Contenido modificado con sugerencias aplicadas.
    """

    try:
        parsed = list(yaml.safe_load_all(content))
    except Exception:
        return content

    for doc in parsed:
        if not isinstance(doc, dict):
            continue

        spec = doc.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        containers = pod_spec.get("containers", [])

        for container in containers:
            sc = container.get("securityContext", {})

            if "readOnlyRootFilesystem" not in sc:
                sc["readOnlyRootFilesystem"] = True
            if "runAsNonRoot" not in sc:
                sc["runAsNonRoot"] = True
            if "allowPrivilegeEscalation" not in sc:
                sc["allowPrivilegeEscalation"] = False

            container["securityContext"] = sc

            if "resources" not in container:
                container["resources"] = {
                    "limits": {"cpu": "500m", "memory": "256Mi"},
                    "requests": {"cpu": "250m", "memory": "128Mi"}
                }

        template["spec"] = pod_spec
        spec["template"] = template
        doc["spec"] = spec

    return yaml.dump_all(parsed, default_flow_style=False)