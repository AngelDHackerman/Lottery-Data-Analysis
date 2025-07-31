# ----------
# Iam Access for Step Functions State Machine
# ----------
resource "aws_iam_role" "sfn_execution_role" {
  name = "sfn-lottery-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "states.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "sfn_execution_policy" {
  name = "sfn-lottery-policy-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid: "AllowInvokeExtractorLambda",
        Effect: "Allow",
        Action: [
          "lambda:InvokeFunction"
        ],
        Resource: "arn:aws:lambda:${var.aws_region}:${var.aws_account_id}:function:${var.extractor_lambda_name}"
      },

      # Glue Job (start + polling + abort opcional)
      {
        Sid: "AllowGlueJobExecution",
        Effect: "Allow",
        Action: [
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns",
          "glue:BatchStopJobRun"
        ],
        Resource: "*"
      },
      {
        Sid: "AllowStartGlueCrawlers",
        Effect: "Allow",
        Action: [
          "glue:StartCrawler",
          "glue:GetCrawler"
        ],
        Resource: "*"
      },
      {
        Sid    = "LogsForSFN",
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_execution_policy_attachment" {
  role       = aws_iam_role.sfn_execution_role.name
  policy_arn = aws_iam_policy.sfn_execution_policy.arn
}

# ----------
# Iam Access for EventBridge
# ----------
resource "aws_iam_role" "eventbridge_to_sfn_role" {
  name = "eventbridge-to-sfn-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "eventbridge_to_sfn_policy" {
  name = "eventbridge-to-sfn-policy-${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid: "AllowStartExecutionOfStateMachine",
        Effect: "Allow",
        Action: "states:StartExecution",
        Resource: aws_sfn_state_machine.pipeline_state_machine.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eventbridge_to_sfn_policy_attachment" {
  role       = aws_iam_role.eventbridge_to_sfn_role.name
  policy_arn = aws_iam_policy.eventbridge_to_sfn_policy.arn
}