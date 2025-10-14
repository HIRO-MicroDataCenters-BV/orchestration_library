{{- define "alerts-populator.natsTopics" -}}
{{- if kindIs "slice" .Values.env.NATS_TOPICS -}}{{ join "," .Values.env.NATS_TOPICS }}{{- else -}}{{ .Values.env.NATS_TOPICS }}{{- end -}}
{{- end }}