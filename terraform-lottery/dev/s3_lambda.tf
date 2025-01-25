# S3 bucket created for storage lambda functions

# Create Bucket
resource "aws_s3_bucket" "lambda_bucket_dev" {
  bucket = "lottery-lambda-bucket-${var.environment}"
}

# Protect the bucket
resource "aws_s3_bucket_public_access_block" "lambda_bucket_block" {
  bucket = aws_s3_bucket.lambda_bucket_dev.id

  block_public_acls     = true
  block_public_policy   = true
  ignore_public_acls    = true
  restrict_public_buckets = true
}

# Ownership of the bucket
resource "aws_s3_bucket_ownership_controls" "lambda_bucket_ownership" {
  bucket = aws_s3_bucket.lambda_bucket_dev.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}