from transformer import transform
from extractor.aws_secrets import get_secrets

def lambda_handler(event, context):
    """
    AWS Lambda entrypoint for triggering the transformation process.
    """
    print("🔁 Trigger received in Lambda...")

    # Get bucket info
    secrets = get_secrets()
    partitioned_bucket = secrets["partitioned"]

    raw_prefix = "raw/"
    processed_prefix = "processed/"

    print(f"🎯 Starting transformation in bucket: {partitioned_bucket}")
    transform(partitioned_bucket, raw_prefix=raw_prefix, processed_prefix=processed_prefix)
    print("✅ Transformation completed.")

    return {
        "statusCode": 200,
        "body": "Transformation completed successfully"
    }
