# IAM Policies for Lambda, CloudTrail, CloudWatch and StepFuctions

# Policy to allow Lambda functions to write logs into CloudWatch Logs
resource "aws_iam_policy" "lambda-cloudwatch-policy" {
  name        = "lottery-lambda-cloudwatch-policy-${var.environment}"
  description = "Allows Lambda functions to write logs into CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = [
        "logs:CreateLogGroup", 
        "logs:CreateLogStream", 
        "logs:PutLogEvents"
        ]
      Resource = aws_cloudwatch_log_group.lambda_logs.arn
    }]
  })
}

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

# # Policy for StepFunctions to execute lambdas of the ETL
# resource "aws_iam_policy" "step_functions_lambda_policy" {
#   name          = "step_functions_lambda_policy_${var.environment}"
#   description   = "Allows step functions to execute lambdas of ETL"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect      = "Allow"
#       Action      = ["lambda:InvokeFunction"]  // Allows lambda invocation
#       Resource    = [
#         aws_lambda_function.scraper_lambda.arn,
#         aws_lambda_function.transform_lambda.arn,
#         aws_lambda_function.load_lambda.arn
#       ]
#     }]
#   })
# }

# Policy: Allow StepFunctions to write logs in CloudWatch logs 
resource "aws_iam_policy" "step_functions_logs_policy" {
  name        = "step_functions_logs_policy_${var.environment}"
  description = "Allows StepFunctions to write logs in CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Required for 'log delivery' setup at account level
        Effect = "Allow",
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.step_functions_logs.arn}:*"
      },
      {
        # Step Functions needs to describe log groups (usually at account level)
        Effect    = "Allow",
        Action    = [
          "logs:DescribeLogGroups"
        ],
        Resource = "*"
      }
    ]
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

# # Policy that allows EventBridge to start Step Funtions
# resource "aws_iam_policy" "eventbridge_step_functions_policy" {
#   name        = "eventbridge_step_functions_policy_${var.environment}"
#   description = "Allows execution of EventBridge weekly"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect   = "Allow"
#       Action   = ["states:StartExecution"]
#       Resource = aws_sfn_state_machine.lottery_etl_workflow.arn
#     }]
#   })
# }

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
          "sagemaker:CreateSpace" 
        ],
        Resource = "*"
      }
    ]
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

# Attach StepFunctions to write logs in CloudWatch policy to StepFunctions Role
resource "aws_iam_role_policy_attachment" "step_functions_logs_attach" {
  policy_arn  = aws_iam_policy.step_functions_logs_policy.arn
  role        = aws_iam_role.step_functions_role.name
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
