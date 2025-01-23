# ETL Group, minimum access to S3, Secrets Manager and Lambda functions
resource "aws_iam_group" "etl_group" {
  name = "ETLGroup"
}

resource "aws_iam_group_policy" "etl_policy" {
  name  = "ETLPolicy"
  group = aws_iam_group.etl_group.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [
          var.s3_prod_bucket_arn, 
          var.s3_prod_bucket_objects_arn,
          var.s3_dev_bucket_arn,
          var.s3_dev_bucket_objects_arn
        ]
      },
      {
        Effect = "Allow"
        Action = ["secretsmanager:GetSecretValue"]
        Resource = var.secrets_manager_arn
      },
      {
        Effect = "Allow"
        Action = ["lambda:InvokeFunction", "lambda:GetFunction"]
        Resource = [
          var.prod_lambda_arn,
          var.dev_lambda_arn
        ]
      }
    ]
  })
}
