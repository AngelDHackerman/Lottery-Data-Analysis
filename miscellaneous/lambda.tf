resource "aws_lambda_function" "lottery_lambda" {
  function_name     = "lotteroy_lambda_${var.environment}"
  runtime           = "python3.9"
  handler           = "handler.lambda_handler"
  role              = aws_iam_role.lambda_exec_role.arn
  timeout           = 10
  memory_size       = 128

  filename          = "lambda_function_.zip"

  environment {
    variables = {
      SECRET_NAME = aws_secretsmanager_secret.lottery_secret.name
      ENVIRONMENT = var.environment
    }
  }
}