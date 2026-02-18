# Module 5: Persistent Storage (~45 min)

## The Problem

Pods are ephemeral. When a pod is deleted, its filesystem is gone. Databases, file uploads, and logs need **persistent storage**.

### Storage Concepts

```
PersistentVolume (PV)         → The actual storage (disk, NFS, cloud volume)
PersistentVolumeClaim (PVC)   → A request for storage by a pod
StorageClass                  → Defines HOW storage is dynamically provisioned
```

```
Pod → PVC → PV → Actual Storage
       ↑
  StorageClass (provisions PV automatically)
```

---

## Demo 1: emptyDir (Temporary Shared Storage)

`emptydir-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-demo
spec:
  containers:
    - name: writer
      image: alpine
      command: ["sh", "-c", "while true; do date >> /shared/log.txt; sleep 2; done"]
      volumeMounts:
        - name: shared-data
          mountPath: /shared
    - name: reader
      image: alpine
      command: ["sh", "-c", "tail -f /shared/log.txt"]
      volumeMounts:
        - name: shared-data
          mountPath: /shared
  volumes:
    - name: shared-data
      emptyDir: {}
```

```bash
kubectl apply -f emptydir-pod.yaml

# Both containers share the same volume
kubectl logs emptydir-demo -c reader -f

# emptyDir is deleted when the pod is deleted
kubectl delete pod emptydir-demo
```

---

## Demo 2: PersistentVolumeClaim (Dynamic Provisioning)

`pvc.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce     # Can be mounted by one node
  resources:
    requests:
      storage: 1Gi
  # storageClassName: standard   # Uses default if omitted
```

```bash
kubectl apply -f pvc.yaml
kubectl get pvc
kubectl get pv    # PV is automatically created (dynamic provisioning)
```

---

## Demo 3: Postgres with Persistent Storage

`postgres-storage.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
stringData:
  POSTGRES_USER: workshop
  POSTGRES_PASSWORD: workshop123
  POSTGRES_DB: tasks
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: postgres-secret
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
              subPath: pgdata
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

```bash
kubectl apply -f postgres-storage.yaml

# Wait for pod to be ready
kubectl get pods -l app=postgres -w

# Create some data
kubectl exec -it deploy/postgres -- psql -U workshop -d tasks -c "
  CREATE TABLE students (id SERIAL PRIMARY KEY, name TEXT);
  INSERT INTO students (name) VALUES ('Alice'), ('Bob');
  SELECT * FROM students;
"

# Delete the pod (Deployment recreates it)
kubectl delete pod -l app=postgres

# Wait for new pod
kubectl get pods -l app=postgres -w

# Data persists!
kubectl exec -it deploy/postgres -- psql -U workshop -d tasks -c "SELECT * FROM students;"

# Clean up
kubectl delete -f postgres-storage.yaml
kubectl delete pvc postgres-pvc
```

---

## Demo 4: StatefulSet (For Stateful Applications)

StatefulSets provide stable network identities and persistent storage per pod.

`statefulset.yaml`:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          volumeMounts:
            - name: redis-data
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: redis-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  clusterIP: None    # Headless service for StatefulSet
  selector:
    app: redis
  ports:
    - port: 6379
```

```bash
kubectl apply -f statefulset.yaml

# Pods get predictable names: redis-0, redis-1, redis-2
kubectl get pods -l app=redis

# Each pod gets its own PVC
kubectl get pvc

# Stable DNS: redis-0.redis, redis-1.redis, redis-2.redis
kubectl run dns-test --rm -it --image=alpine --restart=Never -- \
  sh -c "apk add bind-tools && nslookup redis-0.redis"

# Clean up
kubectl delete -f statefulset.yaml
kubectl delete pvc -l app=redis
```

### Deployment vs StatefulSet

| Feature               | Deployment           | StatefulSet          |
| --------------------- | -------------------- | -------------------- |
| Pod names             | Random suffix        | Ordered (app-0,1,2)  |
| Storage               | Shared PVC           | PVC per pod           |
| Scaling               | Any order            | Ordered (0→1→2)      |
| DNS                   | Via Service only     | Per-pod DNS           |
| Use case              | Stateless apps       | Databases, caches    |

---

## Exercises for Participants

1. Create a PVC and mount it in a pod; write data, delete the pod, verify data persists
2. Deploy Postgres with persistent storage and prove data survives pod deletion
3. Deploy a StatefulSet and observe the ordered pod naming and per-pod storage
4. Use an emptyDir volume to share data between two containers in the same pod
