Overview
This application is a FastAPI-based service for tracking activities. It uses PostgreSQL for data storage and Redis for Celery task queue management.

````
├── app/
│   ├── __init__.py
│   ├── database.py         
│   ├── helpers.py          
│   ├── main.py     
│   ├── models.py       
│   ├── routers.py    
│   ├── schemas.py    
│   └── tasks.py    
├── kubernetes/               
│   ├── configmap.yaml
│   ├── redis.yaml
│   ├── web-server.yaml
│   └── worker.yaml
├── Dockerfile          # Web application Dockerfile
├── worker.Dockerfile   # Celery worker Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
````

### Local Development with Docker Compose
1. Environment Setup
    - Update environment variables (if necessary). For example, add PostgreSQL connection string
2. Build and Run with Docker Compose
    - `docker-compose up --build`
3. Access the Application
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Kubernetes Deployment
For testing purposes I used `Minikube` for local Kubernetes cluster.
NOTE: To deploy these Kubernetes resources, you need to change image in kubernetes manifests for remote image in the image registry (like ECR or Docker Registry)
1. Minikube Setup (https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)
    - `minikube start`
2. Point shell to Minikube's Docker daemon 
   - `eval $(minikube docker-env)`
3. Build Images for Kubernetes 
   - `docker build -t app:latest .`
   - `docker build -t worker:latest -f worker.Dockerfile .`
4. Update ConfigMap data. For example, add RDS PostgreSQL connection string
5. Deploy to Kubernetes 
   - `kubectl apply -f kubernetes/`
6. Verify deployments 
   - `kubectl get pods`
   - `kubectl get services`
7. Access the Application
   - `kubectl port-forward service/web-service 8000:8000`
8. Access the Application 
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs