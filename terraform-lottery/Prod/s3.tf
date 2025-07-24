# # Create bucket for raw data (.txt files)
# resource "aws_s3_bucket" "lottery_raw_data" {
#   bucket = "lottery-partitioned-storage-${var.environment}"

#   lifecycle {
#     prevent_destroy = false
#   }

#   tags = {
#     Name        = "lottery-partitioned-storage-${var.environment}"
#     Environment = var.environment
#     Owner       = "Angel Hackerman"
#     Project     = "Lottery ETL"
#   }
# }

# resource "aws_s3_bucket" "lottery_data_simple" {
#   bucket = "lottery-data-simple-${var.environment}"

#   lifecycle {
#     prevent_destroy = false
#   }
#   tags = {
#     Name        = "lottery-simple-storage-${var.environment}"
#     Environment = var.environment
#     Owner       = "Angel Hackerman"
#     Project     = "Lottery ETL"
#   }
# }

# Bucket for Lambda code
resource "aws_s3_bucket" "lambda_code_zip" {
  bucket = "lambda-code-zip-${var.environment}"

  lifecycle {
    prevent_destroy = false
  }

  tags = {
    Name        = "lambda-code-zip-${var.environment}"
    Environment = var.environment
    Owner       = "Angel Hackerman"
    Project     = "Lottery ETL"
  }
}

# Bucket for Athena results
resource "aws_s3_bucket" "athena_results" {
  bucket            = "lottery-athena-results-${var.environment}"
  force_destroy     = true
  tags = {
    Name = "Athena Query Resutls"
  }
}

# Block public access 
resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket                    = aws_s3_bucket.athena_results.id
  block_public_acls         = true
  block_public_policy       = true
  ignore_public_acls        = true
  restrict_public_buckets   = true
}

# Encryption using SSE-S3
resource "aws_s3_bucket_server_side_encryption_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Remove results after 30 days
resource "aws_s3_bucket_lifecycle_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    id      = "expire-athena-results"
    status  =  "Enabled"
    filter {}
    expiration {
      days = 30
    }
  } 
}