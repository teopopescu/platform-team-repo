resource "aws_ecr_repository" "secret_sharing" {
  name = "ecr-mercury-${var.env}-euwe1-shared-service_secret-sharing"

  image_tag_mutability = "MUTABLE"
#   image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
     scan_on_push = true
   }
}
