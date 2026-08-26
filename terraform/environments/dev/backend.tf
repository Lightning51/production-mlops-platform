terraform {
  backend "s3" {
    bucket       = "production-mlops-platform-terraform-state-664267706249"
    key          = "environments/dev/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}
