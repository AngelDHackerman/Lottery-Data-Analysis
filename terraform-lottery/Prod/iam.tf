# IAM Policies for Lambda, CloudTrail, CloudWatch and StepFuctions

# Policy to allow Lambda functions to access S3 buckets for the ETL .zip files
resource "aws_iam_policy" "lambda-s3-policy" {
  name        = "lottery-lambda-s3-policy-${var.environment}"
  description = "Allows Lambda functions to read and write objects in S3 bucket this is for the ETL .zip files "

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "s3:GetObject", 
        "s3:PutObject"
        ]
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



# Policy: SageMaker S3 read-only for parquet files
resource "aws_iam_policy" "sagemaker_s3_read_policy" {
  name        = "lottery-sagemaker-s3-read-policy-${var.environment}"
  description = "Allows SageMaker to read raw and processed data"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow",
        Action    = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          var.s3_bucket_prod_raw_and_processed_arn,
          "${var.s3_bucket_prod_raw_and_processed_arn}/*"
        ]
      }
    ]
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

# IAM Role for StepFunctions 
resource "aws_iam_role" "step_functions_role" {
  name = "lottery_step_functions_role_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "states.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

# IAM Role For EventBridge to execute Step Functions
resource "aws_iam_role" "eventbridge_role" {
  name = "eventbridge-step-functions-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

# IAM Role for SageMaker Studio
resource "aws_iam_role" "sagemaker_execution_role" {
  name = "lottery-sagemaker-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement     = [{
      Effect      = "Allow", 
      Principal   = {
        Service   = "sagemaker.amazonaws.com"
      },
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "lottery-sagemaker-role-${var.environment}"
  }
}

resource "aws_iam_policy" "sagemaker_studio_admin_policy" {
  name        = "lottery-sagemaker-studio-admin-policy-${var.environment}"
  description = "Policy to allow SageMaker Studio to list and describe apps, domains, spaces, etc."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sagemaker:ListApps",
          "sagemaker:DescribeApp",
          "sagemaker:CreatePresignedDomainUrl",
          "sagemaker:ListUserProfiles",
          "sagemaker:ListDomains",
          "sagemaker:DescribeDomain",
          "sagemaker:ListSpaces",
          "sagemaker:DescribeUserProfile",
          "sagemaker:DescribeSpace",
          "sagemaker:AddTags",
          "sagemaker:CreateSpace",
          "sagemaker:UpdateSpace",
          "sagemaker:CreateApp"
        ],
        Resource = "*"
      }
    ]
  })
}


# Attach policies to IAM Roles

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

# Attach policy to SageMaker execution role
resource "aws_iam_role_policy_attachment" "sagemaker_s3_read_attach" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = aws_iam_policy.sagemaker_s3_read_policy.arn
}

resource "aws_iam_role_policy_attachment" "sagemaker_admin_policy_attach" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = aws_iam_policy.sagemaker_studio_admin_policy.arn
}
