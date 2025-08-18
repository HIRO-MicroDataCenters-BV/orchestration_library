#!/bin/bash
yq eval '
(select(.kind == "Deployment" or .kind == "StatefulSet" or .kind == "DaemonSet" or .kind == "Job" or .kind == "CronJob")
  .spec.template.metadata.labels) |= (
    (. // {}) * {
      "app.kubernetes.io/name": (.["app.kubernetes.io/name"] // "aces-orchestration-api"),
      "app.kubernetes.io/instance": (.["app.kubernetes.io/instance"] // "aces-orchestration-api"),
      "app.kubernetes.io/managed-by": (.["app.kubernetes.io/managed-by"] // "Helm"),
      "app.kubernetes.io/part-of": (.["app.kubernetes.io/part-of"] // "aces-orchestration-api"),
      "app.kubernetes.io/aces-service-name": (.["app.kubernetes.io/aces-service-name"] // "aces-orchestration-api")
    }
)
' -
