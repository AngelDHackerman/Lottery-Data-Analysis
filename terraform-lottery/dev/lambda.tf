# Create 3 lambda functions for ETL lottery proyect
# Use AWS step functions for sequenced execution
# Use of AWS EventVridge for weekly execution 

# Create Lambda for Scraper Script 
resource "aws_lambda_function" "scraper_lambda" {
  function_name       = "scraper_lambda_${var.environment}"
  runtime             = "python3.9"
  handler             = "scraper.lambda_handler"
  role                = aws_iam_role.lambda-role.arn
  timeout             = 300
  memory_size         = 512

  s3_bucket           = aws_s3_bucket.lambda_bucket_dev.id
  s3_key              = "scraper_lambda.zip"
}