variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "db_endpoint" { type = string }

resource "aws_ecs_cluster" "main" {
  name = "kyc-cluster-${var.environment}"
}

# Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/kyc-service-${var.environment}"
  retention_in_days = 14
}

# API Task Definition (FastAPI Backend)
resource "aws_ecs_task_definition" "backend_api" {
  family                   = "kyc-backend-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024" # 1 vCPU
  memory                   = "2048" # 2 GB
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "kyc-backend"
      image     = "nginx:latest" # Placeholder for actual ECR image
      essential = true
      portMappings = [{ containerPort = 8000, hostPort = 8000 }]
      environment = [
        { name = "DATABASE_URL", value = var.db_endpoint },
        { name = "AI_ENGINE_URL", value = "http://localhost:8001" } 
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "backend"
        }
      }
    },
    {
      name      = "ai-engine"
      image     = "nginx:latest" # Placeholder for AI engine image
      essential = true
      portMappings = [{ containerPort = 8001, hostPort = 8001 }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ai-engine"
        }
      }
    }
  ])
}

# Minimal IAM roles for the demo
resource "aws_iam_role" "ecs_execution" {
  name = "kyc-ecs-exec-role-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
  })
}
resource "aws_iam_role_policy_attachment" "ecs_exec" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "kyc-ecs-task-role-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
  })
}
