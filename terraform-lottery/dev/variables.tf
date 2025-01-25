variable "aws_region" {
  description = "AWS region"
  type = string
}

variable "s3_bucket_arn" {
  description = "development bucket"
  type = string
}

variable "s3_bucket_objects_arn" {
  description = "objects inside the bucket s3"
  type = string
}

variable "environment" {
  description = "environment of terraform"
  type = string
}

variable "db_username_dev" {
  description = "username of the database"
  type = string
}

variable "db_password_dev" {
  description = "super secret password of DB"
  type = string
}

variable "s3_lambda_bucket_arn" {
  description = "s3 for the ETL lambdas"
  type = string
}

variable "logs_access" {
  description = "log access in AWS"
  type = string
}