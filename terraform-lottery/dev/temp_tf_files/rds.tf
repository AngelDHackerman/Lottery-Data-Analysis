# Create the RDS database instance with mysql
resource "aws_db_instance" "lottery_db_dev" {
  identifier            = "lottery-db-${var.environment}"
  allocated_storage     = 20
  engine                = "mysql"
  engine_version        = "8.0"
  instance_class        = "db.t3.micro"
  username              = var.db_username_dev
  password              = var.db_password_dev
  publicly_accessible   = false
  skip_final_snapshot   = true
  db_subnet_group_name  = var.lottery_db_subent_group # need to create subnets 
  vpc_security_group_ids = [aws_security_group.db_sg.id]
}

# Create a security group for the database
resource "aws_security_group" "db_sg" {
  name          = "lottery-db-sg-${var.environment}"
  description   = "Security group for Lottery DB"

  ingress = {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    cidr_blocks     = [var.public_ip]
  }
}