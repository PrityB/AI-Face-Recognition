variable "environment" { type = string }
variable "bucket_name_prefix" { type = string }

# S3 Bucket for securely storing KYC documents (Passports, ID cards)
resource "aws_s3_bucket" "kyc_docs" {
  bucket = "${var.bucket_name_prefix}-documents-${var.environment}"
}

# Block public access entirely for PII security
resource "aws_s3_bucket_public_access_block" "kyc_docs" {
  bucket                  = aws_s3_bucket.kyc_docs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable AES256 server-side encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "kyc_docs" {
  bucket = aws_s3_bucket.kyc_docs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket for Machine Learning models and training data
resource "aws_s3_bucket" "kyc_models" {
  bucket = "${var.bucket_name_prefix}-ml-models-${var.environment}"
}

output "document_bucket_name" {
  value = aws_s3_bucket.kyc_docs.bucket
}

output "training_bucket_name" {
  value = aws_s3_bucket.kyc_models.bucket
}
