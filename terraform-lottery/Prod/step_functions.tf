# Create machine for the states of StepFunctions ETL, Santa Lucia Lottery project
resource "aws_sfn_state_machine" "lottery_etl_workflow" {
  name     = "lottery-etl-workflow-${var.environment}"
  role_arn = aws_iam_role.step_functions_role.arn
  type     = "STANDARD"

  definition = jsonencode({
    Comment = "Orquestation of the process of ETL of Santa Lucia Lottery",
    StartAt = "ScraperLambda",
    States = {
      "ScraperLambda" : {
        Type     = "Task",
        Resource = aws_lambda_function.scraper_lambda.arn,
        Next     = "TransformLambda",
        Retry    = [{ ErrorEquals = ["States.ALL"], IntervalSeconds = 2, MaxAttempts = 3, BackoffRate = 2 }]
      },
      "TransformLambda" : {
        Type     = "Task",
        Resource = aws_lambda_function.transform_lambda.arn
        Next     = "LoadLambda",
        Retry    = [{ ErrorEquals = ["States.ALL"], IntervalSeconds = 2, MaxAttempts = 3, BackoffRate = 2 }]
      },
      "LoadLambda" : {
        Type     = "Task",
        Resource = aws_lambda_function.load_lambda.arn
        End      = true,
        Retry    = [{ ErrorEquals = ["States.ALL"], IntervalSeconds = 2, MaxAttempts = 3, BackoffRate = 2 }]
      }
    }
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_functions_logs.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }
}
