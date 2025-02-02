# Create VPC
resource "aws_vpc" "lottery_vpc" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = "lottery-vpc-${var.environment}"
  }
}

# Create private subnets in 2 availability zones (AZs)
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

# Create a security group for the database
resource "aws_security_group" "db_sg" {
  name          = "lottery-db-sg${var.environment}"
  description   = "Security group for Lottery DB"
  vpc_id        = aws_vpc.lottery_vpc.id # assign the security group to the VPC previously created

  # Allow entry connexions to DB only for the allowed IPs
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    cidr_blocks     = [var.public_ip]
  }

  # Allow all the outcoming traffic (normally necessary for RDS)
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lottery-db-sg-${var.environment}"
  }
}