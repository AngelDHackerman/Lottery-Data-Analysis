# CloudWatch Alarm to detect errors in Lambda Functions 
resource "aws_cloudwatch_metric_alarm" "name" {
  alarm_name            = "LambdaErrorAlarm-${var.environment}"
  comparison_operator   = "GreaterThanThreshold"
  evaluation_periods    = 1
  metric_name           = "Errors"
  namespace             = "AWS/Lambda"
  period                = 60
  statistic             = "Sum"
  threshold             = 1
  alarm_description     = "This alarm activates when a lambda function has errors"
  alarm_actions         = [aws_sns_topic.lambda_alerts.arn]

  dimensions = {
    FunctionName = "lottery-lambda-${var.environment}"
  }
}