variable "aws_region" {
  description = "AWS region"
  type = string
}

variable "s3_bucket_arn" {
  description = "S3 bucket for prod"
  type = string
}

variable "s3_bucket_objects_arn" {
  description = "Objects in the dev S3 bucket"
  type = string
}

variable "environment" {
  description = "production environment"
  type = string
}

variable "db_username" {
  description = "database username"
  type = string
}

variable "db_password" {
  description = "super secret password for database"
  type = string
}