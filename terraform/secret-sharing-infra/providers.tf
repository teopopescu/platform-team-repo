terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.9.0"
    }
    docker = {
        source  = "kreuzwerker/docker"
        version = "3.6.2"
      }
  }
}

provider "aws" {
  region = var.region
}

terraform {
  backend "s3" {
    bucket = "tf-state-rm-awstest"
    key    = "va-test-secret-sharing-infra.tfstate"
    use_lockfile = true
  }
}