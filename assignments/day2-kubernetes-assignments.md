# Day 2 Take-Home Assignments: Kubernetes

Short, focused exercises to reinforce the Kubernetes concepts from today. Each one should take 10–20 minutes. Don't worry about getting everything perfect — the goal is to get comfortable with the tools.

---

## Assignment 1: Your First Pod and Deployment

**Concept:** Running workloads on Kubernetes, self-healing.

1. Create a simple nginx deployment with 2 replicas:
   ```bash
   kubectl create deployment my-nginx --image=nginx --replicas=2
   ```

2. Check that 2 pods are running:
   ```bash
   kubectl get pods
   kubectl get deployment my-nginx
   ```

3. **Watch self-healing in action:**
   - Get the name of one pod: `kubectl get pods`
   - Delete it: `kubectl delete pod <POD_NAME>`
   - Immediately run `kubectl get pods` again — Kubernetes is already replacing it!

4. Clean up:
   ```bash
   kubectl delete deployment my-nginx
   ```

**Questions to think about:**
- What would happen if you just ran a bare Pod (no Deployment) and it crashed?
- Why does Kubernetes replace the pod automatically?

---

## Assignment 2: Scale and Update

**Concept:** Scaling deployments, rolling updates, rollback.

1. Create a deployment:
   ```bash
   kubectl create deployment web --image=nginx:1.25
   ```

2. Scale it to 4 replicas:
   ```bash
   kubectl scale deployment web --replicas=4
   kubectl get pods
   ```

3. Update the image to `nginx:1.26` and watch the rolling update:
   ```bash
   kubectl set image deployment/web nginx=nginx:1.26
   kubectl rollout status deployment/web
   ```

4. Check the rollout history:
   ```bash
   kubectl rollout history deployment/web
   ```

5. Roll back to the previous version:
   ```bash
   kubectl rollout undo deployment/web
   ```

6. Verify it rolled back:
   ```bash
   kubectl get deployment web -o wide
   # Look at the IMAGE column
   ```

7. Clean up:
   ```bash
   kubectl delete deployment web
   ```

**Questions to think about:**
- During the rolling update, were there always pods running? Why does that matter?
- When would you need to roll back a deployment?

---

## Assignment 3: Expose an App with a Service

**Concept:** Services give pods a stable, reachable address.

1. Create a deployment:
   ```bash
   kubectl create deployment hello --image=nginx --replicas=3
   ```

2. Expose it as a Service:
   ```bash
   kubectl expose deployment hello --port=80 --name=hello-service
   ```

3. Check the service:
   ```bash
   kubectl get svc hello-service
   kubectl get endpoints hello-service   # See the 3 pod IPs
   ```

4. Access it using port-forward:
   ```bash
   kubectl port-forward svc/hello-service 9090:80
   # Open http://localhost:9090 in your browser
   # Press Ctrl+C when done
   ```

5. Test DNS from inside the cluster:
   ```bash
   kubectl run test --rm -it --image=alpine --restart=Never -- sh
   # Inside: apk add curl && curl http://hello-service
   # Type exit when done
   ```

6. Clean up:
   ```bash
   kubectl delete deployment hello
   kubectl delete svc hello-service
   ```

**Questions to think about:**
- What happens to the Service's IP if a pod is replaced?
- Why is using the service name (like `hello-service`) better than using a pod's IP directly?

---

## Assignment 4: ConfigMap — Separate Config from Code

**Concept:** Store configuration outside your container image.

1. Create a ConfigMap:
   ```bash
   kubectl create configmap app-config \
     --from-literal=ENVIRONMENT=staging \
     --from-literal=LOG_LEVEL=debug
   ```

2. Check what's inside:
   ```bash
   kubectl get configmap app-config -o yaml
   ```

3. Run a pod that uses it:
   ```bash
   kubectl run config-demo \
     --image=alpine \
     --env="ENVIRONMENT=ignore-this" \
     --restart=Never \
     -- sh -c "env | grep -E 'ENVIRONMENT|LOG_LEVEL'"
   ```
   *(Note: env from `--env` shows — now let's use the ConfigMap instead)*

4. Create a pod that reads from the ConfigMap. Save this as `pod-config.yaml`:

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: config-demo
   spec:
     restartPolicy: Never
     containers:
       - name: demo
         image: alpine
         command: ["sh", "-c", "env | grep -E 'ENVIRONMENT|LOG_LEVEL' && sleep 5"]
         envFrom:
           - configMapRef:
               name: app-config
   ```

   ```bash
   kubectl apply -f pod-config.yaml
   kubectl logs config-demo
   # You should see ENVIRONMENT=staging and LOG_LEVEL=debug
   ```

5. Clean up:
   ```bash
   kubectl delete pod config-demo
   kubectl delete configmap app-config
   ```

**Questions to think about:**
- What's the advantage of storing config in a ConfigMap instead of hardcoding it in the image?
- What would you use a Secret for instead of a ConfigMap?

---

## Assignment 5: Persistent Storage — Data That Survives

**Concept:** Pods are temporary; PersistentVolumeClaims keep data safe.

1. Create a PersistentVolumeClaim. Save as `pvc.yaml`:

   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: my-data
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 100Mi
   ```

   ```bash
   kubectl apply -f pvc.yaml
   kubectl get pvc   # Should show STATUS: Bound
   ```

2. Write data with a pod. Save as `writer-pod.yaml`:

   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: writer
   spec:
     restartPolicy: Never
     containers:
       - name: writer
         image: alpine
         command: ["sh", "-c", "echo 'Hello from Kubernetes!' > /data/message.txt && echo 'Written!'"]
         volumeMounts:
           - name: storage
             mountPath: /data
     volumes:
       - name: storage
         persistentVolumeClaim:
           claimName: my-data
   ```

   ```bash
   kubectl apply -f writer-pod.yaml
   kubectl logs writer   # Should print "Written!"
   kubectl delete pod writer
   ```

3. Read the data back with a different pod — prove the data survived:

   ```bash
   kubectl run reader --rm -it --restart=Never \
     --image=alpine \
     --overrides='{"spec":{"volumes":[{"name":"storage","persistentVolumeClaim":{"claimName":"my-data"}}],"containers":[{"name":"reader","image":"alpine","command":["cat","/data/message.txt"],"volumeMounts":[{"name":"storage","mountPath":"/data"}]}]}}' \
     -- cat /data/message.txt
   ```

   You should see: `Hello from Kubernetes!`

4. Clean up:
   ```bash
   kubectl delete pvc my-data
   ```

**Questions to think about:**
- What would happen to this data if there were no PVC and the pod was deleted?
- What kind of applications need persistent storage? (Think: databases, file uploads)

---

## Checklist

Before wrapping up, make sure you can answer these:

```
[ ] What is a Pod? What is a Deployment?
[ ] Why does Kubernetes restart pods automatically?
[ ] What is a Service and why do you need one?
[ ] How do pods communicate with each other inside Kubernetes?
[ ] What is a ConfigMap used for?
[ ] What is the difference between a ConfigMap and a Secret?
[ ] What problem does a PersistentVolumeClaim solve?
[ ] How do you roll back a deployment?
```
