# ETL Group, minimum access to S3, Secrets Manager and Lambda functions
resource "aws_iam_group" "etl_group" {
  name = "ETLGroup"
}

# Create User group policy as ETLPolicy
resource "aws_iam_group_policy" "etl_policy" {
  name  = "ETLPolicy"
  group = aws_iam_group.etl_group.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [
          var.s3_prod_bucket_arn, 
          var.s3_prod_bucket_objects_arn,
          var.s3_dev_bucket_arn,
          var.s3_dev_bucket_objects_arn
        ]
      },
      {
        Effect = "Allow"
        Action = ["secretsmanager:GetSecretValue"]
        Resource = "*" 
      },
      {
        Effect = "Allow"
        Action = ["lambda:InvokeFunction", "lambda:GetFunction"]
        Resource = "*"
      }
    ]
  })
}

# Mandatory use of MFA for the IAM users
resource "aws_iam_policy" "force_mfa" {
  name        = "ForceMFA"
  description = "Forzar el uso de MFA en IAM"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent" = "false"
          }
        }
      }
    ]
  })
}

resource "aws_iam_group_policy_attachment" "force_mfa_attachment" {
  group      = aws_iam_group.etl_group.name
  policy_arn = aws_iam_policy.force_mfa.arn
}

# Restricted IPs address, only the known IPs will be able to access
resource "aws_iam_policy" "restrict_ip_access" {
  name        = "RestrictIPAccess"
  description = "Restringir acceso de IAM a direcciones IP permitidas"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Deny"
        Action = "*"
        Resource = "*"
        Condition = {
          NotIpAddress = {
            "aws:SourceIp" = var.allowed_ip_ranges
          }
        }
      }
    ]
  })
}

resource "aws_iam_group_policy_attachment" "restrict_ip_attachment" {
  group      = aws_iam_group.etl_group.name
  policy_arn = aws_iam_policy.restrict_ip_access.arn
}


# Password policy each 90 days password should change
resource "aws_iam_account_password_policy" "password_policy" {
  minimum_password_length        = 12
  require_lowercase_characters   = true
  require_uppercase_characters   = true
  require_numbers                = true
  require_symbols                = true
  allow_users_to_change_password = true
  max_password_age               = 90
}
