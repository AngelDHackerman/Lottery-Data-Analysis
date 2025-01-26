# Create a secret in AWS Secrets manager

resource "aws_secretsmanager_secret" "lottery_secret" {
  name = "lottery_secret_${var.environment}"
  description = "Secrets for Lotería Santa Lucía ${var.environment}"
}

