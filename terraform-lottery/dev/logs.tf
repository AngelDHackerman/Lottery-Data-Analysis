# CloudWatch logGroup only for track the lambda functions 
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name                  = "/aws/lambda/lottery-lambda-${var.environment}" # using this sintax name for the hierarchy
  retention_in_days     = 90  

  tags = {
    Name = "lottery-lambda-logs-${var.environment}"
  }
}

# CloudWatch logGroup for track general events
resource "aws_cloudwatch_log_group" "cloudtrail_logs" {
  name                  = "/aws/cloudtrail/lottery-cloudtrail-${var.environment}"
  retention_in_days     = 90

  tags = {
    Name = "lottery-cloudtrail-logs-${var.environment}"
  }
}