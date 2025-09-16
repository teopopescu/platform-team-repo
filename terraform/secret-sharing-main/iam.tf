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