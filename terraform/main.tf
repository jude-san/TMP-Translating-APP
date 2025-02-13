resource "aws_lambda_function" "translate_Function" {
  function_name = "translate_Function"
  handler       = "index.handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec_role.arn

  filename = "function.zip" # Replace with your Lambda deployment package
  # source_code_hash = filebase64sha256("function.zip")
  source_code_hash = data.archive_file.lambda.output_base64sha256

  layers = [aws_lambda_layer_version.lambda_layer.arn]

  environment {
    variables = {
      REQUEST_BUCKET  = "${aws_s3_bucket.bucket1.bucket}"
      RESPONSE_BUCKET = "${aws_s3_bucket.bucket2.bucket}"
    }
  }
}


### Lambda Layer for dependencies - upload the dependencies as a zip file 
resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "layers_dependencies.zip"
  layer_name = "translate_denpencies_layer"

  compatible_runtimes = ["python3.11"]
}

### archive_file takes a local/directory and zips it up for the lambda function
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../script/function.py"
  output_path = "function.zip"
}

### archive_file takes a local/directory and zips it up for the lambda function
data "archive_file" "layers" {
  type        = "zip"
  source_dir  = "${path.module}/../script/package"
  output_path = "layers_dependencies.zip"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}


# IAM Policy for Lambda to access S3, Translate, and CloudWatch Logs
resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  description = "Policy for Lambda to access S3, Translate, and CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::${aws_s3_bucket.bucket1.bucket}/*"
        Resource = "arn:aws:s3:::${aws_s3_bucket.bucket2.bucket}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "translate:TranslateText"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach the IAM Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}


# resource "random_id" "bucket_suffix" {
#   byte_length = 8 # Increase length for more uniqueness
# }

## S3 Buckets
resource "aws_s3_bucket" "bucket1" {
  bucket = "translate-request-bucket" # Change to a unique bucket name

  tags = {
    Name        = "Translate_bucket"
    Environment = "Div"
  }
}
resource "aws_s3_bucket" "bucket2" {
  bucket = "translate-response-bucket" # Change to a unique bucket name

  tags = {
    Name        = "Translate_bucket"
    Environment = "Dev"
  }
}


### creating authorizer for API Gateway

## API Gateway
resource "aws_api_gateway_rest_api" "translate_api" {
  name        = "translate_api"
  description = "API Gateway for Lambda integration"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resource
resource "aws_api_gateway_resource" "my_resource" {
  rest_api_id = aws_api_gateway_rest_api.translate_api.id
  parent_id   = aws_api_gateway_rest_api.translate_api.root_resource_id
  path_part   = "translate"
}

# API Gateway Method
resource "aws_api_gateway_method" "post_method" {
  rest_api_id   = aws_api_gateway_rest_api.translate_api.id
  resource_id   = aws_api_gateway_resource.my_resource.id
  http_method   = "POST"
  authorization = "NONE"
}


# API Gateway Integration with Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.translate_api.id
  resource_id             = aws_api_gateway_resource.my_resource.id
  http_method             = aws_api_gateway_method.post_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.translate_Function.invoke_arn
}


# API Gateway Deployment
resource "aws_api_gateway_deployment" "translate_deployment" {
  rest_api_id = aws_api_gateway_rest_api.translate_api.id
  #   stage_name  = "prod"
  triggers = {
    # NOTE: The configuration below will satisfy ordering considerations,
    #       but not pick up all future REST API changes. More advanced patterns
    #       are possible, such as using the filesha1() function against the
    #       Terraform configuration file(s) or removing the .id references to
    #       calculate a hash against whole resources. Be aware that using whole
    #       resources will show a difference after the initial implementation.
    #       It will stabilize to only change when resources change afterwards.
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.my_resource.id,
      aws_api_gateway_method.post_method.id,
      aws_api_gateway_integration.lambda_integration.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_api_gateway_stage" "translate_stage" {
  deployment_id = aws_api_gateway_deployment.translate_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.translate_api.id
  stage_name    = "tanlate_prod"
}



# Lambda Permission for API Gateway
resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.translate_Function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.translate_api.execution_arn}/*"
  #   source_arn = "arn:aws:execute-api:${var.myregion}:${var.accountId}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.resource.path}"
  # }

}


resource "null_resource" "invoke_lambda" {
  triggers = {
    always_run = ""
  }

  provisioner "local-exec" {
    command = "aws lambda invoke --function-name ${aws_lambda_function.translate_Function.function_name} --payload fileb://../script/payload.json output.json"
  }
}



