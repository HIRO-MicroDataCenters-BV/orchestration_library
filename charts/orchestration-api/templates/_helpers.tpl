{{/*
Common labels
*/}}
{{- define "orchestration-api.commonLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/name: aces-orchestration-api
{{- end }}
