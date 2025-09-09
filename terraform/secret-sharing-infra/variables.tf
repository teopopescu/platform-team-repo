variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "env" {
  description = "The environment for which the secret is being shared, e.g., dev, tst, uat, stg, prd."
  type        = string
  default = "dev"
}
  