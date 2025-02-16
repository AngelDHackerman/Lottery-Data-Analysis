# Create bucket for raw data (.txt files)
resource "aws_s3_bucket" "lottery_raw_data" {
  bucket = "lottery-raw-data-${var.environment}"
  
  force_destroy = true # facilitates the cleaning if there are problems

  tags = {
    Name        = "lottery-raw-data-${var.environment}"
    Environment = var.environment
    Owner       = "Angel Hackerman"
    Project     = "Lottery ETL"
  }
}

# Create bucket for processed data (.csv files)
resource "aws_s3_bucket" "lottery_processed_data" {
  bucket = "lottery-processed-data-${var.environment}"

  force_destroy = true # facilitates the cleaning if there are problems

  tags = {
    Name        = "lottery-processed-data-${var.environment}"
    Environment = var.environment
    Owner       = "Angel Hackerman"
    Project     = "Lottery ETL"
  }
}