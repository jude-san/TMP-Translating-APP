# Outputs
output "api_gateway_invoke_url" {
  value = aws_api_gateway_deployment.my_deployment.invoke_url
}

output "s3_bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}

output "lambda_function_name" {
  value = aws_lambda_function.my_lambda.function_name
}
