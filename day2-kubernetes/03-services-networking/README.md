# Module 3: Services & Networking (~1 hour)

## The Problem

Pods are ephemeral — they get new IPs when replaced. **Services** provide a stable endpoint.

```
Without Service:              With Service:
App → Pod IP (10.1.0.5)       App → Service (task-api:80) → Pod 1
Pod dies, new IP (10.1.0.9)                                → Pod 2
App breaks!                                                → Pod 3
                              Service handles discovery + load balancing
```

---

## Service Types

| Type           | Description                                         | Access                     |
| -------------- | --------------------------------------------------- | -------------------------- |
| `ClusterIP`    | Internal only (default)                             | Within the cluster         |
| `NodePort`     | Exposes on each node's IP at a static port          | `<NodeIP>:<NodePort>`      |
| `LoadBalancer` | Provisions an external load balancer (cloud only)   | External IP                |
| `ExternalName` | Maps to a DNS name                                  | DNS alias                  |

---

## Demo 1: ClusterIP Service

First, create a deployment:

```bash
kubectl apply -f ../02-pods-deployments/deployment.yaml
```

`service-clusterip.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: task-api-service
spec:
  type: ClusterIP
  selector:
    app: task-api      # Matches pods with this label
  ports:
    - protocol: TCP
      port: 80         # Service port
      targetPort: 80   # Container port
```

```bash
kubectl apply -f service-clusterip.yaml

# View the service
kubectl get svc task-api-service
kubectl describe svc task-api-service

# Notice the Endpoints — these are the pod IPs
kubectl get endpoints task-api-service

# Test from inside the cluster
kubectl run test-pod --rm -it --image=alpine --restart=Never -- sh
# Inside: apk add curl && curl http://task-api-service
# Notice: DNS resolves the service name!
# Try multiple times — requests go to different pods

# Port-forward to access from your machine
kubectl port-forward svc/task-api-service 8080:80
# Visit http://localhost:8080
```

---

## Demo 2: NodePort Service

`service-nodeport.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: task-api-nodeport
spec:
  type: NodePort
  selector:
    app: task-api
  ports:
    - protocol: TCP
      port: 80          # Service port (inside cluster)
      targetPort: 80    # Container port
      nodePort: 30080   # Port on every node (30000-32767)
```

```bash
kubectl apply -f service-nodeport.yaml
kubectl get svc task-api-nodeport

# Access via NodePort
# If using minikube:
minikube service task-api-nodeport --url

# If using Docker Desktop:
curl http://localhost:30080

# If using kind:
# You need to expose the port when creating the cluster
```

---

## Demo 3: LoadBalancer Service

`service-loadbalancer.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: task-api-lb
spec:
  type: LoadBalancer
  selector:
    app: task-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```

```bash
kubectl apply -f service-loadbalancer.yaml
kubectl get svc task-api-lb

# On cloud: an external IP is provisioned
# On Docker Desktop: localhost works
# On minikube: use `minikube tunnel` in a separate terminal

# Watch for external IP
kubectl get svc task-api-lb -w
```

---

## Demo 4: DNS Service Discovery

```bash
# Kubernetes provides DNS for services automatically
# Format: <service-name>.<namespace>.svc.cluster.local

# Launch a debug pod
kubectl run dns-test --rm -it --image=alpine --restart=Never -- sh

# Inside the pod:
apk add curl bind-tools

# DNS lookup
nslookup task-api-service
nslookup task-api-service.default.svc.cluster.local

# Access the service by name
curl http://task-api-service
curl http://task-api-service.default.svc.cluster.local

exit
```

---

## Demo 5: Ingress (HTTP Routing)

Ingress provides HTTP/HTTPS routing with host/path-based rules.

### Install Ingress Controller

```bash
# For minikube:
minikube addons enable ingress

# For Docker Desktop / kind:
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Wait for it
kubectl get pods -n ingress-nginx -w
```

### Create two deployments + services

```bash
kubectl create deployment web --image=nginx --replicas=2
kubectl expose deployment web --port=80
kubectl create deployment api --image=nginx --replicas=2
kubectl expose deployment api --port=80
```

`ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: workshop-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: workshop.local
      http:
        paths:
          - path: /web
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

```bash
kubectl apply -f ingress.yaml
kubectl get ingress

# Add to /etc/hosts (or use curl with Host header)
# 127.0.0.1 workshop.local

curl -H "Host: workshop.local" http://localhost/web
curl -H "Host: workshop.local" http://localhost/api

# Clean up
kubectl delete ingress workshop-ingress
kubectl delete deployment web api
kubectl delete svc web api
```

---

## Demo 6: Multi-Port Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port-demo
spec:
  selector:
    app: task-api
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: metrics
      port: 9090
      targetPort: 9090
```

---

## Clean Up

```bash
kubectl delete -f service-clusterip.yaml
kubectl delete -f service-nodeport.yaml
kubectl delete -f service-loadbalancer.yaml
kubectl delete -f ../02-pods-deployments/deployment.yaml
```

---

## Exercises for Participants

1. Create a deployment + ClusterIP service and test DNS resolution from a debug pod
2. Expose a service as NodePort and access it from your browser
3. Set up an Ingress with two paths routing to two different services
4. Use `kubectl port-forward` to access a ClusterIP service from your machine

---

## Quick Reference

```bash
kubectl get svc                          # List services
kubectl describe svc NAME                # Service details
kubectl get endpoints NAME               # Show backing pod IPs
kubectl expose deployment NAME --port=80 # Quick service creation
kubectl port-forward svc/NAME L:R        # Forward service port
kubectl get ingress                      # List ingress rules
```
