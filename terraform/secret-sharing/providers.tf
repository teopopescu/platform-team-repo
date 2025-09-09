terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.9.0"
    }
  }
}

provider "aws" {
  region = var.region
}

terraform {
  backend "s3" {
    bucket = "tf-state-rm-awstest"
    key    = "va-test-secret-sharing.tfstate"
    use_lockfile = true
  }
}