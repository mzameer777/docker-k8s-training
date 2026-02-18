# Module 4: ConfigMaps & Secrets (~45 min)

## Why Externalize Configuration?

Hardcoding config in images means rebuilding for every environment. ConfigMaps and Secrets decouple configuration from images.

| Resource      | Purpose                        | Encoded?     |
| ------------- | ------------------------------ | ------------ |
| **ConfigMap** | Non-sensitive configuration    | Plain text   |
| **Secret**    | Sensitive data (passwords, keys)| Base64       |

---

## Demo 1: ConfigMap from Literal Values

```bash
# Create a ConfigMap imperatively
kubectl create configmap app-config \
  --from-literal=APP_VERSION=2.0.0 \
  --from-literal=ENVIRONMENT=staging \
  --from-literal=LOG_LEVEL=info

# View it
kubectl get configmap app-config
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml
```

---

## Demo 2: ConfigMap from YAML

`configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: task-api-config
data:
  APP_VERSION: "3.0.0"
  ENVIRONMENT: "production"
  LOG_LEVEL: "warning"
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
```

```bash
kubectl apply -f configmap.yaml
kubectl get cm task-api-config -o yaml
```

---

## Demo 3: Using ConfigMaps in Pods

### Option A: Environment Variables

`pod-env-configmap.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-env-demo
spec:
  containers:
    - name: api
      image: alpine
      command: ["sh", "-c", "env | grep -E 'APP_|ENVIRONMENT|LOG_|DB_' && sleep 3600"]
      envFrom:
        - configMapRef:
            name: task-api-config    # All keys become env vars
```

```bash
kubectl apply -f pod-env-configmap.yaml
kubectl logs api-env-demo
# Output shows all ConfigMap keys as environment variables

kubectl delete pod api-env-demo
```

### Option B: Select Specific Keys

`pod-env-selective.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-selective-demo
spec:
  containers:
    - name: api
      image: alpine
      command: ["sh", "-c", "echo Version=$VERSION Env=$ENV && sleep 3600"]
      env:
        - name: VERSION
          valueFrom:
            configMapKeyRef:
              name: task-api-config
              key: APP_VERSION
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: task-api-config
              key: ENVIRONMENT
```

### Option C: Mount as Volume (File)

`configmap-file.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        location / {
            return 200 'Hello from ConfigMap!\n';
            add_header Content-Type text/plain;
        }
    }
```

`pod-volume-configmap.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-config-demo
spec:
  containers:
    - name: nginx
      image: nginx:1.25
      ports:
        - containerPort: 80
      volumeMounts:
        - name: config-volume
          mountPath: /etc/nginx/conf.d
  volumes:
    - name: config-volume
      configMap:
        name: nginx-config
```

```bash
kubectl apply -f configmap-file.yaml
kubectl apply -f pod-volume-configmap.yaml

kubectl port-forward pod/nginx-config-demo 8080:80
curl http://localhost:8080
# Output: Hello from ConfigMap!

kubectl delete pod nginx-config-demo
```

---

## Demo 4: Secrets

```bash
# Create a Secret imperatively
kubectl create secret generic db-credentials \
  --from-literal=DB_USER=admin \
  --from-literal=DB_PASSWORD=supersecret123

# View it (values are base64 encoded)
kubectl get secret db-credentials -o yaml

# Decode a value
kubectl get secret db-credentials -o jsonpath='{.data.DB_PASSWORD}' | base64 -d
```

### Secret from YAML

`secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
type: Opaque
data:
  # Values must be base64 encoded
  # echo -n 'admin' | base64 → YWRtaW4=
  # echo -n 'p@ssw0rd!' | base64 → cEBzc3cwcmQh
  DB_USER: YWRtaW4=
  DB_PASSWORD: cEBzc3cwcmQh
---
# Alternative: use stringData (plain text, encoded automatically)
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets-easy
type: Opaque
stringData:
  DB_USER: admin
  DB_PASSWORD: "p@ssw0rd!"
  API_KEY: "my-secret-api-key"
```

```bash
kubectl apply -f secret.yaml
kubectl get secrets
```

---

## Demo 5: Using Secrets in Pods

`pod-secret.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-demo
spec:
  containers:
    - name: api
      image: alpine
      command: ["sh", "-c", "echo User=$DB_USER Pass=$DB_PASSWORD && sleep 3600"]
      env:
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: api-secrets-easy
              key: DB_USER
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: api-secrets-easy
              key: DB_PASSWORD
```

```bash
kubectl apply -f pod-secret.yaml
kubectl logs secret-demo
# Output: User=admin Pass=p@ssw0rd!

kubectl delete pod secret-demo
```

---

## Demo 6: ConfigMap + Secret Together in a Deployment

`deployment-config.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api-configured
spec:
  replicas: 2
  selector:
    matchLabels:
      app: task-api-configured
  template:
    metadata:
      labels:
        app: task-api-configured
    spec:
      containers:
        - name: api
          image: alpine
          command: ["sh", "-c", "env | sort && sleep 3600"]
          envFrom:
            - configMapRef:
                name: task-api-config     # Non-sensitive config
            - secretRef:
                name: api-secrets-easy    # Sensitive config
```

```bash
kubectl apply -f deployment-config.yaml
kubectl logs -l app=task-api-configured | head -20
```

---

## Clean Up

```bash
kubectl delete -f deployment-config.yaml
kubectl delete configmap app-config task-api-config nginx-config
kubectl delete secret db-credentials api-secrets api-secrets-easy
```

---

## Exercises for Participants

1. Create a ConfigMap with your app's config and inject it as environment variables
2. Create a Secret for database credentials and mount it in a pod
3. Mount a ConfigMap as a file (e.g., a custom nginx config)
4. Create a deployment that uses both a ConfigMap and a Secret
