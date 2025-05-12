variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name prefix"
  type        = string
  default     = "zero-trust-poc"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}