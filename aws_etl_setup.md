# 🚀 Configuración de ETL para Lotería Santa Lucía en AWS con Terraform

Este documento describe cómo configurar un proceso ETL utilizando **AWS Lambda, AWS Step Functions y AWS EventBridge** en un entorno gestionado con **Terraform**.

---

## **📌 Arquitectura del ETL**

El flujo de trabajo sigue tres etapas principales:

1. **`scraper_lambda`** → Descarga los datos de la lotería desde la fuente web.
2. **`transform_lambda`** → Limpia y transforma los datos obtenidos.
3. **`load_lambda`** → Guarda los datos en **Amazon RDS** o **S3**.

El proceso es orquestado con **AWS Step Functions**, asegurando que cada paso se ejecute en orden y maneje errores correctamente.

Un **cron job en AWS EventBridge** programa la ejecución automática **una vez por semana**.

---

## **1️⃣ Subir Código de las 3 Lambdas a S3**
Antes de desplegar las funciones Lambda, sube el código empaquetado a S3:

```sh
zip scraper_lambda.zip scraper_lambda.py
zip transform_lambda.zip transform_lambda.py
zip load_lambda.zip load_lambda.py

aws s3 cp scraper_lambda.zip s3://lottery-lambda-bucket-dev/
aws s3 cp transform_lambda.zip s3://lottery-lambda-bucket-dev/
aws s3 cp load_lambda.zip s3://lottery-lambda-bucket-dev/
```

---

## **2️⃣ Crear IAM Role para las Lambdas**
Define permisos en `iam.tf`:

```hcl
resource "aws_iam_role" "lambda_exec_role" {
  name = "lottery_lambda_exec_role_${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}
```

Esta IAM Role permite a las Lambdas acceder a **S3, Secrets Manager y CloudWatch Logs**.

---

## **3️⃣ Crear las Funciones Lambda**
Define `lambda.tf`:

```hcl
resource "aws_lambda_function" "scraper_lambda" {
  function_name = "scraper_lambda_${var.environment}"
  runtime       = "python3.9"
  handler       = "scraper.lambda_handler"
  role          = aws_iam_role.lambda_exec_role.arn
  timeout       = 300
  memory_size   = 512

  s3_bucket = aws_s3_bucket.lambda_bucket_dev.id
  s3_key    = "scraper_lambda.zip"
}
```

Repite lo mismo para `transform_lambda` y `load_lambda`.

---

## **4️⃣ Crear AWS Step Function para Orquestar el ETL**

Define `step_function.tf`:

```hcl
resource "aws_sfn_state_machine" "etl_step_function" {
  name     = "lottery_etl_step_function_${var.environment}"
  role_arn = aws_iam_role.lambda_exec_role.arn

  definition = jsonencode({
    Comment = "Orchestrates ETL process for Lottery Data",
    StartAt = "ScrapeData",
    States = {
      ScrapeData = {
        Type = "Task",
        Resource = aws_lambda_function.scraper_lambda.arn,
        Next = "TransformData"
      },
      TransformData = {
        Type = "Task",
        Resource = aws_lambda_function.transform_lambda.arn,
        Next = "LoadData"
      },
      LoadData = {
        Type = "Task",
        Resource = aws_lambda_function.load_lambda.arn,
        End = true
      }
    }
  })
}
```

---

## **5️⃣ Programar la Ejecución Automática con EventBridge**

Define `scheduler.tf`:

```hcl
resource "aws_cloudwatch_event_rule" "weekly_etl_trigger" {
  name                = "weekly_etl_trigger_${var.environment}"
  description         = "Ejecuta el ETL de la Lotería Santa Lucía una vez a la semana"
  schedule_expression = "cron(0 12 ? * 2 *)"
}

resource "aws_cloudwatch_event_target" "etl_trigger" {
  rule = aws_cloudwatch_event_rule.weekly_etl_trigger.name
  arn  = aws_sfn_state_machine.etl_step_function.arn
  role_arn = aws_iam_role.lambda_exec_role.arn
}
```

🔹 **Esto ejecutará el ETL automáticamente cada martes a las 12:00 UTC.**

---

## **6️⃣ Ejecutar Terraform para Desplegar Todo**

Ejecuta los siguientes comandos:

```sh
cd terraform/dev
terraform init
terraform apply -var-file="terraform.tfvars"
```

🔹 **Esto creará en AWS:**
✅ **3 Lambdas (`scraper`, `transform`, `load`)**  
✅ **Un Step Function para orquestar las Lambdas**  
✅ **Un cron job en EventBridge para ejecutar el ETL automáticamente**  

---

## **🚀 Conclusión**
✅ **El ETL está modularizado en 3 Lambdas para mejor escalabilidad.**  
✅ **AWS Step Functions maneja la ejecución en orden (`scraper → transform → load`).**  
✅ **Un Cron Job en EventBridge ejecuta todo automáticamente cada semana.**  

🎯 **¡Con esta configuración, el ETL de la Lotería Santa Lucía será más eficiente, escalable y fácil de mantener!** 🚀🔥
