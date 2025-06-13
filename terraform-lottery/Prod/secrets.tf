# Create a secret in AWS Secrets manager for the database

# Create the secret
resource "aws_secretsmanager_secret" "lottery_secret" {
  name = "lottery_secret_${var.environment}"
  description = "Secrets for Lotería Santa Lucía ${var.environment}"
}

# Upload the secrets to AWS
resource "aws_secretsmanager_secret_version" "lottery_secret_value" {
  secret_id           = aws_secretsmanager_secret.lottery_secret.id
  secret_string       = jsonencode({
    s3_bucket_raw     = var.s3_bucket_partitioned_data_storage_prod_arn
  })
}