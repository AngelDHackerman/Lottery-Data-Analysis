resource "aws_cloudwatch_event_rule" "weekly_etl_trigger" {
  name                = "lottery-etl-weekly-trigger-${var.environment}"
  schedule_expression = "cron(0 18 ? * MON *)" # Todos los lunes a las 12:00 PM Guatemala
  description         = "Trigger the lottery ETL Step Function every Monday at 12:00 PM GMT-6"
}

resource "aws_cloudwatch_event_target" "trigger_step_function" {
  rule      = aws_cloudwatch_event_rule.weekly_etl_trigger.name
  target_id = "StepFunctionLotteryETL"
  arn       = aws_sfn_state_machine.pipeline_state_machine.arn
  role_arn  = aws_iam_role.eventbridge_to_sfn_role.arn
}
