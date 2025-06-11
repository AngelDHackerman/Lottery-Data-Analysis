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

# Internet Gateway 
resource "aws_internet_gateway" "lottery_igw" {
  vpc_id = aws_vpc.lottery_vpc.id

  tags = {
    Name = "lottery-igw-${var.environment}"
  }
}

# Public Route Table 
resource "aws_route_table" "lottery_public_rt" {
  vpc_id = aws_vpc.lottery_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lottery_igw.id
  }

  tags = {
    Name = "lottery-public-rt-${var.environment}"
  }
}

# Attach the route table to a subnet
resource "aws_route_table_association" "public_subnet_1" {
  subnet_id       = aws_subnet.private_subnet_1.id
  route_table_id  = aws_route_table.lottery_public_rt.id
}