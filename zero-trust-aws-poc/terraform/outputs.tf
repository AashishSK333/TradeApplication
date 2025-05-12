output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.client.id
}

output "api_url" {
  value = "${aws_apigatewayv2_stage.api.invoke_url}"
}

output "website_url" {
  value = "http://${aws_s3_bucket.website.website_endpoint}"
}