# Create rule of EventBridge for execute ETL Weekly
resource "aws_cloudwatch_event_rule" "weekly_etl_execution" {
  name                  = "weekly-etl-execution-${var.environment}"
  description           = "Execute the ETL of Loteria Santa Lucia weekly"
  schedule_expression   = "cron(0 12 ? * 3 *)" # Tuesday at 12:00 PM UTC
}

# Define the action of the rule, Execute Step Funtions
resource "aws_cloudwatch_event_target" "trigger_step_functions" {
  rule          = aws_cloudwatch_event_rule.weekly_etl_execution.name
  arn           = aws_sfn_state_machine.lottery_etl_workflow.arn
  role_arn      = aws_iam_role.eventbridge_role.arn  # crear role for event bridge
}