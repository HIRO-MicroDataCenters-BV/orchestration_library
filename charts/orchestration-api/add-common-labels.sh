#!/usr/bin/env bash
# helm:postrenderer:v1

set -eo pipefail

RELEASE_NAME="${RELEASE_NAME:-aces-orchestration-api}"

# Read all rendered manifests from Helm via stdin
input=$(cat)

# Process using yq and output to stdout
echo "$input" | yq eval "
  (select(.kind == \"Deployment\" 
       or .kind == \"StatefulSet\" 
       or .kind == \"DaemonSet\" 
       or .kind == \"Job\" 
       or .kind == \"CronJob\")
    .spec.template.metadata.labels) |= (
      (. // {}) * {
        \"app.kubernetes.io/name\": (.\"app.kubernetes.io/name\" // \"$RELEASE_NAME\"),
        \"app.kubernetes.io/instance\": (.\"app.kubernetes.io/instance\" // \"$RELEASE_NAME\"),
        \"app.kubernetes.io/managed-by\": (.\"app.kubernetes.io/managed-by\" // \"$RELEASE_NAME\"),
        \"app.kubernetes.io/part-of\": (.\"app.kubernetes.io/part-of\" // \"$RELEASE_NAME\"),
        \"aces-component-name\": (.\"aces-component-name\" // \"$RELEASE_NAME\")
      }
  )
" -
