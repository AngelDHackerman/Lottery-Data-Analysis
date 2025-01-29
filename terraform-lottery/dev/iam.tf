
# Policy for CloudWatch logs from Lambda
resource "aws_iam_policy" "lambda_cloudwatch_policy" {
  name        = "lottery_lambda_cloudwatch_policy_${var.environment}"
  description = "Allows Lambda to write logs into CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = aws_cloudwatch_log_group.lambda_logs.arn
    }]
  })
}

# Policy to access to S3 from Lambda
resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lottery_lambda_s3_policy_${var.environment}"
  description = "Allows Lambda to access S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${var.s3_lambda_bucket_arn_dev}/*"
    }]
  })
}

# Policy for secrets manager from lamda
resource "aws_iam_policy" "lambda_secrets_policy" {
  name        = "lottery_lambda_secrets_policy_${var.environment}"
  description = "Allows Lambda to retrieve secrets from AWS Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = aws_secretsmanager_secret.lottery_secret.arn
    }]
  })
}

# Policy for allow CloudTrail write logs in CloudWatch 


# Policy for Step Functions from Lambda

# resource "aws_iam_policy" "lambda_stepfunctions_policy" {
#   name        = "lottery_lambda_stepfunctions_policy_${var.environment}"
#   description = "Allows Lambda to start Step Functions executions"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect   = "Allow"
#       Action   = ["states:StartExecution"]
#       Resource = "*" # ARN for step functions here
#     }]
#   })
# }

# Create IAM Role for the lambda policy 
resource "aws_iam_role" "lambda_role" {
  name = "lottery_lambda_role_${var.environment}"

  # Allows lambda assume this role
  assume_role_policy = jsonencode({
    Version     = "2012-10-17"
    Statement   = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Create role allowing CloudTrail to write logs in CloudWatch
resource "aws_iam_role" "cloudtrail_logging_role" {
  name = "cloudtrail-logging-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

# Attach each policy to the IAM Role
resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_attach" {
  policy_arn = aws_iam_policy.lambda_cloudwatch_policy.arn
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy_attachment" "lambda_secrets_attach" {
  policy_arn = aws_iam_policy.lambda_secrets_policy.arn
  role       = aws_iam_role.lambda_role.name
}

# resource "aws_iam_role_policy_attachment" "lambda_stepfunctions_attach" {
#   policy_arn = aws_iam_policy.lambda_stepfunctions_policy.arn
#   role       = aws_iam_role.lambda_role.name
# }



# Attach the role to a lambda function

# resource "aws_lambda_function" "etl_lambda" {
#   function_name = "lottery_etl_lambda"
#   role          = aws_iam_role.lambda_role.arn
#   runtime       = "python3.9"
#   handler       = "lambda_function.lambda_handler"
#   filename      = "lambda_package.zip"
# }
