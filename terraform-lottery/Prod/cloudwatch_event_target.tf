# resource "aws_cloudwatch_event_target" "trigger_state_machine" {
#   rule      = aws_cloudwatch_event_rule.weekly_trigger.name
#   target_id = "start-lottery-etl-pipeline"
#   arn       = aws_sfn_state_machine.pipeline_state_machine.arn
#   role_arn  = aws_iam_role.eventbridge_to_sfn_role.arn
# }
