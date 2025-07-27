import re
import yaml

def suggest_remediations_dockerfile(content: str) -> str:
    lines = content.splitlines()
    suggested = []
    has_user = any(line.strip().startswith("USER") for line in lines)

    for line in lines:
        stripped = line.strip()

        # FROM imagen:latest → FROM imagen:<TAG>
        if stripped.startswith("FROM") and ":latest" in stripped:
            new_line = re.sub(r':latest', ':<TAG>', line)
            suggested.append(f"# SUGERENCIA: evita usar 'latest'\n{new_line}")
            continue

        # USER root → USER appuser
        if stripped.startswith("USER") and "root" in stripped:
            suggested.append(f"# SUGERENCIA: evita usar 'root'\nUSER appuser")
            continue

        suggested.append(line)

    # Si no hay ningún USER, añadir al final
    if not has_user:
        suggested.append("# SUGERENCIA: añade un usuario no root")
        suggested.append("USER appuser")

    return "\n".join(suggested)


def suggest_remediations_kubernetes_yaml(content: str) -> str:
    try:
        parsed = list(yaml.safe_load_all(content))
    except Exception:
        return content  # YAML no válido

    for doc in parsed:
        if not isinstance(doc, dict):
            continue
        spec = doc.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        containers = pod_spec.get("containers", [])

        for container in containers:
            sc = container.get("securityContext", {})
            # Añadir campos si no existen
            if "readOnlyRootFilesystem" not in sc:
                sc["readOnlyRootFilesystem"] = True
            if "runAsNonRoot" not in sc:
                sc["runAsNonRoot"] = True
            container["securityContext"] = sc

    return yaml.dump_all(parsed, default_flow_style=False)