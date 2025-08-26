terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "github_org" {
  description = "GitHub organization name"
  type        = string
}

data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "github_actions_data_product" {
  name = "github-actions-data-product-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Condition = {
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/*-data-product:*"
          }
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Purpose = "GitHub Actions for Data Product repositories"
  }
}

resource "aws_iam_policy" "data_product_policy" {
  name        = "github-actions-data-product-policy"
  description = "Policy for data product repositories"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "data_product_policy" {
  role       = aws_iam_role.github_actions_data_product.name
  policy_arn = aws_iam_policy.data_product_policy.arn
}

resource "aws_iam_role" "github_actions_platform_team" {
  name = "github-actions-platform-team-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github.arn
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/platform-team-repo:ref:refs/heads/main"
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Purpose = "GitHub Actions for Platform Team repository"
  }
}

resource "aws_iam_policy" "platform_team_policy" {
  name        = "github-actions-platform-team-policy"
  description = "Policy for platform team repository with full deployment permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "rds:*",
          "secretsmanager:*",
          "iam:PassRole",
          "iam:GetRole",
          "iam:ListRoles"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          "arn:aws:s3:::terraform-state-*",
          "arn:aws:s3:::terraform-state-*/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "platform_team_policy" {
  role       = aws_iam_role.github_actions_platform_team.name
  policy_arn = aws_iam_policy.platform_team_policy.arn
}

output "data_product_role_arn" {
  description = "ARN of the data product GitHub Actions role"
  value       = aws_iam_role.github_actions_data_product.arn
}

output "platform_team_role_arn" {
  description = "ARN of the platform team GitHub Actions role"
  value       = aws_iam_role.github_actions_platform_team.arn
}