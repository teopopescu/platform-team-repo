## Lambda Function Configuration
data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "lambda_read_secret" {
  name = "lambda-read-secret"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret",
        "secretsmanager:CreateSecret",
        "secretsmanager:PutSecret",
        "secretsmanager:PutSecretValue",
        "secretsmanager:TagResource",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
      ],
      Resource = ["*"]
    }]
  })
}

resource "aws_iam_role" "secret_sharing" {
  name               = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy_attachment" "attach_secret" {
  role       = aws_iam_role.secret_sharing.name
  policy_arn = aws_iam_policy.lambda_read_secret.arn
}

resource "aws_lambda_function" "secret_sharing" {
  function_name = "lmb-mercury-${var.env}-euwe1-${var.product_name}_service_secret-sharing"
  role          = aws_iam_role.secret_sharing.arn

  package_type = "Image"
  # image_uri = "${aws_ecr_repository.secret_sharing.repository_url}:latest"
  image_uri = "957129869060.dkr.ecr.eu-west-1.amazonaws.com/ecr-mercury-${var.env}-euwe1-shared-service_secret-sharing:latest"

  environment {
    variables = {
      PRODUCT_NAME         = var.product_name
      ENV                  = var.env
      CONTACT_NAME         = var.contact_name
      CONTACT_EMAIL        = var.contact_email
      ACCEPTED_PARTNER_IDS = jsonencode(var.accepted_partner_ids)
    }
  }

  timeout = 300

  architectures = ["x86_65"]
}


## API Gateway Configuration

resource "aws_apigatewayv2_api" "api" {
  name          = "agw-mercury-${var.env}-euwe1-${var.product_name}_service_secret-sharing"
  description   = "API Gateway for sharing secrets for ${var.product_name}."
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.secret_sharing.invoke_arn
  payload_format_version = "2.0"
}

# resource "aws_apigatewayv2_route" "route" {
#   api_id    = aws_apigatewayv2_api.api.id
#   route_key = "GET /"
#   target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
# }

resource "aws_apigatewayv2_route" "pgp" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /.well-known/pgp-key"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "secret" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /secrets/import"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "export" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "GET /secrets/export"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.secret_sharing.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}