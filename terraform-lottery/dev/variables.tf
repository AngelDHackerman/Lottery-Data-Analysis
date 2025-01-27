variable "aws_region" {
  description = "AWS region"
  type = string
}

variable "aws_region_2" {
  description = "AWS region"
  type = string
}

variable "aws_availability_zone_1" {
  description = "AWS availability zone 1"
  type = string
}

variable "aws_availability_zone_2" {
  description = "AWS availability zone 2"
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

variable "s3_lambda_bucket_arn_dev" {
  description = "s3 for the ETL lambdas"
  type = string
}

variable "logs_access" {
  description = "log access in AWS"
  type = string
}

variable "public_ip" {
  description = "ip allowed to access AWS"
  type = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default = "10.0.0.0/16"
}

variable "private_subnet_1_cidr" {
  description = "CIDR block for the first private subnet"
  default = "10.0.1.0/24"
}

variable "private_subnet_2_cidr" {
  description = "CIDR block for the second private subnet"
  default     = "10.0.2.0/24"
}

variable "secrets_manager_arn_dev" {
  description = "AWS Secrets manager"
  type = string
}

variable "endpoint_db_dev" {
  description = "enpoint for the dev database"
  type = string
}

variable "arn_db_dev" {
  description = "arn for the dev databse"
  type = string
}

variable "db_port" {
  description = "database port"
  type = string
}

variable "db_availability_zone_dev" {
  description = "database dev availability zone"
  type = string
}