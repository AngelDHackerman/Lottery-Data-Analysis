# upload code to S3
resource "aws_s3_object" "lambda_package" {
  bucket = aws_s3_bucket.lambda_code_zip.id
  key    = "lambda_package.zip"
  source = "${var.lambdas_path_local}"
  etag   = filemd5("${var.lambdas_path_local}")
}

# Lambda: Extractor 
resource "aws_lambda_function" "extractor_lambda" {
  function_name    = "lottery-extractor-${var.environment}"
  s3_bucket        = aws_s3_bucket.lambda_code_zip.id
  s3_key           = aws_s3_object.lambda_package.key
  source_code_hash = filebase64sha256("${var.lambdas_path_local}")
  handler          = "extractor.lambda_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = 120
  memory_size      = 1024
  role             = aws_iam_role.lambda_exec.arn

  environment {
    variables = {
      PARTITIONED_BUCKET    = var.s3_bucket_partitioned_data_storage_prod_arn
      SIMPLE_BUCKET         = var.s3_bucket_simple_data_storage_prod_arn
      REGION                = var.aws_region
    }
  }

  depends_on = [
    aws_s3_object.lambda_package,
    aws_iam_role_policy_attachment.lambda_basic
  ]

  tags = {
    Name        = "lottery-extractor-${var.environment}"
    Environment = var.environment
    Project     = "Lottery ETL"
    Owner       = "Angel Hackerman"   
  }
}

