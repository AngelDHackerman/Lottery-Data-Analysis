variable "aws_region" {
  description = "Región de AWS"
  default     = "us-east-1"
}

# Credentials for production user
variable "prod_aws_access_key" {
  description = "AWS Access Key for production user"
  type        = string
  sensitive   = true
}

variable "prod_aws_secret_key" {
  description = "AWS Secret Key for production user"
  type        = string
  sensitive   = true
}

# Credentials for development user
variable "dev_aws_access_key" {
  description = "AWS Access key for development user"
  type        = string
  sensitive   = true
}

variable "dev_aws_secret_key" {
  description   = "AWS Access key for development user"
  type          = string
  sensitive     = true
}

variable "allowed_ip_ranges" {
  description = "List of allowed IPs"
  type        = list(string)
}

variable "iam_users" {
  description = "Users that require MFA"
  type        = list(string)
}

variable "s3_prod_bucket_arn" {
  description = "ARN of the main bucket"
  type        = string
}

variable "s3_dev_bucket_arn" {
  description = "ARN of the testing bucket"
  type        = string
}

variable "s3_prod_bucket_objects_arn" {
  description = "ARN for all the objects inside the S3 production bucket"
  type        = string
}

variable "s3_dev_bucket_objects_arn" {
  description = "ARN for all the objects inside the S3 testing bucket"
  type        = string
}

variable "secrets_manager_arn" {
  description = "ARN of the Secrets Manager for credentials"
  type = string
}

variable "prod_lambda_arn" {
  description = "ARN for the production lambda functions"
  type        = string
}

variable "dev_lambda_arn" {
  description = "ARN for the testing lambda functions"
  type        = string
}

variable "environment" {
  description = "Deployment Environment (prod or dev)"
  type        = string
}
