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

# Bucket policy for CloudTrail
resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow CloudTrail to write logs in the bucket
      {
        Sid       = "AllowCloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl"      = "bucket-owner-full-control"
            "aws:SourceAccount" = var.aws_account_id
          }
        }
      },
      # Allow CloudTrail to check the bucket with `s3:GetBucketAcl`
      {
        Sid       = "AllowCloudTrailBucketACL"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = aws_s3_bucket.cloudtrail_logs.arn
      },
      # Allow CloudTrail to check the policy of the bucket with `s3:ListBucket`
      {
        Sid       = "AllowCloudTrailListBucket"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:ListBucket"
        Resource  = aws_s3_bucket.cloudtrail_logs.arn
      },
      #   Block no secure access (only allow HTTPs connection.)
      {
        Sid       = "DenyNonSecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
