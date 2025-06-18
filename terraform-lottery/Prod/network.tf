# Create main VPC for Lottery Proyect
resource "aws_vpc" "lottery" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "lottery-vpc-${var.environment}" }
}

# Subnets 2 private for SageMaker Studio, 1 public for NAT Gateway
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.lottery.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = { Name = "priv-subnet-a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.lottery.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  tags = { Name = "priv-subnet-b" }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.lottery.id
  cidr_block        = "10.0.3.0/24"
  map_public_ip_on_launch = true
  availability_zone = "us-east-1a"
  tags = { Name = "pub-subnet" }
}

# Internet Gateway
# Create and associate the VPC for public outbound traffic 
# (although this Studio will be in private subnets).

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.lottery.id
  tags   = { Name = "lottery-igw" }
}
