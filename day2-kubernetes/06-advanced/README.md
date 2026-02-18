# Module 6: Advanced Kubernetes (~1.5 hours)

## Topics Covered

1. Resource Quotas & Limits
2. Horizontal Pod Autoscaler (HPA)
3. Jobs & CronJobs
4. RBAC (Role-Based Access Control)
5. Network Policies
6. Helm (Package Manager)

---

## Demo 1: Resource Quotas & LimitRanges

### LimitRange — Default limits for a namespace

`limitrange.yaml`:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
    - type: Container
      default:          # Default limits if not specified
        memory: "256Mi"
        cpu: "250m"
      defaultRequest:   # Default requests if not specified
        memory: "128Mi"
        cpu: "100m"
      max:
        memory: "1Gi"
        cpu: "1"
      min:
        memory: "64Mi"
        cpu: "50m"
```

### ResourceQuota — Cap total resources in a namespace

`resourcequota.yaml`:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
spec:
  hard:
    requests.cpu: "2"
    requests.memory: "2Gi"
    limits.cpu: "4"
    limits.memory: "4Gi"
    pods: "10"
    services: "5"
    persistentvolumeclaims: "5"
```

```bash
kubectl create namespace quota-demo
kubectl apply -f limitrange.yaml -n quota-demo
kubectl apply -f resourcequota.yaml -n quota-demo

# View quotas
kubectl get resourcequota -n quota-demo
kubectl describe resourcequota namespace-quota -n quota-demo

# Deploy a pod — gets default limits from LimitRange
kubectl run test --image=nginx -n quota-demo
kubectl describe pod test -n quota-demo  # Notice the limits

# Try to exceed quota (create many pods)
kubectl create deployment big-app --image=nginx --replicas=15 -n quota-demo
kubectl get events -n quota-demo  # See quota exceeded errors

kubectl delete namespace quota-demo
```

---

## Demo 2: Horizontal Pod Autoscaler (HPA)

`hpa-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hpa-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hpa-demo
  template:
    metadata:
      labels:
        app: hpa-demo
    spec:
      containers:
        - name: app
          image: nginx:1.25
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "200m"
              memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: hpa-demo
spec:
  selector:
    app: hpa-demo
  ports:
    - port: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hpa-demo
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hpa-demo
  minReplicas: 1
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

```bash
# Make sure metrics-server is running
# minikube: minikube addons enable metrics-server
# kind/Docker Desktop: install metrics-server

kubectl apply -f hpa-deployment.yaml

# Watch the HPA
kubectl get hpa hpa-demo -w

# Generate load (in another terminal)
kubectl run load-generator --rm -it --image=busybox --restart=Never -- \
  sh -c "while true; do wget -q -O- http://hpa-demo > /dev/null; done"

# Watch pods scale up
kubectl get pods -l app=hpa-demo -w

# Stop the load generator (Ctrl+C), pods scale back down after ~5 min

kubectl delete -f hpa-deployment.yaml
```

---

## Demo 3: Jobs & CronJobs

### Job — Run to completion

`job.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processor
spec:
  completions: 3       # Run 3 times total
  parallelism: 2       # Run 2 at a time
  backoffLimit: 3       # Retry up to 3 times on failure
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: processor
          image: alpine
          command: ["sh", "-c", "echo Processing batch $(date) && sleep 5 && echo Done!"]
```

```bash
kubectl apply -f job.yaml

# Watch pods complete
kubectl get pods -l job-name=data-processor -w
kubectl get jobs

# View logs
kubectl logs -l job-name=data-processor

kubectl delete job data-processor
```

### CronJob — Scheduled tasks

`cronjob.yaml`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "*/2 * * * *"    # Every 2 minutes
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: alpine
              command: ["sh", "-c", "echo 'Running backup at' $(date) && sleep 3 && echo 'Backup complete!'"]
```

```bash
kubectl apply -f cronjob.yaml

# Wait a few minutes, then check
kubectl get cronjobs
kubectl get jobs
kubectl get pods

# View logs from the latest job
kubectl logs -l job-name=$(kubectl get jobs -o jsonpath='{.items[-1].metadata.name}')

kubectl delete cronjob backup-job
```

---

## Demo 4: RBAC (Role-Based Access Control)

`rbac.yaml`:

```yaml
# Create a namespace for the demo
apiVersion: v1
kind: Namespace
metadata:
  name: rbac-demo
---
# Role: what permissions are granted
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: rbac-demo
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
---
# ServiceAccount: identity for pods/users
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dev-user
  namespace: rbac-demo
---
# RoleBinding: attach the role to the service account
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-user-pod-reader
  namespace: rbac-demo
subjects:
  - kind: ServiceAccount
    name: dev-user
    namespace: rbac-demo
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f rbac.yaml

# Create a pod in the namespace
kubectl run test-pod --image=nginx -n rbac-demo

# Test what the dev-user can do
kubectl auth can-i list pods -n rbac-demo --as=system:serviceaccount:rbac-demo:dev-user
# yes

kubectl auth can-i create pods -n rbac-demo --as=system:serviceaccount:rbac-demo:dev-user
# no

kubectl auth can-i delete pods -n rbac-demo --as=system:serviceaccount:rbac-demo:dev-user
# no

kubectl delete namespace rbac-demo
```

---

## Demo 5: Network Policies

`network-policy.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: netpol-demo
---
# Deny all traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: netpol-demo
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
# Allow traffic only from frontend to backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: netpol-demo
spec:
  podSelector:
    matchLabels:
      tier: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              tier: frontend
      ports:
        - port: 80
```

```bash
kubectl apply -f network-policy.yaml

# Create pods
kubectl run frontend --image=nginx --labels="tier=frontend" -n netpol-demo
kubectl run backend --image=nginx --labels="tier=backend" -n netpol-demo
kubectl run other --image=nginx --labels="tier=other" -n netpol-demo

# Note: NetworkPolicies require a CNI plugin that supports them (Calico, Cilium, etc.)
# On minikube, you may need: minikube start --cni=calico

kubectl delete namespace netpol-demo
```

---

## Demo 6: Helm — Kubernetes Package Manager

```bash
# Install Helm (if not already installed)
# brew install helm    (macOS)
# choco install kubernetes-helm  (Windows)

# Add a chart repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Search for charts
helm search repo nginx
helm search repo postgresql

# Install a chart
helm install my-nginx bitnami/nginx

# View what was installed
helm list
kubectl get all -l app.kubernetes.io/instance=my-nginx

# View chart values (configuration options)
helm show values bitnami/nginx | head -50

# Install with custom values
helm install my-redis bitnami/redis --set auth.password=workshop123

# Upgrade a release
helm upgrade my-nginx bitnami/nginx --set replicaCount=3

# View release history
helm history my-nginx

# Rollback
helm rollback my-nginx 1

# Uninstall
helm uninstall my-nginx
helm uninstall my-redis
```

---

## Bonus: Debugging Cheat Sheet

```bash
# Pod stuck in CrashLoopBackOff?
kubectl logs POD --previous         # Logs from crashed container
kubectl describe pod POD            # Check events section

# Pod stuck in Pending?
kubectl describe pod POD            # Check events — likely resource issue
kubectl get events --sort-by='.lastTimestamp'

# Pod stuck in ImagePullBackOff?
kubectl describe pod POD            # Check image name and registry access

# Can't connect to a service?
kubectl get endpoints SERVICE       # Are there backing pods?
kubectl get pods -l LABEL           # Are pods running and ready?
kubectl run debug --rm -it --image=alpine --restart=Never -- sh
# Inside: apk add curl && curl http://SERVICE

# General debugging
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods                    # Resource usage
kubectl top nodes
```

---

## Exercises for Participants

1. Set up a ResourceQuota in a namespace and try to exceed it
2. Create an HPA and generate load to trigger scaling
3. Create a Job that processes 5 items with parallelism of 2
4. Set up a CronJob that runs every minute
5. Create an RBAC Role that allows only reading pods and bind it to a ServiceAccount
6. Install a Helm chart and customize its values
