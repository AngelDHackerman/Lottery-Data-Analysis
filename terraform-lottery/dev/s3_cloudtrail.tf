# Create a S3 bucket for storage of cloud trail logs

resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "lottery-cloudtrail-logs-${var.environment}"

  force_destroy = true # facilitates the cleaning if there are problems

  tags = {
    Name = "lottery-cloudtrail-logs-${var.environment}"
  }
}

# Enable versioning of the S3 bucket
resource "aws_s3_bucket_versioning" "cloudtrail_logs_versioning" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Encription of the bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_logs_encryption" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}