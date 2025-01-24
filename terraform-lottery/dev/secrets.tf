resource "aws_secretsmanager_secret" "lottery_secret" {
  name = "lottery_secret_${var.environment}"
  description = "Secrets for Lotería Santa Lucía ${var.environment}"
}

resource "aws_secretsmanager_secret_version" "lottery_secret_value" {
  secret_id         = aws_secretsmanager_secret.lottery_secret.id
  secret_string     = jsonencode({
    username = var.db_username
    password = var.db_password
    db_host  = aws_db_instance.lottery_db.address
  })
}