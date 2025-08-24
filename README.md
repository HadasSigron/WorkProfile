# WorkProfile Application

## Overview

WorkProfile is a production-ready multi-tier web application built with
**Flask** and **MySQL**.\
It is designed for deployment on **Kubernetes** with a full **CI/CD
pipeline** using GitHub Actions.\
The project supports both local development (via Docker Compose) and
cloud-native deployment.

------------------------------------------------------------------------

## Architecture

### Docker Compose (Nginx + Flask + MySQL)

![Architecture - Docker Compose](docs/architecture-compose.png)

### Kubernetes (Deployments, StatefulSet, Services)

![Architecture - Kubernetes](docs/architecture-k8s.png)

### CI/CD Pipeline (GitHub Actions)

![CI/CD Pipeline](docs/architecture-pipeline.png)

------------------------------------------------------------------------

## Application Screenshots

Below are example screenshots of the WorkProfile application in action:

![UI Screenshot 1](docs/ui-1.png) ![UI Screenshot 2](docs/ui-2.png) ![UI
Screenshot 3](docs/ui-3.png)

------------------------------------------------------------------------

## Running Locally with Docker Compose

``` bash
# Clone the repository
git clone https://github.com/<your-username>/WorkProfile.git
cd WorkProfile

# Start the stack (Nginx + Flask + MySQL)
docker-compose -f docker-compose/docker-compose.yml up -d --build

# Access the app
http://localhost:8080/
```

------------------------------------------------------------------------

## Deployment on Kubernetes (Killercoda or local cluster)

``` bash
# Create namespace
kubectl create namespace workprofile

# MySQL secrets + init.sql
kubectl -n workprofile apply -f k8s/mysql-secret.yaml
kubectl -n workprofile create configmap mysql-initdb-config   --from-file=init.sql=init.sql   -o yaml --dry-run=client | kubectl apply -n workprofile -f -

# MySQL StatefulSet + Services
kubectl -n workprofile apply -f k8s/mysql-statefulset.yaml
kubectl -n workprofile apply -f k8s/mysql-service.yaml
kubectl -n workprofile rollout status statefulset/mysql --timeout=360s

# WorkProfile application (ConfigMap + Deployment + Service)
kubectl -n workprofile apply -f k8s/workprofile-configmap.yaml
kubectl -n workprofile apply -f k8s/workprofile-deployment.yaml
kubectl -n workprofile apply -f k8s/workprofile-service.yaml
kubectl -n workprofile rollout status deployment/workprofile --timeout=300s

# Get NodePort and access via Killercoda Traffic Port (e.g., 30080)
kubectl -n workprofile get svc workprofile-service
```

------------------------------------------------------------------------

## CI/CD Pipeline (GitHub Actions)

-   **build-test**: Lint + unit tests, build Docker image, generate
    tag.\
-   **e2e-tests**: Run integration tests with Docker Compose.\
-   **push-image**: Push Docker image to GitHub Container Registry
    (GHCR).\
-   **deploy-k8s**: Deploy MySQL + WorkProfile on Kubernetes, validate
    stack, port-forward, health-check.

------------------------------------------------------------------------

## Notes

-   Secrets are managed securely with Kubernetes Secrets.\
-   Configurations are stored in ConfigMaps.\
-   Health probes (liveness & readiness) ensure reliability.\
-   Resource limits provide predictable scaling.

------------------------------------------------------------------------

## Contribution

Contributions are welcome! Please open issues or submit pull requests on
GitHub.
