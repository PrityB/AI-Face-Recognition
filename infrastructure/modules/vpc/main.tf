variable "environment" { type = string }
variable "vpc_cidr" { type = string }

# Use official AWS VPC module internally
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.5.0"

  name = "kyc-vpc-${var.environment}"
  cidr = var.vpc_cidr

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true # Save costs in dev
  enable_vpn_gateway = false
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
}

output "public_subnet_ids" {
  value = module.vpc.public_subnets
}
