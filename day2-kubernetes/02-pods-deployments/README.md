# Module 2: Deployments & ReplicaSets (~1.5 hours)

## Why Not Just Pods?

Bare pods don't self-heal. If a pod crashes or a node fails, the pod is **gone**. Deployments manage pods for you:

- Maintain a desired number of replicas
- Roll out updates with zero downtime
- Roll back if something goes wrong
- Scale up or down easily

```
Deployment → manages → ReplicaSet → manages → Pods
```

---

## Demo 1: Create a Deployment

`deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api
  labels:
    app: task-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-api
  template:
    metadata:
      labels:
        app: task-api
    spec:
      containers:
        - name: api
          image: nginx:1.25
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "250m"
```

```bash
# Create the deployment
kubectl apply -f deployment.yaml

# Watch pods come up
kubectl get pods -w

# View the deployment
kubectl get deployment task-api
kubectl describe deployment task-api

# View the ReplicaSet (created automatically)
kubectl get replicaset
kubectl describe rs  # rs = replicaset shorthand
```

---

## Demo 2: Self-Healing

```bash
# List pods
kubectl get pods

# Delete one pod — watch it get replaced!
kubectl delete pod <POD_NAME>

# Immediately check — a new pod is being created
kubectl get pods

# The deployment always maintains 3 replicas
kubectl get deployment task-api
```

---

## Demo 3: Scaling

```bash
# Scale up to 5 replicas
kubectl scale deployment task-api --replicas=5
kubectl get pods

# Scale down to 2
kubectl scale deployment task-api --replicas=2
kubectl get pods

# Declarative: edit the YAML and re-apply
# Change replicas: 3 in deployment.yaml, then:
kubectl apply -f deployment.yaml
```

---

## Demo 4: Rolling Updates

```bash
# Current state
kubectl get deployment task-api -o wide

# Update the image (from nginx:1.25 to nginx:1.26)
kubectl set image deployment/task-api api=nginx:1.26

# Watch the rolling update happen
kubectl rollout status deployment/task-api

# Pods are replaced gradually (old pods terminate as new ones become ready)
kubectl get pods -w

# View rollout history
kubectl rollout history deployment/task-api
```

---

## Demo 5: Rollback

```bash
# Deploy a BAD image (this will fail to start)
kubectl set image deployment/task-api api=nginx:nonexistent

# Watch it struggle
kubectl rollout status deployment/task-api
# Ctrl+C after a moment

kubectl get pods  # Some pods in ImagePullBackOff

# Rollback to the previous version
kubectl rollout undo deployment/task-api

# Verify it's healthy again
kubectl rollout status deployment/task-api
kubectl get pods

# Rollback to a specific revision
kubectl rollout history deployment/task-api
kubectl rollout undo deployment/task-api --to-revision=1
```

---

## Demo 6: Deployment Strategy

### RollingUpdate (Default)

`deployment-rolling.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-demo
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max pods ABOVE desired count during update
      maxUnavailable: 1   # Max pods that can be unavailable during update
  selector:
    matchLabels:
      app: rolling-demo
  template:
    metadata:
      labels:
        app: rolling-demo
    spec:
      containers:
        - name: app
          image: nginx:1.25
          ports:
            - containerPort: 80
```

### Recreate (All-at-once)

`deployment-recreate.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recreate-demo
spec:
  replicas: 4
  strategy:
    type: Recreate   # Kill all old pods, then create new ones
  selector:
    matchLabels:
      app: recreate-demo
  template:
    metadata:
      labels:
        app: recreate-demo
    spec:
      containers:
        - name: app
          image: nginx:1.25
          ports:
            - containerPort: 80
```

```bash
# Deploy both
kubectl apply -f deployment-rolling.yaml
kubectl apply -f deployment-recreate.yaml

# Update rolling — pods replaced gradually
kubectl set image deployment/rolling-demo app=nginx:1.26
kubectl get pods -l app=rolling-demo -w

# Update recreate — all pods killed, then new ones created
kubectl set image deployment/recreate-demo app=nginx:1.26
kubectl get pods -l app=recreate-demo -w

# Clean up
kubectl delete -f deployment-rolling.yaml -f deployment-recreate.yaml
```

---

## Demo 7: Liveness and Readiness Probes

`deployment-probes.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: probes-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: probes-demo
  template:
    metadata:
      labels:
        app: probes-demo
    spec:
      containers:
        - name: app
          image: nginx:1.25
          ports:
            - containerPort: 80
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 3
            periodSeconds: 5
            failureThreshold: 3
```

```bash
kubectl apply -f deployment-probes.yaml

# View probe status
kubectl describe pod -l app=probes-demo

# Probes in action:
# - Liveness: If it fails 3 times, the container is RESTARTED
# - Readiness: If it fails, the pod is removed from Service endpoints

kubectl delete -f deployment-probes.yaml
```

**Probe Types:**

| Probe         | Purpose                                           |
| ------------- | ------------------------------------------------- |
| `liveness`    | Is the container alive? If not, restart it         |
| `readiness`   | Is the container ready for traffic? If not, remove from Service |
| `startup`     | Is the container still starting? Disables liveness check until ready |

---

## Exercises for Participants

1. Create a deployment with 3 replicas, then scale to 5
2. Perform a rolling update and watch the pods replace one by one
3. Deploy a bad image, then rollback to the previous version
4. Add liveness and readiness probes to a deployment
5. Compare RollingUpdate vs Recreate strategies

---

## Quick Reference

```bash
kubectl apply -f deployment.yaml                  # Create/update
kubectl get deployments                            # List deployments
kubectl describe deployment NAME                   # Details
kubectl scale deployment NAME --replicas=N         # Scale
kubectl set image deployment/NAME CONTAINER=IMAGE  # Update image
kubectl rollout status deployment/NAME             # Watch rollout
kubectl rollout history deployment/NAME            # View history
kubectl rollout undo deployment/NAME               # Rollback
kubectl rollout undo deployment/NAME --to-revision=N  # Rollback to specific
```
