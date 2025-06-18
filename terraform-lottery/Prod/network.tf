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
  tags = { Name = "priv-subnet-a-${var.environment}" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.lottery.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  tags = { Name = "priv-subnet-b-${var.environment}" }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.lottery.id
  cidr_block        = "10.0.3.0/24"
  map_public_ip_on_launch = true
  availability_zone = "us-east-1a"
  tags = { Name = "pub-subnet-${var.environment}" }
}

# Internet Gateway
# Create and associate the VPC for public outbound traffic 
# (although this Studio will be in private subnets).

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.lottery.id
  tags   = { Name = "lottery-igw-${var.environment}" }
}

# NAT Gateway
# In the public subnet with an Elastic IP.
# Allows private subnets to reach the internet 
# (for pip installs, updates, or optionally reading S3 without an endpoint).
resource "aws_eip" "nat_eip" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public.id
  tags          = { Name = "lottery-nat-${var.environment}" }
}

# Route Tables
# Public Table: 0.0.0.0/0 → igw
# Private Table: (a table that you then associate with your two private subnets)
# 0.0.0.0/0 → nat-gateway-id
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.lottery.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.lottery.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
}

resource "aws_route_table_association" "priv_a_assoc" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private_rt.id
}
resource "aws_route_table_association" "priv_b_assoc" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private_rt.id
}
