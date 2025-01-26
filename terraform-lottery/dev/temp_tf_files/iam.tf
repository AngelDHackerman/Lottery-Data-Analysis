# Create role for ETL lambda functions

resource "aws_iam_role" "lambda_exec_role" {
  name = "lottery_lambda_exec_role${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "lottery_lambda_policy_${var.environment}"
  description = "Policy for ETL Lambdas"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${var.s3_lambda_bucket_arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = aws_secretsmanager_secret.lottery_secret.arn # Create el secreto de AWS Secrets manager. 
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreatelogStream", "logs:PutLogEvents"]
        Resource = var.logs_access
      },
      {
        Effect   = "Allow"
        Action   = ["states:StartExecution"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role          = aws_iam_role.lambda_exec_role.name
  policy_arn    = aws_iam_policy.lambda_policy.arn
}