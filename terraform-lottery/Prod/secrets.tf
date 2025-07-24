# Create a secret in AWS Secrets manager for the database

# # Create the secret
# resource "aws_secretsmanager_secret" "lottery_secret" {
#   name = "lottery_secret_${var.environment}_2"
#   description = "Secrets for Lotería Santa Lucía ${var.environment}"
# }

# # Upload the secrets to AWS
# resource "aws_secretsmanager_secret_version" "lottery_secret_value" {
#   secret_id           = aws_secretsmanager_secret.lottery_secret.id
#   secret_string       = jsonencode({
#     s3_bucket_partitioned_data_storage_prod_arn   = var.s3_bucket_partitioned_data_storage_prod_arn
#     s3_bucket_simple_data_storage_prod_arn        = var.s3_bucket_simple_data_storage_prod_arn
#     scrape_do_token                               = var.scrape_do_token
#   })
# }