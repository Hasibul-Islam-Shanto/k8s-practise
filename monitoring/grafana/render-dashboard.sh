#!/bin/sh
# Grafana 13 does not ship envsubst. Fill dashboard placeholders with sed.
set -eu

: "${APP_JOB_NAME:?Set APP_JOB_NAME}"
: "${APP_COMPOSE_PROJECT:?Set APP_COMPOSE_PROJECT}"
: "${APP_HTTP_REQUESTS_METRIC:?Set APP_HTTP_REQUESTS_METRIC}"
: "${APP_HTTP_DURATION_BUCKET_METRIC:?Set APP_HTTP_DURATION_BUCKET_METRIC}"
: "${APP_PROCESS_MEMORY_METRIC:?Set APP_PROCESS_MEMORY_METRIC}"
: "${APP_ROUTE_FILTER:?Set APP_ROUTE_FILTER}"
: "${APP_DISPLAY_NAME:?Set APP_DISPLAY_NAME}"
: "${DASHBOARD_TITLE:?Set DASHBOARD_TITLE}"
: "${DASHBOARD_UID:?Set DASHBOARD_UID}"

mkdir -p /tmp/dashboards
sed \
  -e "s#\\\${APP_JOB_NAME}#${APP_JOB_NAME}#g" \
  -e "s#\\\${APP_COMPOSE_PROJECT}#${APP_COMPOSE_PROJECT}#g" \
  -e "s#\\\${APP_HTTP_REQUESTS_METRIC}#${APP_HTTP_REQUESTS_METRIC}#g" \
  -e "s#\\\${APP_HTTP_DURATION_BUCKET_METRIC}#${APP_HTTP_DURATION_BUCKET_METRIC}#g" \
  -e "s#\\\${APP_PROCESS_MEMORY_METRIC}#${APP_PROCESS_MEMORY_METRIC}#g" \
  -e "s#\\\${APP_ROUTE_FILTER}#${APP_ROUTE_FILTER}#g" \
  -e "s#\\\${APP_DISPLAY_NAME}#${APP_DISPLAY_NAME}#g" \
  -e "s#\\\${DASHBOARD_TITLE}#${DASHBOARD_TITLE}#g" \
  -e "s#\\\${DASHBOARD_UID}#${DASHBOARD_UID}#g" \
  /etc/grafana/dashboard-templates/incident-observability.json \
  > /tmp/dashboards/incident-observability.json

exec /run.sh
