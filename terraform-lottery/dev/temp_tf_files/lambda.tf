# Create 3 lambda functions for ETL lottery proyect
# Use AWS step functions for sequenced execution
# Use of AWS EventVridge for weekly execution 

resource "aws_lambda_function" "scraper_lambda" {
  function_name       = "scraper_lambda_${var.environment}"
  runtime             = "python3.9"
  handler             = "scraper.lambda_handler"
  role                = aws_iam_role.lambda_exec_role.arn # need to create a IAM role
}