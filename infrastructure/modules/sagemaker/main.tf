variable "environment" { type = string }
variable "training_bucket" { type = string }

resource "aws_sagemaker_notebook_instance" "ml_dev" {
  name          = "kyc-ml-exploration-${var.environment}"
  role_arn      = aws_iam_role.sagemaker_execution_role.arn
  instance_type = "ml.t3.medium"
}

# IAM Role for SageMaker to construct and train models securely
resource "aws_iam_role" "sagemaker_execution_role" {
  name = "kyc-sagemaker-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_s3" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess" # Demo only. Scope down in prod.
}

resource "aws_iam_role_policy_attachment" "sagemaker_full" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

output "notebook_url" {
  value = aws_sagemaker_notebook_instance.ml_dev.url
}
