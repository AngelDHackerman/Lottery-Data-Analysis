resource "aws_cloudwatch_log_group" "lambda_logs" {
  name                  = "/aws/lambda/lottery-lambda-${var.environment}" # using this sintax name for the hierarchy
  retention_in_days     = 30  # Keep the logs for 30 days

  tags = {
    Name = "lottery-lambda-logs-${var.environment}"
  }
}