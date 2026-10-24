# Monitoring stack

Prometheus, Grafana, Loki, Alloy, Node Exporter, and cAdvisor run as their own Compose project. They watch a Docker Compose app on the same machine through one shared Docker network.

## How data reaches Grafana

Two paths run side by side. Metrics go through Prometheus. Logs go through Alloy and Loki. Grafana is the only place you read both.

![Metrics and logs flowing into Grafana](architecture.png)

**Metrics.** The backend API, Node Exporter, and cAdvisor each expose a metrics endpoint. Prometheus scrapes all three on a schedule. The backend job is the application (`APP_METRICS_TARGET` in `.env.monitoring`). Node Exporter is host CPU and memory. cAdvisor is per-container CPU and memory. Grafana queries Prometheus with PromQL and draws those series on the dashboard.

**Logs.** Every container writes stdout and stderr. Those lines are the Docker container logs. Grafana Alloy tails them through the Docker socket, adds `compose_project` and `compose_service`, and forwards the stream to Loki. Grafana queries Loki with LogQL. The app does not run its own log shipper.

| Service | What it does | Where to open it |
|---|---|---|
| Grafana | Dashboards | http://localhost:3000 |
| Prometheus | Metrics | http://127.0.0.1:9090 |
| Loki | Log storage | http://127.0.0.1:3100 |
| Alloy | Ships container logs to Loki | http://127.0.0.1:12345 |
| Node Exporter | Host CPU and memory | scraped by Prometheus |
| cAdvisor | Container CPU and memory | scraped by Prometheus |

Grafana is the page you use. Prometheus, Loki, and Alloy stay on localhost.

Use `compose.monitoring.yaml` on Linux and Ubuntu, including EC2. Use `compose.monitoring.mac.yaml` on Docker Desktop for Mac. The Mac file changes the host mounts that Node Exporter and cAdvisor need. On a Mac those two report the Docker Desktop Linux VM, not macOS itself.

Start the application before this stack. This lab's app lives in the parent directory and joins the network `incident-observability`. Full application setup is in `README(EC2 Deployment).md` at the repo root.

## Getting started

From this `monitoring/` directory.

### 1. Create the shared network

Prometheus reaches the app by Docker DNS. Create the network once. Skip this if it already exists.

```bash
docker network create incident-observability
```

The name must match `OBSERVABILITY_NETWORK` in `.env.monitoring`. The app metrics service must join that same network. This lab's backend does that in the parent `compose.yaml`.

### 2. Create the env file

```bash
cp .env.monitoring.example .env.monitoring
```

Set a Grafana password before you open port 3000:

```env
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=choose-a-password
```

The other keys already match this lab (`backend:5000`, job `incident-backend`, Compose project `incident-app`). Leave them unless you are pointing the stack at a different app. Each key has a comment in `.env.monitoring.example`.

### 3. Start the stack

Linux / Ubuntu / EC2:

```bash
docker compose --env-file .env.monitoring -f compose.monitoring.yaml config
docker compose --env-file .env.monitoring -f compose.monitoring.yaml up -d
docker compose --env-file .env.monitoring -f compose.monitoring.yaml ps
```

Mac / Docker Desktop:

```bash
docker compose --env-file .env.monitoring -f compose.monitoring.mac.yaml config
docker compose --env-file .env.monitoring -f compose.monitoring.mac.yaml up -d
docker compose --env-file .env.monitoring -f compose.monitoring.mac.yaml ps
```

`config` only prints the resolved file. `up -d` starts the containers. You do not build images.

You should see `prometheus`, `grafana`, `loki`, `alloy`, `node-exporter`, and `cadvisor`.

### 4. Open Grafana and Prometheus

Grafana: http://localhost:3000

Sign in with `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`. The dashboard is in the `bongoDev` folder: **bongoDev Incident App Observability**. Provisioning loads it about 30 seconds after Grafana starts. Refresh the page if the folder is empty on the first load.

Prometheus targets: http://127.0.0.1:9090/targets

`incident-backend`, `node-exporter`, `cadvisor`, and `prometheus` should be `UP`. A backend target stays down until the app is running and attached to `incident-observability`.

In Prometheus, this confirms the app scrape:

```promql
up{job="incident-backend"}
```

A value of `1` means the target is up. After the app has served some `/api` traffic:

```promql
sum(rate(incident_http_requests_total[1m]))
```

Logs in Grafana go to **Explore**, choose the Loki datasource, and run:

```logql
{compose_project="incident-app"}
```

Backend logs only:

```logql
{compose_project="incident-app", compose_service="backend"}
```

`compose_project` is the `name:` at the top of the application Compose file. `compose_service` is the Compose service name. Alloy adds both from the Docker socket. The app does not need a log agent.

### 5. Stop or restart

Linux:

```bash
docker compose --env-file .env.monitoring -f compose.monitoring.yaml down
docker compose --env-file .env.monitoring -f compose.monitoring.yaml up -d
```

Mac:

```bash
docker compose --env-file .env.monitoring -f compose.monitoring.mac.yaml down
docker compose --env-file .env.monitoring -f compose.monitoring.mac.yaml up -d
```

`down` stops containers and keeps the Prometheus, Loki, and Grafana volumes. After you change `.env.monitoring`, run `up -d` again so Prometheus and Grafana re-render their configs.

## Reuse this folder with another app

Copy `monitoring/`, edit `.env.monitoring`, and start the stack again. You do not rebuild images.

One running copy scrapes one application job from the env file. To scrape another app at the same time, copy the app job in `prometheus/prometheus.yml.template` and put literal values in the copy. Only the first job is filled from `.env.monitoring`.

Values substituted into YAML and JSON must be simple tokens: letters, numbers, `.`, `_`, `-`, `:`, and `/`. Do not use spaces, quotes, or `#` in scrape targets, job names, metric names, or the route filter. `DASHBOARD_TITLE`, `APP_DISPLAY_NAME`, `GRAFANA_FOLDER`, and `GRAFANA_DASHBOARD_PROVIDER` may contain spaces; quote those values in `.env.monitoring`.

### What to change

| Key | This lab | Must match |
|---|---|---|
| `OBSERVABILITY_NETWORK` | `incident-observability` | External Docker network name. Create it once with `docker network create`. The app metrics service joins a network with this name. |
| `MONITORING_COMPOSE_NAME` | `incident-observability` | Compose project name of this stack. Changing it creates new volumes. |
| `APP_JOB_NAME` | `incident-backend` | Prometheus `job` label. Dashboard queries use the same value. |
| `APP_METRICS_PATH` | `/metrics` | Path the app serves Prometheus text on. |
| `APP_METRICS_TARGET` | `backend:5000` | `<compose-service-name>:<port>` on `OBSERVABILITY_NETWORK`. |
| `APP_LABEL_APPLICATION` / `APP_LABEL_ENVIRONMENT` | `incident-management` / `lab` | Optional labels on the app, node-exporter, and cadvisor jobs. The shipped dashboard does not filter on them. |
| `APP_COMPOSE_PROJECT` | `incident-app` | `name:` at the top of the application Compose file. Used by container CPU, container memory, and the log panel. |
| `APP_HTTP_REQUESTS_METRIC` | `incident_http_requests_total` | Counter the app exports for HTTP requests. |
| `APP_HTTP_DURATION_BUCKET_METRIC` | `incident_http_request_duration_seconds_bucket` | Histogram bucket metric for latency. |
| `APP_PROCESS_MEMORY_METRIC` | `incident_backend_process_resident_memory_bytes` | Process RSS metric. This lab prefixes default Node.js metrics with `incident_backend_`. |
| `APP_ROUTE_FILTER` | `/api/.*` | Prometheus regex for the `route` label. |
| `APP_DISPLAY_NAME` | `Backend` | Short name in the status, process memory, and log panel titles. |
| `DASHBOARD_TITLE` / `DASHBOARD_UID` | `bongoDev Incident App Observability` / `bongodev-incident-observability` | Dashboard title and uid. Keep the uid stable to update the same dashboard. |
| `GRAFANA_FOLDER` / `GRAFANA_DASHBOARD_PROVIDER` | `bongoDev` / `bongoDev Incident Lab` | Folder and provider name in Grafana. |

The application Compose file is outside this folder. Its metrics service must still attach to `OBSERVABILITY_NETWORK`. This lab does that in `compose.yaml`:

```yaml
services:
  backend:
    networks:
      - app_internal
      - observability

networks:
  observability:
    external: true
    name: incident-observability
```

For another project, set `name` to the same value as `OBSERVABILITY_NETWORK`, and set `APP_METRICS_TARGET` to that service name and metrics port.

### Leave these files alone

| File | Why it already fits another project |
|---|---|
| `loki/loki-config.yml` | Local log storage. No app name in it. |
| `alloy/config.alloy` | Tails every container through the Docker socket and labels logs with `compose_project` and `compose_service`. |
| `grafana/provisioning/datasources/datasources.yaml` | Points Grafana at `http://prometheus:9090` and `http://loki:3100` on the private `monitoring` network. |
| `grafana/provisioning/dashboards/dashboards.yaml` | Loads the rendered JSON. Folder name comes from `GRAFANA_FOLDER`. |

Host panels in the dashboard (EC2 CPU and memory) also keep working, because they query `job="node-exporter"`.

Both Compose files read `OBSERVABILITY_NETWORK`. You do not edit the network name in the Compose files.

`prometheus/prometheus.yml.template` and `grafana/dashboards/incident-observability.json` keep placeholders and short comments. Edit `.env.monitoring` instead of those placeholders. Grafana renders the dashboard JSON when the container starts. Prometheus renders its config the same way.

### What the other application must provide

- A Prometheus metrics HTTP endpoint, on a port reachable from `OBSERVABILITY_NETWORK`.
- Structured or plain lines on stdout and stderr. Alloy ships container logs without an agent inside the app.
- Metric and label names set in `.env.monitoring`, or you change those keys to the names the app actually exports.

This lab's backend does that in `backend/src/server.js` with `prom-client`: `incident_http_requests_total`, `incident_http_request_duration_seconds`, and default process metrics prefixed `incident_backend_`. Request logs are one JSON line per request. `/metrics` and `/health` are not counted.

### Check the new app

In Prometheus (`http://127.0.0.1:9090/targets`) confirm the new job is `UP`. In Grafana Explore, confirm logs with the Compose project name from `APP_COMPOSE_PROJECT`:

```logql
{compose_project="your-compose-project-name"}
```
