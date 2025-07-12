resource "aws_athena_workgroup" "lottery_wg" {
  name = "lottery-wg"

  configuration {
    result_configuration {
      output_location = "${aws_s3_bucket.athena_results.arn}/"
    }
  }
}
