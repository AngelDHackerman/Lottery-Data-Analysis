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
      {
        Sid: "AllowGlueJobExecution",
        Effect: "Allow",
        Action: [
          "glue:StartJobRun"
        ],
        Resource: "*"
      },
      {
        Sid: "AllowStartGlueCrawlers",
        Effect: "Allow",
        Action: [
          "glue:StartCrawler"
        ],
        Resource: "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_execution_policy_attachment" {
  role       = aws_iam_role.sfn_execution_role.name
  policy_arn = aws_iam_policy.sfn_execution_policy.arn
}