terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "AI-KYC-Platform"
      Environment = var.environment
    }
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# 1. Networking
module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
  vpc_cidr    = "10.0.0.0/16"
}

# 2. Storage
module "storage" {
  source = "./modules/storage"
  
  environment = var.environment
  bucket_name_prefix = "ai-kyc-docs"
}

# 3. Database
module "database" {
  source = "./modules/database"
  
  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
}

# 4. ECS Fargate (API & AI Inference)
module "ecs" {
  source = "./modules/ecs"
  
  environment = var.environment
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  db_endpoint = module.database.endpoint
}

# 5. SageMaker (Training)
module "sagemaker" {
  source = "./modules/sagemaker"
  
  environment      = var.environment
  training_bucket  = module.storage.training_bucket_name
}
