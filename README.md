![image](https://github.com/user-attachments/assets/3d43773d-4f4b-4abe-b364-dd3537cb708e)

![image](https://github.com/user-attachments/assets/869d70a2-5e0c-4c3a-a5de-a8225476186e)


Hybrid Anime Recommendation System



A scalable, hybrid anime recommendation engine combining collaborative filtering and content-based suggestions. This application is deployed on Google Cloud Platform (GCP) using Kubernetes for orchestration and Jenkins for CI/CD.

🚀 Features

Hybrid Recommendations: Blend of user-based collaborative filtering and anime-content similarity using embeddings.

Fast Inference: Precomputed user/anime embeddings for real-time responses.

Web UI: Simple anime-themed front-end allowing users to input their user ID and receive top recommendations.

Scalable Infrastructure: Containerized with Docker, orchestrated by Kubernetes.

CI/CD Pipeline: Automated build, test, and deployment via Jenkins.

🏗️ Architecture Overview

Frontend: Static HTML/CSS served by Nginx. User input form and result rendering.

Backend API: Python Flask application exposing a /recommend endpoint.

Model Serving: TensorFlow/Keras model loaded in-memory, user & anime embeddings retrieved from Redis.

Data Storage:

GCS: Stores CSV datasets and serialized artifacts (encodings, weights).

Redis: Caches frequently accessed embeddings for low-latency.

Kubernetes:

Deployment: Flask API and Nginx frontend in separate Pods.

Service: Exposes the application via a GCP Load Balancer.

ConfigMaps & Secrets: Store configuration and sensitive keys.

Jenkins: Monitors Git, triggers Docker builds, runs unit tests, pushes images to GCR, and updates Kubernetes via kubectl.

📦 Repository Structure

├── charts/                 # Helm charts (optional)
├── deployments/            # K8s manifests (YAML)
├── docs/                   # Architecture diagrams, design docs
├── frontend/               # Static HTML/CSS/JS for UI
├── backend/                # Flask app source code
├── ml/                     # Training & preprocessing scripts
├── Jenkinsfile             # CI/CD pipeline definition
├── Dockerfile.frontend     # Nginx + static assets build
├── Dockerfile.backend      # Python Flask API build
├── requirements.txt        # Python dependencies
└── README.md               # (this file)

🛠️ Prerequisites

GCP Project with:

GKE cluster

GCR (Google Container Registry)

GCS bucket for data/artifacts

IAM service account with roles: Kubernetes Engine Developer, Storage Object Viewer, Storage Admin

Jenkins Server with:

Docker installed

GCP SDK & gcloud authenticated

kubectl configured for the GKE cluster

🔧 Setup & Deployment

1. Clone the Repository

git clone https://github.com/your-org/anime-recommender.git
cd anime-recommender

2. Configure Environment Variables

Create a .env file or use Kubernetes Secrets:

GCS_BUCKET=gs://your-bucket
REDIS_HOST=redis.example.com
REDIS_PORT=6379
MODEL_PATH=/mnt/models/recommender

3. CI/CD with Jenkins

Jenkinsfile defines stages:

Checkout from Git

Build Docker images (frontend & backend)

Unit Tests (pytest for backend)

Push images to GCR

Deploy to GKE using kubectl apply

Ensure Jenkins credentials include a Service Account JSON for GCP tasks.

4. Kubernetes Deployment

Apply manifests under deployments/:

kubectl apply -f deployments/frontend-deployment.yaml
kubectl apply -f deployments/backend-deployment.yaml
kubectl apply -f deployments/redis-deployment.yaml
kubectl apply -f deployments/service.yaml

5. Access the Application

Once Pods are running, find the external IP:

kubectl get svc anime-recommender

Open your browser at http://<EXTERNAL_IP>/.

🧪 Testing

Unit tests: Under backend/tests/, run:

pytest --maxfail=1 --disable-warnings -q

Model validation: Notebook ml/evaluate_model.ipynb shows performance metrics and sample recommendations.

🚀 Scaling & Monitoring

Horizontal Pod Autoscaling for backend API based on CPU usage.

Stackdriver (Cloud Monitoring & Logging) for metrics and logs.

Redis Cluster for high-availability and low-latency embedding lookup.

📄 License

This project is released under the MIT License. See LICENSE for details.

👥 Contributors

Mayank Rajput – Design, Implementation, MLOps

Your Team – Reviews, Testing, UX
