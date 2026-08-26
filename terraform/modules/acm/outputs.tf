output "certificate_arn" {
  description = "ACM certificate ARN"
  value       = aws_acm_certificate.api.arn
}

output "certificate_domain_name" {
  description = "Domain covered by the certificate"
  value       = aws_acm_certificate.api.domain_name
}