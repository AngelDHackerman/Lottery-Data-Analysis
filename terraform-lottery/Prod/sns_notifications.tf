# Create SNS topic for send alerts of errors in lambda functions
resource "aws_sns_topic" "lambda_alerts" {
  name = "lambda-alerts-${var.environment}"
}

# Subscription to SNS for recieve notifications via email
resource "aws_sns_topic_subscription" "name" {
  topic_arn     = aws_sns_topic.lambda_alerts.arn
  protocol      = "email"
  endpoint      = "${var.cloudWatch_email}"
}