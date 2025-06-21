# IAM Policies for Lambda, CloudTrail, CloudWatch and StepFuctions

# Policy: SageMaker S3 read-only for parquet files
resource "aws_iam_policy" "sagemaker_s3_read_policy" {
  name        = "lottery-sagemaker-s3-read-policy-${var.environment}"
  description = "Allows SageMaker to read raw and processed data"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow",
        Action    = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          var.s3_bucket_simple_data_storage_prod_arn,
          "${var.s3_bucket_simple_data_storage_prod_arn}/*"
        ]
      }
    ]
  })
}

# IAM Role for SageMaker Studio
resource "aws_iam_role" "sagemaker_execution_role" {
  name = "lottery-sagemaker-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement     = [{
      Effect      = "Allow", 
      Principal   = {
        Service   = "sagemaker.amazonaws.com"
      },
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "lottery-sagemaker-role-${var.environment}"
  }
}

resource "aws_iam_policy" "sagemaker_studio_admin_policy" {
  name        = "lottery-sagemaker-studio-admin-policy-${var.environment}"
  description = "Policy to allow SageMaker Studio to list and describe apps, domains, spaces, etc."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sagemaker:ListApps",
          "sagemaker:DescribeApp",
          "sagemaker:CreatePresignedDomainUrl",
          "sagemaker:ListUserProfiles",
          "sagemaker:ListDomains",
          "sagemaker:DescribeDomain",
          "sagemaker:ListSpaces",
          "sagemaker:DescribeUserProfile",
          "sagemaker:DescribeSpace",
          "sagemaker:AddTags",
          "sagemaker:CreateSpace",
          "sagemaker:UpdateSpace",
          "sagemaker:CreateApp",
          "sagemaker:DeleteApp",
          "sagemaker:DeleteSpace"
        ],
        Resource = "*"
      }
    ]
  })
}

# Attach policy to SageMaker execution role
resource "aws_iam_role_policy_attachment" "sagemaker_s3_read_attach" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = aws_iam_policy.sagemaker_s3_read_policy.arn
}

resource "aws_iam_role_policy_attachment" "sagemaker_admin_policy_attach" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = aws_iam_policy.sagemaker_studio_admin_policy.arn
}

# Attach AWS-managed policies for SageMaker
resource "aws_iam_role_policy_attachment" "sagemaker_full_access" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_full_access" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}
