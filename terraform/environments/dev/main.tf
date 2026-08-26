data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

resource "aws_ecr_repository" "app" {
  name                 = var.project_name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}
module "networking" {
  source = "../../modules/networking"

  project_name = var.project_name
  environment  = var.environment

  vpc_cidr = "10.0.0.0/16"

  availability_zones = [
    "ap-south-1a",
    "ap-south-1b",
  ]

  public_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24",
  ]

  private_subnet_cidrs = [
    "10.0.11.0/24",
    "10.0.12.0/24",
  ]
}

module "security_groups" {
  source = "../../modules/security-groups"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.networking.vpc_id
}


module "iam" {
  source = "../../modules/iam"

  project_name = var.project_name
  environment  = var.environment
}

module "ecs" {
  source = "../../modules/ecs"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  ecr_repository_url = aws_ecr_repository.app.repository_url
  image_tag          = "1.0.0"

  vpc_id = module.networking.vpc_id

  private_subnet_ids = module.networking.private_subnet_ids

  ecs_security_group_id = module.security_groups.ecs_security_group_id

  execution_role_arn = module.iam.ecs_execution_role_arn
  task_role_arn      = module.iam.ecs_task_role_arn

  target_group_arn = module.alb.target_group_arn

  container_port = 8000

  cpu    = 512
  memory = 1024

  desired_count = 2
}

module "alb" {
  source = "../../modules/alb"

  project_name = var.project_name
  environment  = var.environment

  vpc_id = module.networking.vpc_id

  public_subnet_ids = module.networking.public_subnet_ids

  alb_security_group_id = module.security_groups.alb_security_group_id

  container_port = 8000

  certificate_arn = module.acm.certificate_arn
}

module "acm" {
  source = "../../modules/acm"

  domain_name    = "api.shubhanshudevlab.online"
  hosted_zone_id = "Z09279973GM8FIVOL5ZNZ"
}

resource "aws_route53_record" "api" {
  zone_id = "Z09279973GM8FIVOL5ZNZ"

  name = "api.shubhanshudevlab.online"
  type = "A"

  alias {
    name                   = module.alb.alb_dns_name
    zone_id                = module.alb.alb_zone_id
    evaluate_target_health = true
  }
}


module "github_actions" {
  source = "../../modules/github-actions"

  project_name = var.project_name
  environment  = var.environment

  ecr_repository_arn = aws_ecr_repository.app.arn

  execution_role_arn = module.iam.ecs_execution_role_arn
  task_role_arn      = module.iam.ecs_task_role_arn
}