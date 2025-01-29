# IAM Policies for Lambda and CloudTrail

# Policy to allow Lambda functions to write logs into CloudWatch Logs
resource "aws_iam_policy" "lambda-cloudwatch-policy" {
  name        = "lottery-lambda-cloudwatch-policy-${var.environment}"
  description = "Allows Lambda functions to write logs into CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = aws_cloudwatch_log_group.lambda_logs.arn
    }]
  })
}

# Policy to allow Lambda functions to access S3 buckets
resource "aws_iam_policy" "lambda-s3-policy" {
  name        = "lottery-lambda-s3-policy-${var.environment}"
  description = "Allows Lambda functions to read and write objects in S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${var.s3_lambda_bucket_arn_dev}/*"
    }]
  })
}

# Policy to allow Lambda functions to retrieve secrets from AWS Secrets Manager
resource "aws_iam_policy" "lambda-secrets-policy" {
  name        = "lottery-lambda-secrets-policy-${var.environment}"
  description = "Allows Lambda functions to retrieve secrets from AWS Secrets Manager"

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = aws_secretsmanager_secret.lottery_secret.arn
    }]
  })
}

# Policy to allow CloudTrail to write logs into CloudWatch Logs
# Policy for CloudTrail to write logs in CloudWatch Logs
resource "aws_iam_policy" "cloudtrail-cloudwatch-policy" {
  name        = "lottery-cloudtrail-cloudwatch-policy-${var.environment}"
  description = "Allows CloudTrail to send logs to CloudWatch Logs"

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.cloudtrail_logs.arn}:*"
      }
    ]
  })
}

# Policy to allow CloudTrail to store logs in an S3 bucket
resource "aws_iam_policy" "cloudtrail-s3-policy" {
  name        = "lottery-cloudtrail-s3-policy-${var.environment}"
  description = "Allows CloudTrail to store logs in the designated S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.cloudtrail_logs.arn}/*"
    }]
  })
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda-role" {
  name = "lottery-lambda-role-${var.environment}"

  # Allows AWS Lambda service to assume this role
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# IAM Role for CloudTrail logging
resource "aws_iam_role" "cloudtrail-logging-role" {
  name = "lottery-cloudtrail-logging-role-${var.environment}"

  # Allows AWS CloudTrail service to assume this role
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Attach policies to IAM Roles

# Attach policy for Lambda to write logs in CloudWatch
resource "aws_iam_role_policy_attachment" "lambda-cloudwatch-attach" {
  role       = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-cloudwatch-policy.arn
}

# Attach policy for Lambda to access S3
resource "aws_iam_role_policy_attachment" "lambda-s3-attach" {
  role       = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-s3-policy.arn
}

# Attach policy for Lambda to access Secrets Manager
resource "aws_iam_role_policy_attachment" "lambda-secrets-attach" {
  role       = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-secrets-policy.arn
}

# Attach policy for CloudTrail to write logs in S3
resource "aws_iam_role_policy_attachment" "cloudtrail-s3-attach" {
  role       = aws_iam_role.cloudtrail-logging-role.name
  policy_arn = aws_iam_policy.cloudtrail-s3-policy.arn
}

# Attach policy for CloudTrail to write logs in CloudWatch
resource "aws_iam_role_policy_attachment" "cloudtrail-cloudwatch-attach" {
  role       = aws_iam_role.cloudtrail-logging-role.name
  policy_arn = aws_iam_policy.cloudtrail-cloudwatch-policy.arn
}




# Attachment for AWS Step Functions
# resource "aws_iam_role_policy_attachment" "lambda_stepfunctions_attach" {
#   policy_arn = aws_iam_policy.lambda_stepfunctions_policy.arn
#   role       = aws_iam_role.lambda_role.name
# }