# Create bucket for raw data (.txt files)
resource "aws_s3_bucket" "lottery_raw_data" {
  bucket = "lottery-partitioned-storage-${var.environment}"

  lifecycle {
    prevent_destroy = false
  }

  tags = {
    Name        = "lottery-partitioned-storage-${var.environment}"
    Environment = var.environment
    Owner       = "Angel Hackerman"
    Project     = "Lottery ETL"
  }
}

resource "aws_s3_bucket" "lottery_data_simple" {
  bucket = "lottery-data-simple-${var.environment}"

  lifecycle {
    prevent_destroy = true
  }
  tags = {
    Name        = "lottery-simple-storage-${var.environment}"
    Environment = var.environment
    Owner       = "Angel Hackerman"
    Project     = "Lottery ETL"
  }
}
