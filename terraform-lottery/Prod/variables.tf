variable "aws_account_id" {
  description = "AWS account id"
  type = string
}

variable "aws_region" {
  description = "AWS region"
  type = string
}

variable "aws_region_2" {
  description = "AWS region"
  type = string
}

variable "aws_availability_zone_a" {
  description = "AWS availability zone 1"
  type = string
}

variable "aws_availability_zone_b" {
  description = "AWS availability zone 2"
  type = string
}

variable "s3_bucket_objects_arn" {
  description = "objects inside the bucket s3 ELIMINAR ESTE BUCKET"
  type = string
}

variable "s3_bucket_partitioned_data_storage_prod_arn"{
  description = "arn for the bucket where the raw and process data for Loteria Santa Lucia can be found"
  type = string
}
variable "s3_bucket_simple_data_storage_prod_arn"{
  description = "bucket for EDA data"
  type = string
}

variable "environment" {
  description = "environment of terraform"
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

variable "lottery_internet_gateway_id" {
  description = "ID for the Lottery internet gateway"
  type = string
}
variable "lottery_route_table_id" {
  description = "ID for the lottery route table"  
  type = string
}
variable "lottery_sagemaker_execution_role_prod_arn" {
  description = "ARN for SageMaker Execution Role"
  type = string
}
variable "public_subnet_1_cidr" {
  default = "10.0.3.0/24"
}
variable "enable_internet" {
  type    = bool
  default = false            # cambia a true cuando necesites pip/GitHub, etc.
}
variable "lambdas_path_local" {
  type = string
}
variable "s3_bucket_partitioned_name" {
  type = string
  description = "Nombre del bucket particionado sin ARN"
}
variable "s3_bucket_simple_name" {
  type = string
  description = "Nombre del bucket simple sin ARN"
}
variable "scrape_do_token" {
  type = string
  description = "token access for scrape.do"
}