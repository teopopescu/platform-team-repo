variable "product_name" {
  description = "The name of the product."
  type        = string
}

variable "env" {
  description = "The environment for which the secret is being shared, e.g., dev, tst, uat, stg, prd."
  type        = string
}

variable "allowed_cidrs" {
  type    = list(string)
  default = ["203.0.113.0/24", "198.51.100.10/32"]
}

variable "contact_email" {
  description = "The email address associated with the product."
  type        = string
}

variable "contact_name" {
  description = "The name of the contact for the product."
  type        = string
}

variable "accepted_partner_ids" {
  description = "The list of accepted partner IDs for the product."
  type = list(object({
    id   = string
    name = string
    public_key = string
  }))
}
