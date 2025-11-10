{{- define "tuning-parameters-populator.natsTopics" -}}
{{- if kindIs "slice" .Values.env.NATS_TOPICS -}}{{ join "," .Values.env.NATS_TOPICS }}{{- else -}}{{ .Values.env.NATS_TOPICS }}{{- end -}}
{{- end }}

{{- define "tuning-parameters-populator.natsJSSubjects" -}}
{{- if kindIs "slice" .Values.env.NATS_JS_SUBJECTS -}}{{ join "," .Values.env.NATS_JS_SUBJECTS }}{{- else -}}{{ .Values.env.NATS_JS_SUBJECTS }}{{- end -}}
{{- end }}