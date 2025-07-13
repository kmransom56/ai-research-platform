# Adding a New Application to the AI-Research Platform

This short guide shows how to integrate **any containerised app** (e.g. n8n, Prompt-Forge, Grafana) with one command while avoiding host-port clashes.

---
## 1. Overview of the automation pipeline

| Step | What happens | File/script touched |
|------|--------------|---------------------|
| `add-application.sh` | • Finds a free host port in **11000-12000** when `--port auto` or omitted  <br>• Adds an *nginx* `location` that proxies the chosen port  <br>• Injects a **Docker Compose** service into `configs/docker-compose/docker-compose-full-stack.yml`  <br>• Adds a card + quick-link in **applications.html**  <br>• Adds a button in **control-panel.html**  <br>• Updates the port documentation markdown | scripts/platform-management/add-application.sh |
| `create-html-symlinks.sh` | Keeps `webapp/public/*.html` & `webapp/build/*.html` as symlinks to the authoritative copies in `webapi/wwwroot/`. | scripts/platform-management/create-html-symlinks.sh |
| Nginx reload | New proxy path goes live (`systemctl reload nginx`). | /etc/nginx/sites-available/ai-hub.conf |

---
## 2. Quick-start example – n8n

```bash
# One-liner (auto-assigns host port, adds everything)
./scripts/platform-management/add-application.sh \
  --name "n8n" \
  --port auto \
  --path "/n8n" \
  --description "Low-code automation engine" \
  --docker-image "docker.n8n.io/n8nio/n8n" \
  --docker-env "  -v n8n_data:/home/node/.n8n"
```
The script prints the assigned port (e.g. **11011**) and shows what it added.

Start the container and reload nginx:
```bash
docker compose -f configs/docker-compose/docker-compose-full-stack.yml up -d n8n
sudo systemctl reload nginx
```
Access the app:
* External (via gateway): `https://<tailscale-domain>:8443/n8n/`
* Direct (host): `http://localhost:11011/`

---
## 3. Prompt-Forge example

```bash
./add-application.sh \
  --name "PromptForge" \
  --port auto \
  --path "/promptforge" \
  --description "Prompt-Forge playground" \
  --docker-image "ghcr.io/insaanimanav/prompt-forge:main" \
  --docker-env "  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
```
Script might choose **11012** and map `11012:8080` automatically.

---
## 4. Flags reference

| Flag | Meaning |
|------|---------|
| `--port auto` or omit | Scan 11000-12000 and pick the first free host port. |
| `--docker-image` | Container image to run. |
| `--path auto` or omit | Build a unique `/your-app-name/` path; if the base path exists adds `-2`, `-3`, … |
| `--docker-env` | Literal YAML added under `