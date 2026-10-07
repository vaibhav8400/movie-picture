# Movie Picture Pipeline

An automated continuous integration and continuous deployment (CI/CD) pipeline built with GitHub Actions, Docker, Amazon ECR, and Kubernetes (AWS EKS) for a microservices-based Movie Picture web application.

---

## 🌐 Live Microservice Endpoints

The microservices are continuously deployed to an AWS EKS cluster via AWS Elastic Load Balancers:

* **Frontend Web Application:** http://<frontend-elb-hostname>
* **Backend REST API (`/movies`):** http://<backend-elb-hostname>/movies
* **Source Repository:** https://github.com/<your-username>/cd12354-Movie-Picture-Pipeline

---

## 📸 Evidence

### Workflow Runs

| Workflow | Screenshot |
| :--- | :--- |
| Frontend CI | ![Frontend CI](screenshots/frontend-ci.png) |
| Backend CI | ![Backend CI](screenshots/backend-ci.png) |
| Frontend CD | ![Frontend CD](screenshots/frontend-cd.png) |
| Backend CD | ![Backend CD](screenshots/backend-cd.png) |

### Deployed Applications

* **Frontend loading movies:**

  ![Frontend app](screenshots/frontend-app.png)

* **Backend `/movies` response:**

  ![Backend movies](screenshots/backend-movies.png)

### Amazon ECR Images

![ECR images](screenshots/ecr.png)

---

## 🏗️ Architecture & Tech Stack

* **Frontend Application (`starter/frontend`):** React 18 and TypeScript Single Page Application served via a production Node/Express runtime.
* **Backend REST API (`starter/backend`):** Python 3.10 Flask service served using uWSGI with enabled Cross-Origin Resource Sharing (CORS).
* **Container Registry:** Amazon Elastic Container Registry (ECR) for backend and frontend Docker images.
* **Cluster Orchestration:** Amazon Elastic Kubernetes Service (AWS EKS v1.31) provisioned with Terraform, leveraging Kustomize for declarative GitOps updates.
* **CI/CD Automation:** GitHub Actions workflows executing dependency caching, linting, testing, image packaging, and zero-downtime rolling releases.

---

## 🚀 CI/CD Pipeline Implementation

### 1. Frontend Continuous Integration (`frontend-ci.yaml`)

Workflow name: **Frontend Continuous Integration**. Triggered on pull requests targeting `main` and via `workflow_dispatch`:

* **Lint Job:**
  * Checkout code and Node.js 18 setup.
  * **Cache:** Restores `~/.npm` dependencies using `actions/cache@v3` prior to installation.
  * Dependency installation via `npm ci` followed by ESLint verification (`npm run lint`).
* **Test Job (runs in parallel with Lint):**
  * Checkout code and Node.js 18 setup.
  * **Cache:** Restores `~/.npm` dependencies using `actions/cache@v3` prior to installation.
  * Dependency installation via `npm ci`, then Jest test suites in non-interactive mode (`npm test -- --watchAll=false`).
* **Build Job (requires `[lint, test]`):**
  * Checkout code, Node.js 18 setup, cache restore, and dependency installation.
  * Application image built with Docker (`docker build`).

### 2. Backend Continuous Integration (`backend-ci.yaml`)

Workflow name: **Backend Continuous Integration**. Triggered on pull requests targeting `main` and via `workflow_dispatch`:

* **Lint Job:** Runs `flake8` under Pipenv.
* **Test Job (runs in parallel with Lint):** Runs `pytest` under Pipenv.
* **Build Job (requires `[lint, test]`):** Builds the backend Docker image.

### 3. Backend Continuous Deployment (`backend-cd.yaml`)

Workflow name: **Backend Continuous Deployment**. Triggered on push to `main` modifying `starter/backend/**` and via `workflow_dispatch`:

* Executes Python code standards validation (`flake8`) and test suites (`pytest`) under Pipenv.
* Authenticates with AWS ECR via `aws-actions/amazon-ecr-login@v1`.
* Builds, tags, and pushes backend Docker images to Amazon ECR.
* Updates the Kubernetes deployment image with `kustomize edit set image` and applies the manifest.
* **Deployment Verification & Logging:**
  * Performs rollout status verification: `kubectl rollout status deployment/backend --timeout=180s`.
  * Emits full cluster state: `kubectl get all`.
  * Emits deployment metadata: `kubectl describe deploy backend`.
  * Validates ECR image details: `aws ecr describe-images --repository-name backend --image-ids imageTag=latest`.

### 4. Frontend Continuous Deployment (`frontend-cd.yaml`)

Workflow name: **Frontend Continuous Deployment**. Triggered on push to `main` modifying `starter/frontend/**` and via `workflow_dispatch`:

* Executes cached dependency installations (`actions/cache@v3`), ESLint checks, and Jest tests.
* Builds the production Docker image (only after lint and test succeed, via `needs`) with build-arg injection:
  `--build-arg REACT_APP_MOVIE_API_URL=${{ secrets.REACT_APP_MOVIE_API_URL }}`
* Pushes the compiled frontend container image to Amazon ECR.
* Deploys the service to AWS EKS using Kustomize.
* **Deployment Verification & Logging:**
  * Verifies rollout health: `kubectl rollout status deployment/frontend --timeout=180s`.
  * Emits full cluster state: `kubectl get all`.
  * Emits deployment metadata: `kubectl describe deploy frontend`.
  * Validates ECR image details: `aws ecr describe-images --repository-name frontend --image-ids imageTag=latest`.

---

## 🔐 GitHub Repository Secrets Configuration

No credentials are stored in the repository or workflow files. The following repository secrets are configured under **Settings > Secrets and variables > Actions**:

| Secret Name | Value / Description |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM Secret Access Key |
| `AWS_SESSION_TOKEN` | AWS STS Session Token (for Learner Lab sessions) |
| `AWS_DEFAULT_REGION` | `us-east-1` |
| `EKS_CLUSTER_NAME` | `cluster` |
| `BACKEND_ECR_REPO` | `backend` |
| `FRONTEND_ECR_REPO` | `frontend` |
| `REACT_APP_MOVIE_API_URL` | Backend Load Balancer URL (set after backend is deployed; no `/movies` suffix) |

---

## 💻 Local Development & Testing

### Frontend

```bash
cd starter/frontend

# Install dependencies
npm ci

# Run linter & test suite
npm run lint
npm test -- --watchAll=false

# Build production bundle
npm run build

# Start local server
REACT_APP_MOVIE_API_URL=http://localhost:5000 npm start
```

### Backend

```bash
cd starter/backend

# Install dependencies
pipenv install

# Run application
pipenv run serve

# Check the running application
curl http://localhost:5000/movies
```

### Backend with Docker

```bash
cd starter/backend

# Build and run the image
docker build --tag mp-backend:latest .
docker run -p 5000:5000 --name mp-backend -d mp-backend

# Expected output from /movies
# {"movies":[{"id":"123","title":"Top Gun: Maverick"},{"id":"456","title":"Sonic the Hedgehog"},{"id":"789","title":"A Quiet Place"}]}

# Stop the application
docker stop mp-backend
```
