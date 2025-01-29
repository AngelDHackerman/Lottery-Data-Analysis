# Create a cloudTrail object for tracking activities in the lottery proyect

resource "aws_cloudtrail" "lottery_trail" {
  name              = "lottery-cloudtrail-${var.environment}"
  s3_bucket_name    = aws_s3_bucket.cloudtrail_logs.id

  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  event_selector {
    read_write_type             = "All"
    include_management_events   = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.cloudtrail_logs.arn}/"]
    }   
  }

  tags = {
    Name = "lottery-cloudtrail-${var.environment}"
  }
}