apiVersion: v1
kind: Pod
metadata:
  name: my-sample-pod
  labels:
    app: my-app
    environment: development
spec:
  containers:
  - name: nginx-container
    image: nginx:latest
    ports:
    - containerPort: 80
  - name: busybox-container
    image: busybox
    command: ["sh", "-c", "echo Hello from BusyBox; sleep 3600"]