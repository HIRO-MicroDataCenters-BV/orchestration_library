#!/bin/bash
RELEASE_NAME="$1"
yq eval "
  (select(.kind == \"Deployment\" or .kind == \"StatefulSet\" or .kind == \"DaemonSet\" or .kind == \"Job\" or .kind == \"CronJob\")
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
