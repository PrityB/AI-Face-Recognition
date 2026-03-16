# Deployment Guide: AI Identity Verification

This guide outlines how to deploy the AI KYC Platform to AWS using the provided Terraform modules, or how to run it locally.

## Option 1: Local Development (Docker Compose)

The fastest way to test the platform.

1. Ensure Docker and docker-compose are installed.
2. In the project root, run:
   ```bash
   docker-compose build
   docker-compose up -d
   ```
3. The services are now available:
   - Backend API: `http://localhost:8000/docs`
   - AI Engine: `http://localhost:8001/docs`
   - PostgreSQL: `localhost:5432`

## Option 2: AWS Production Deployment (Terraform)

This provisions the full VPC, ECS Fargate clusters, S3 buckets, and RDS instances.

### Prerequisites
1. Install [Terraform](https://developer.hashicorp.com/terraform/downloads) (v1.5+)
2. Install the AWS CLI and configure credentials:
   ```bash
   aws configure
   ```

### Deployment Steps

1. **Initialize Terraform**
   ```bash
   cd infrastructure
   terraform init
   ```

2. **Validate and Plan**
   ```bash
   terraform validate
   terraform plan -out=tfplan
   ```

3. **Apply the Infrastructure**
   > **Note:** This will incur AWS costs. The exact cost depends on how long you leave the services running.
   ```bash
   terraform apply tfplan
   ```

4. **Push Docker Images to ECR**
   After Terraform creates the Elastic Container Registry (ECR), you must build and push your Docker images (`docs/Dockerfile.ai-engine` and `docs/Dockerfile.backend`) to those repositories so ECS can run them. 
   *(This step is automated via the GitHub Actions CI/CD pipeline if configured with your AWS credentials).*

### Teardown
To avoid ongoing AWS charges for the RDS database and NAT Gateways:
```bash
terraform destroy
```
