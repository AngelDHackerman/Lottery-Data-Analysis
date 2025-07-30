# resource "aws_cloudwatch_event_rule" "weekly_trigger" {
#   name                = "weekly-etl-lottery-trigger-${var.environment}"
#   description         = "Dispara la Step Function de ETL de la Lotería Santa Lucía cada semana"
#   schedule_expression = "cron(0 14 ? * 6 *)" # Cada sábado a las 8am hora Guatemala (UTC+0 14h)

#   tags = {
#     Environment = var.environment
#   }
# }
