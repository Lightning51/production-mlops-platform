variable "aws_region" {
  description = "AWS region for the environment"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for AWS resources"
  type        = string
  default     = "production-mlops-platform"
}
