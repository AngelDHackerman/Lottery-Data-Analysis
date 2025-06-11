# # Create 3 Lambda functions for ETL lottery project
# # Use AWS Step Functions for sequenced execution
# # Use AWS EventBridge for weekly execution 

# # Create Lambda for "Scraper" Script ETL
# resource "aws_lambda_function" "scraper_lambda" {
#   function_name = "scraper_lambda_${var.environment}"
#   runtime       = "python3.9"
#   handler       = "scraper.lambda_handler"
#   role          = aws_iam_role.lambda-role.arn
#   timeout       = 300
#   memory_size   = 256
#   architectures = ["x86_64"]

#   s3_bucket        = aws_s3_bucket.lambda_bucket_dev.id
#   s3_key           = "scraper_lambda.zip"
#   source_code_hash = data.aws_s3_object.scraper_lambda_code.etag
# }

# # Create Lambda for "Transform" script ETL
# resource "aws_lambda_function" "transform_lambda" {
#   function_name = "transform_lambda_${var.environment}"
#   runtime       = "python3.9"
#   handler       = "transform.lambda_handler"
#   role          = aws_iam_role.lambda-role.arn
#   timeout       = 300
#   memory_size   = 256
#   architectures = ["x86_64"]

#   s3_bucket        = aws_s3_bucket.lambda_bucket_dev.id
#   s3_key           = "transform_lambda.zip"
#   source_code_hash = data.aws_s3_object.transform_lambda_code.etag
# }

# # Create Lambda for "Loader" script ETL
# resource "aws_lambda_function" "load_lambda" {
#   function_name = "load_lambda_${var.environment}"
#   runtime       = "python3.9"
#   handler       = "load.lambda_handler"
#   role          = aws_iam_role.lambda-role.arn
#   timeout       = 300
#   memory_size   = 256
#   architectures = ["x86_64"]

#   s3_bucket        = aws_s3_bucket.lambda_bucket_dev.id
#   s3_key           = "load_lambda.zip"
#   source_code_hash = data.aws_s3_object.load_lambda_code.etag
# }

# # Get the hash of the ZIP files in order to detect changes
# data "aws_s3_object" "scraper_lambda_code" {
#   bucket = aws_s3_bucket.lambda_bucket_dev.id
#   key    = "scraper_lambda.zip"
# }

# data "aws_s3_object" "transform_lambda_code" {
#   bucket = aws_s3_bucket.lambda_bucket_dev.id
#   key    = "transform_lambda.zip"
# }

# data "aws_s3_object" "load_lambda_code" {
#   bucket = aws_s3_bucket.lambda_bucket_dev.id
#   key    = "load_lambda.zip"
# }
