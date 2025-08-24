# WorkProfile Application

## Overview
WorkProfile is a production-ready multi-tier web application built with **Flask** and **MySQL**.  
It is designed for deployment on **Kubernetes**, with a complete **CI/CD pipeline** that automates:
- Building and testing the application  
- Pushing Docker images to **GitHub Container Registry (GHCR)**  
- Deploying to Kubernetes clusters (kind / Killercoda environments)  

---

## Architecture

### CI/CD Pipeline
The GitHub Actions pipeline covers:
1. **build-test** → Install dependencies, run linting & unit tests, create a semantic image tag  
2. **e2e-tests** → Start full stack with Docker Compose, run smoke tests and Python E2E tests  
3. **push-image** → Build & push Docker image to GHCR (latest + semantic version)  
4. **deploy-k8s** → Create a kind cluster, deploy MySQL + WorkProfile, verify resources, and run connectivity tests  

📷 *CI/CD Pipeline Diagram*  
![CI CD Pipeline WorkProfile](docs/images/cicd-pipeline.png)

---

### Three-Tier Architecture (Docker Compose)
Local testing uses **docker-compose**, which runs:
- **Nginx** (frontend proxy)  
- **Flask Application** (backend API)  
- **MySQL** (database)  

📷 *Docker Compose Architecture*  
![docker-compose WorkProfile](docs/images/docker-architecture.png)

---

### Kubernetes Deployment
On Kubernetes, the system consists of:
- **MySQL StatefulSet** (with PersistentVolumeClaims for data durability)  
- **Secrets** (database credentials)  
- **ConfigMaps** (init SQL + app config)  
- **WorkProfile Deployment** (Flask app with readiness/liveness probes)  
- **Services** (ClusterIP for MySQL, NodePort for WorkProfile)  

📷 *Kubernetes Deployment Architecture*  
![Kubernetes WorkProfile](docs/images/k8s-architecture.png)

---

## Components

### WorkProfile Flask Application
- Python 3.10 backend with REST endpoints  
- Unit and end-to-end (E2E) tests  
- Configurable through Kubernetes ConfigMaps  

### MySQL StatefulSet
- Persistent 2Gi storage  
- Credentials stored securely in Secrets  
- Initialized via ConfigMap (init.sql)  

### Docker & GHCR
- Docker images built and tagged (e.g. `v1.0.27`)  
- Images pushed to GHCR for versioning and distribution  

### Kubernetes Deployment
- Deployments + StatefulSets with resource limits  
- Health checks with liveness/readiness probes  
- NodePort service for external access  

---

## Setup and Usage

### Prerequisites
- A Kubernetes cluster (or Killercoda environment)  
- `kubectl` CLI installed and configured  
- Docker + Docker Compose (for local testing)  
- GitHub repository with secrets:  
  - `GITHUB_TOKEN`  
  - `GHCR_TOKEN` (for pushing images to GHCR)  

---

## Running Locally (Docker Compose)

```bash
# 1. Clone the repository
git clone https://github.com/HadasSigron/WorkProfile.git
cd WorkProfile

# 2. Start full stack (Flask + MySQL + Nginx)
docker-compose -f docker-compose/docker-compose.yml up -d --build

# 3. Access the app locally
http://localhost:8080

# 4. Run tests
pytest tests/e2e_tests.py
```

---

## Manual Deployment to Kubernetes (Killercoda Example)

```bash
# 0. Clean start
kubectl delete namespace workprofile --ignore-not-found
kubectl create namespace workprofile

# 1. Clone repository
git clone https://github.com/HadasSigron/WorkProfile.git
cd WorkProfile

# 2. Deploy MySQL
kubectl -n workprofile apply -f k8s/mysql-secret.yaml
kubectl -n workprofile create configmap mysql-initdb-config   --from-file=init.sql=init.sql   -o yaml --dry-run=client | kubectl apply -n workprofile -f -
kubectl -n workprofile apply -f k8s/mysql-statefulset.yaml
kubectl -n workprofile apply -f k8s/mysql-service.yaml
kubectl -n workprofile rollout status statefulset/mysql --timeout=300s

# 3. Deploy WorkProfile application
kubectl -n workprofile apply -f k8s/workprofile-configmap.yaml
kubectl -n workprofile apply -f k8s/workprofile-deployment.yaml
kubectl -n workprofile apply -f k8s/workprofile-service.yaml
kubectl -n workprofile rollout status deployment/workprofile --timeout=300s

# 4. Verify services and pods
kubectl -n workprofile get pods,svc -o wide

# 5. Access the application (NodePort 30080)
# In Killercoda: http://<session-id>.spchr.killercoda.com:30080

# 6. Health check from inside cluster
kubectl -n workprofile run curl-$RANDOM --rm -it --image=curlimages/curl --restart=Never --   curl -sf http://workprofile-service:5000/health
```

---

## Screenshots

📷 *1. Killercoda Deployment Terminal*  
![Killercoda Terminal](docs/images/kc-terminal.png)

📷 *2. Application Homepage*  
![App Home](docs/images/app-home.png)

📷 *3. Application Add Form*  
![App Add Form](docs/images/app-add.png)

---

## Additional Notes
- Semantic versioning: `v1.0.<run_number>`  
- Credentials always stored in **Secrets**, never in plain text  
- Resource limits ensure predictable performance  
- Health checks guarantee resiliency and self-healing  

---

## Contribution
For issues or contributions, please open a PR or issue on GitHub.
