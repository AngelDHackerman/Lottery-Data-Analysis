
# Allow lamddas to write logs into CloudWatch
resource "aws_iam_policy" "lambda_policy" {
  name        = "lottery_lambda_policy_${var.environment}"
  description = "Policy for ETL Lambdas"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = aws_cloudwatch_log_group.lambda_logs.arn
      }
    ]
  })
}
