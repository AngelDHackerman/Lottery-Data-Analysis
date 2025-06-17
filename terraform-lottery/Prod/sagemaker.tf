# -----------------------------
# SageMaker Studio Domain
# -----------------------------
resource "aws_sagemaker_domain" "lottery_domain" {
  domain_name               = "lottery-sagemaker-${var.environment}"
  auth_mode                 = "IAM"
  vpc_id                    = aws_vpc.lottery_vpc.id

  # Usa ambas subredes privadas
  subnet_ids                = [
    aws_subnet.private_subnet_1.id,
    aws_subnet.private_subnet_2.id
  ]

  # Requiere acceso solo dentro del VPC (no usa internet directamente)
  app_network_access_type   = "VpcOnly"

  default_user_settings {
    execution_role = var.lottery_sagemaker_execution_role_prod_arn

    jupyter_server_app_settings {
      default_resource_spec {
        instance_type = "system"
      }
    }
  }

  tags = {
    Name = "lottery-sagemaker-${var.environment}"
  }
}

# -----------------------------
# SageMaker User Profile
# -----------------------------
resource "aws_sagemaker_user_profile" "lottery_user" {
  domain_id         = aws_sagemaker_domain.lottery_domain.id
  user_profile_name = "lottery-analyst"

  user_settings {
    execution_role = var.lottery_sagemaker_execution_role_prod_arn
  }
}
