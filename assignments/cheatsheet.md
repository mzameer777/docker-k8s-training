# Docker & Kubernetes Quick Reference Cheat Sheet

Keep this handy while working through the assignments.

---

## Docker

### Images

```bash
docker build -t NAME:TAG .                       # Build from Dockerfile
docker build -f FILE -t NAME:TAG .               # Use specific Dockerfile
docker build --build-arg KEY=VAL -t NAME:TAG .   # Pass build arg
docker build --target STAGE -t NAME:TAG .        # Build specific stage
docker images                                     # List local images
docker pull IMAGE:TAG                             # Download image
docker push IMAGE:TAG                             # Push to registry
docker tag SOURCE TARGET                          # Tag an image
docker rmi IMAGE                                  # Remove image
docker history IMAGE                              # Show layers
docker inspect IMAGE                              # Detailed metadata
```

### Containers

```bash
docker run -d --name NAME IMAGE                  # Run in background
docker run -it IMAGE COMMAND                     # Run interactively
docker run --rm IMAGE                            # Auto-remove on exit
docker run -p HOST:CONTAINER IMAGE               # Port mapping
docker run -e KEY=VAL IMAGE                      # Set env var
docker run -v NAME:/path IMAGE                   # Named volume
docker run -v /host:/container IMAGE             # Bind mount
docker run --memory=256m --cpus=0.5 IMAGE        # Resource limits
docker run --network NET IMAGE                   # Specific network
docker run --read-only IMAGE                     # Read-only filesystem
docker run --user 1000 IMAGE                     # Run as specific user
docker ps                                         # Running containers
docker ps -a                                      # All containers
docker stop NAME                                  # Stop container
docker rm NAME                                    # Remove container
docker rm -f NAME                                 # Force remove
docker logs NAME [-f]                             # View logs
docker exec -it NAME COMMAND                      # Run in container
docker inspect NAME                               # Detailed info
docker stats                                      # Live resource usage
docker cp NAME:/path /host/path                   # Copy from container
```

### Volumes & Networks

```bash
docker volume create NAME                         # Create volume
docker volume ls                                  # List volumes
docker volume rm NAME                             # Delete volume
docker network create NAME                        # Create network
docker network ls                                 # List networks
docker network connect NET CONTAINER              # Add to network
docker network rm NAME                            # Delete network
```

### Docker Compose

```bash
docker compose up -d                              # Start in background
docker compose up -d --build                      # Rebuild then start
docker compose down                               # Stop and remove
docker compose down -v                            # Also remove volumes
docker compose ps                                 # List services
docker compose logs [-f] [SERVICE]                # View logs
docker compose exec SERVICE COMMAND               # Run in service
docker compose build                              # Build images
docker compose config                             # Preview resolved config
docker compose restart SERVICE                    # Restart a service
docker compose scale SERVICE=N                    # Scale service
```

---

## Kubernetes

### Basics

```bash
kubectl cluster-info                              # Cluster info
kubectl get nodes                                 # List nodes
kubectl get all                                   # List everything
kubectl get RESOURCE                              # List resource type
kubectl get RESOURCE NAME                         # Get specific resource
kubectl get RESOURCE -o wide                      # Extra columns
kubectl get RESOURCE -o yaml                      # Full YAML output
kubectl get RESOURCE -l KEY=VAL                   # Filter by label
kubectl get RESOURCE --show-labels                # Show labels
kubectl describe RESOURCE NAME                    # Detailed info + events
kubectl explain RESOURCE                          # Built-in docs
kubectl apply -f FILE.yaml                        # Create/update
kubectl delete -f FILE.yaml                       # Delete from YAML
kubectl delete RESOURCE NAME                      # Delete specific
kubectl get events --sort-by='.lastTimestamp'     # View events
```

### Pods

```bash
kubectl run NAME --image=IMAGE                    # Create pod quickly
kubectl logs POD [-f]                             # View logs
kubectl logs POD -c CONTAINER                     # Specific container
kubectl logs POD --previous                       # Crashed container
kubectl exec -it POD -- COMMAND                   # Execute in pod
kubectl exec -it POD -c CONTAINER -- COMMAND      # Specific container
kubectl port-forward pod/NAME LOCAL:REMOTE        # Forward port
kubectl cp POD:/path /local/path                  # Copy from pod
kubectl top pods                                  # Resource usage
```

### Deployments

```bash
kubectl create deployment NAME --image=IMAGE      # Quick deployment
kubectl scale deployment NAME --replicas=N        # Scale
kubectl set image deployment/NAME CONT=IMAGE      # Update image
kubectl rollout status deployment/NAME            # Watch rollout
kubectl rollout history deployment/NAME           # Rollout history
kubectl rollout undo deployment/NAME              # Rollback
kubectl rollout undo deployment/NAME --to-revision=N  # Specific revision
kubectl rollout restart deployment/NAME           # Restart all pods
```

### Services

```bash
kubectl expose deployment NAME --port=80          # Quick service
kubectl get svc                                   # List services
kubectl get endpoints NAME                        # Show pod IPs
kubectl port-forward svc/NAME LOCAL:REMOTE        # Forward service port
```

### ConfigMaps & Secrets

```bash
kubectl create configmap NAME --from-literal=K=V  # From literal
kubectl create configmap NAME --from-file=FILE     # From file
kubectl create secret generic NAME --from-literal=K=V
kubectl get configmap NAME -o yaml
kubectl get secret NAME -o yaml
kubectl get secret NAME -o jsonpath='{.data.KEY}' | base64 -d
```

### Namespaces

```bash
kubectl create namespace NAME                     # Create namespace
kubectl get all -n NAME                           # Resources in namespace
kubectl config set-context --current --namespace=NAME  # Set default NS
```

### Debugging

```bash
# Pod in CrashLoopBackOff
kubectl logs POD --previous
kubectl describe pod POD           # Check Events section

# Pod in Pending
kubectl describe pod POD           # Usually scheduling/resource issue

# Pod in ImagePullBackOff
kubectl describe pod POD           # Check image name + registry

# Can't reach a service
kubectl get endpoints SVC          # Any pods backing it?
kubectl run debug --rm -it --image=alpine --restart=Never -- sh
# > apk add curl && curl http://SERVICE-NAME

# General
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods
kubectl top nodes
kubectl auth can-i VERB RESOURCE -n NAMESPACE --as=SERVICEACCOUNT
```

### RBAC

```bash
kubectl auth can-i list pods                      # Check my permissions
kubectl auth can-i list pods --as=system:serviceaccount:NS:SA
kubectl get clusterroles                          # Built-in roles
kubectl describe clusterrole edit                 # What 'edit' allows
```

### Helm

```bash
helm repo add NAME URL                            # Add chart repo
helm repo update                                  # Refresh repos
helm search repo KEYWORD                          # Search charts
helm install RELEASE CHART                        # Install
helm install RELEASE CHART --set KEY=VAL          # With custom values
helm install RELEASE CHART -f values.yaml         # With values file
helm list                                         # Installed releases
helm upgrade RELEASE CHART                        # Upgrade
helm rollback RELEASE VERSION                     # Rollback
helm uninstall RELEASE                            # Remove
helm show values CHART                            # Default values
helm template RELEASE CHART                       # Preview manifests
```

---

## Useful One-Liners

```bash
# Watch pods across all namespaces
kubectl get pods --all-namespaces -w

# Delete all pods in a namespace with a label
kubectl delete pods -l app=myapp -n mynamespace

# Get the image of a running deployment
kubectl get deployment myapp -o jsonpath='{.spec.template.spec.containers[0].image}'

# Force delete a stuck namespace
kubectl delete namespace NAME --force --grace-period=0

# Get all resource types
kubectl api-resources

# Diff before applying
kubectl diff -f manifest.yaml

# Dry run (validate without applying)
kubectl apply -f manifest.yaml --dry-run=client

# Base64 encode a secret value
echo -n "mypassword" | base64

# Decode a secret value
kubectl get secret NAME -o jsonpath='{.data.KEY}' | base64 -d

# Quick interactive debug pod
kubectl run debug --rm -it --image=alpine --restart=Never -- sh

# Watch HPA
kubectl get hpa -w

# Port forward a service
kubectl port-forward svc/myservice 8080:80 &
```
