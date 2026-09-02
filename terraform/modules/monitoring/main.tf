resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name        = "${var.name_prefix}-ecs-cpu-high"
  alarm_description = "ECS service CPU utilization is above 70%"

  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  datapoints_to_alarm = 2

  metric_name = "CPUUtilization"
  namespace   = "AWS/ECS"
  period      = 300
  statistic   = "Average"
  threshold   = 70

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name        = "${var.name_prefix}-ecs-memory-high"
  alarm_description = "ECS service memory utilization is above 80%"

  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  datapoints_to_alarm = 2

  metric_name = "MemoryUtilization"
  namespace   = "AWS/ECS"
  period      = 300
  statistic   = "Average"
  threshold   = 80

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name        = "${var.name_prefix}-alb-5xx"
  alarm_description = "ALB target is returning HTTP 5XX errors"

  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  datapoints_to_alarm = 2

  metric_name = "HTTPCode_Target_5XX_Count"
  namespace   = "AWS/ApplicationELB"
  period      = 300
  statistic   = "Sum"
  threshold   = 5

  dimensions = {
    LoadBalancer = local.load_balancer_dimension
    TargetGroup  = local.target_group_dimension
  }

  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_hosts" {
  alarm_name        = "${var.name_prefix}-alb-unhealthy-targets"
  alarm_description = "ALB has unhealthy ECS targets"

  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  datapoints_to_alarm = 2

  metric_name = "UnHealthyHostCount"
  namespace   = "AWS/ApplicationELB"
  period      = 60
  statistic   = "Maximum"
  threshold   = 0

  dimensions = {
    LoadBalancer = local.load_balancer_dimension
    TargetGroup  = local.target_group_dimension
  }

  treat_missing_data = "notBreaching"
}

locals {
  load_balancer_dimension = replace(
    var.alb_arn,
    "arn:aws:elasticloadbalancing:${var.aws_region}:${var.aws_account_id}:loadbalancer/",
    ""
  )

  target_group_dimension = replace(
    var.target_group_arn,
    "arn:aws:elasticloadbalancing:${var.aws_region}:${var.aws_account_id}:targetgroup/",
    ""
  )
}