{{- define "k8s-dashboard.nginxConfChecksum" -}}
{{ include (print $.Template.BasePath "/nginx-configmap.yaml") . | sha256sum }}
{{- end -}}
