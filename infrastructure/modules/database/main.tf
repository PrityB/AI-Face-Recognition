variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

resource "aws_db_subnet_group" "kyc" {
  name       = "kyc-db-subnets-${var.environment}"
  subnet_ids = var.subnet_ids
}

# PostgreSQL Database for KYC Records Architecture
resource "aws_db_instance" "kyc_postgres" {
  identifier           = "kyc-db-${var.environment}"
  allocated_storage    = 20
  storage_type         = "gp3"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t4g.micro" # Cost effective for dev/demo
  db_name              = "kyc_db"
  username             = "postgres"
  password             = "Password123!" # Change in prod using Secrets Manager
  parameter_group_name = "default.postgres15"
  
  db_subnet_group_name   = aws_db_subnet_group.kyc.name
  skip_final_snapshot    = true # True for dev, False for prod
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.db.id]
}

resource "aws_security_group" "db" {
  name        = "kyc-db-sg-${var.environment}"
  description = "Allow inbound traffic from ECS only"
  vpc_id      = var.vpc_id

  ingress {
    description = "PostgreSQL Access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Allow from within VPC only
  }
}

output "endpoint" {
  value = aws_db_instance.kyc_postgres.endpoint
}
