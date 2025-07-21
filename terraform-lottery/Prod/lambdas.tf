# # Lambda: Extractor 
# resource "aws_lambda_function" "extractor_lambda" {
#   function_name         = "lottery-extractor"
#   handler               = "extractor.lambda_handler.lambda_hadler"
#   runtime               = "python3.12"
#   timeout               = 120
#   memory_size           = 1024
#   filename              = var.lambdas_path_local
#   source_code_hash      = filebase64sha256(var.lambdas_path_local)

#   role = aws_iam_role.lambda_exec.arn

#   environment {
#     variables = {
#       PARTITIONED_BUCKET    = var.s3_bucket_partitioned_data_storage_prod_arn
#       SIMPLE_BUCKET         = var.s3_bucket_simple_data_storage_prod_arn
#       REGION                = var.aws_region
#     }
#   }

#   depends_on = [ aws_iam_role_policy_attachment.lambda_basic ]
# }

# # Lambda: Transformer
# resource "aws_lambda_function" "transformer_lambda" {
#   function_name    = "lottery-transformer"
#   handler          = "transformer.lambda_handler.lambda_handler"
#   runtime          = "python3.12"
#   timeout          = 180
#   memory_size      = 1024
#   filename         = var.lambdas_path_local
#   source_code_hash = filebase64sha256(var.lambdas_path_local)

#   role = aws_iam_role.lambda_exec.arn

#   environment {
#     variables = {
#       PARTITIONED_BUCKET = var.s3_bucket_partitioned_data_storage_prod_arn
#       SIMPLE_BUCKET      = var.s3_bucket_simple_data_storage_prod_arn
#       REGION             = var.aws_region
#     }
#   }

#   depends_on = [aws_iam_role_policy_attachment.lambda_basic]
# }