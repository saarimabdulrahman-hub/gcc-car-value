# =============================================================================
# CloudFront Module — CDN for API with TLS termination
# =============================================================================

locals {
  name = "gcc-car-value-${var.environment}"
}

resource "aws_cloudfront_distribution" "main" {
  enabled         = true
  is_ipv6_enabled = true
  http_version    = "http2and3"
  price_class     = var.environment == "production" ? "PriceClass_100" : "PriceClass_200"

  # --- Origin: ALB ---
  origin {
    domain_name = var.alb_dns_name
    origin_id   = "${local.name}-alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # --- Default Cache Behavior ---
  default_cache_behavior {
    target_origin_id       = "${local.name}-alb"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    compress               = true

    # API responses should not be cached by default
    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Origin", "Accept", "Content-Type"]

      cookies {
        forward = "all"
      }
    }
  }

  # --- Cache Behavior: Static Assets ---
  ordered_cache_behavior {
    path_pattern           = "/static/*"
    target_origin_id       = "${local.name}-alb"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]
    compress               = true

    min_ttl     = 0
    default_ttl = 86400    # 24 hours
    max_ttl     = 604800   # 1 week

    forwarded_values {
      query_string = false
      headers      = ["Origin"]

      cookies {
        forward = "none"
      }
    }
  }

  # --- Cache Behavior: Health Check (no cache) ---
  ordered_cache_behavior {
    path_pattern           = "/v1/health"
    target_origin_id       = "${local.name}-alb"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = false

    min_ttl     = 0
    default_ttl = 0
    max_ttl     = 0

    forwarded_values {
      query_string = false
      headers      = ["Origin"]

      cookies {
        forward = "none"
      }
    }
  }

  # --- Geo Restriction (GCC only for production) ---
  restrictions {
    geo_restriction {
      restriction_type = var.environment == "production" ? "whitelist" : "none"
      locations        = var.environment == "production" ? ["AE", "SA", "QA", "KW", "BH", "OM"] : []
    }
  }

  # --- TLS ---
  viewer_certificate {
    cloudfront_default_certificate = var.certificate_arn == null
    acm_certificate_arn            = var.certificate_arn
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = var.certificate_arn != null ? "sni-only" : null
  }

  # --- Custom Domain ---
  dynamic "aliases" {
    for_each = var.domain_name != null ? [var.domain_name] : []
    content {
      items = [aliases.value]
    }
  }

  tags = merge(var.tags, {
    Name = "${local.name}-cf"
  })
}
