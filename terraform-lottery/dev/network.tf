# Create VPC
resource "aws_vpc" "lottery_vpc" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = "lottery-vpc-${var.environment}"
  }
}

# Create subnets in 2 availability zones (AZs)
resource "aws_subnet" "private_subnet_1" {
  vpc_id                = aws_vpc.lottery_vpc.id
  cidr_block            = var.private_subnet_1_cidr
  availability_zone     = var.aws_availability_zone_1
  map_public_ip_on_launch = false

  tags = {
    Name = "Private Subnet 1"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id                = aws_vpc.lottery_vpc.id
  cidr_block            = var.private_subnet_2_cidr
  availability_zone     = var.aws_availability_zone_2
  map_public_ip_on_launch = false

  tags = {
    Name = "Private Subnet 2"
  }
}

# Create a group of subnets for the dabase in RDS
resource "aws_db_subnet_group" "lottery_db_subent_group" {
  name              = "lottery-db-subnet-group-${var.environment}"
  description       = "Subnet group for Lottery DB"
  subnet_ids        = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id] # add private subnets

  tags = {
    Name = "lottery-db-subnet-group-${var.environment}"
  }
}