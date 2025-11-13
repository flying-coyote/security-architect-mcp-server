# CloudWatch Alarms for Security Architect MCP Server
# Terraform configuration for production monitoring

# SNS Topic for Alerts
resource "aws_sns_topic" "mcp_alerts" {
  name = "security-mcp-alerts-${var.environment}"

  tags = {
    Environment = var.environment
    Service     = "Security-Architect-MCP"
    ManagedBy   = "Terraform"
  }
}

resource "aws_sns_topic_subscription" "mcp_alerts_email" {
  topic_arn = aws_sns_topic.mcp_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_sns_topic_subscription" "mcp_alerts_slack" {
  topic_arn = aws_sns_topic.mcp_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_notifier.arn
}

# High Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "security-mcp-${var.environment}-high-error-rate"
  alarm_description   = "Alert when error rate exceeds 5%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "Errors"
  namespace          = "AWS/Lambda"
  period             = "300"
  statistic          = "Average"
  threshold          = "0.05"
  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = "security-mcp-${var.environment}-mcp"
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]
  ok_actions    = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "High"
    Team     = "Security-Architecture"
  }
}

# High Latency Alarm
resource "aws_cloudwatch_metric_alarm" "high_latency" {
  alarm_name          = "security-mcp-${var.environment}-high-latency"
  alarm_description   = "Alert when P99 latency exceeds 10 seconds"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  threshold          = "10000"
  treat_missing_data = "notBreaching"

  metric_query {
    id          = "p99"
    return_data = true

    metric {
      metric_name = "Duration"
      namespace   = "AWS/Lambda"
      period      = "300"
      stat        = "p99"

      dimensions = {
        FunctionName = "security-mcp-${var.environment}-mcp"
      }
    }
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "Medium"
    Team     = "Security-Architecture"
  }
}

# Token Savings Below Threshold
resource "aws_cloudwatch_metric_alarm" "low_token_savings" {
  alarm_name          = "security-mcp-${var.environment}-low-token-savings"
  alarm_description   = "Alert when token savings drop below 90%"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "4"
  metric_name        = "ReductionPercentage"
  namespace          = "Custom/MCP"
  period             = "3600"
  statistic          = "Average"
  threshold          = "90"
  treat_missing_data = "breaching"

  dimensions = {
    Environment = var.environment
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "Low"
    Team     = "Security-Architecture"
  }
}

# Concurrent Execution Limit
resource "aws_cloudwatch_metric_alarm" "concurrent_execution_limit" {
  alarm_name          = "security-mcp-${var.environment}-concurrent-limit"
  alarm_description   = "Alert when concurrent executions approach limit"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "ConcurrentExecutions"
  namespace          = "AWS/Lambda"
  period             = "60"
  statistic          = "Maximum"
  threshold          = "80"  # Alert at 80% of 100 concurrent limit
  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = "security-mcp-${var.environment}-mcp"
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "High"
    Team     = "Security-Architecture"
  }
}

# Security Validation Failures
resource "aws_cloudwatch_metric_alarm" "security_validation_failures" {
  alarm_name          = "security-mcp-${var.environment}-security-failures"
  alarm_description   = "Alert on security validation failures (possible attack)"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "SecurityValidationFailures"
  namespace          = "Custom/MCP"
  period             = "300"
  statistic          = "Sum"
  threshold          = "10"
  treat_missing_data = "notBreaching"

  dimensions = {
    Environment = var.environment
  }

  alarm_actions = [
    aws_sns_topic.mcp_alerts.arn,
    aws_sns_topic.security_team_alerts.arn  # Also alert security team
  ]

  tags = {
    Severity = "Critical"
    Team     = "Security-Architecture"
    SecurityRelevant = "true"
  }
}

# Memory Utilization
resource "aws_cloudwatch_metric_alarm" "high_memory_utilization" {
  alarm_name          = "security-mcp-${var.environment}-high-memory"
  alarm_description   = "Alert when memory utilization exceeds 90%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name        = "MemoryUtilization"
  namespace          = "AWS/Lambda"
  period             = "300"
  statistic          = "Maximum"
  threshold          = "90"
  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = "security-mcp-${var.environment}-mcp"
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "Medium"
    Team     = "Security-Architecture"
  }
}

# Throttling Alarm
resource "aws_cloudwatch_metric_alarm" "throttles" {
  alarm_name          = "security-mcp-${var.environment}-throttles"
  alarm_description   = "Alert when Lambda function is being throttled"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "Throttles"
  namespace          = "AWS/Lambda"
  period             = "300"
  statistic          = "Sum"
  threshold          = "5"
  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = "security-mcp-${var.environment}-mcp"
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "High"
    Team     = "Security-Architecture"
  }
}

# API Gateway 5XX Errors
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "security-mcp-${var.environment}-api-5xx"
  alarm_description   = "Alert on API Gateway 5XX errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "5XXError"
  namespace          = "AWS/ApiGateway"
  period             = "300"
  statistic          = "Sum"
  threshold          = "10"
  treat_missing_data = "notBreaching"

  dimensions = {
    ApiName = "security-mcp-${var.environment}"
    Stage   = var.environment
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "High"
    Team     = "Security-Architecture"
  }
}

# Cost Anomaly Detection
resource "aws_cloudwatch_metric_alarm" "cost_anomaly" {
  alarm_name          = "security-mcp-${var.environment}-cost-anomaly"
  alarm_description   = "Alert when estimated daily cost exceeds threshold"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "4"
  metric_name        = "EstimatedCost"
  namespace          = "Custom/MCP"
  period             = "3600"
  statistic          = "Sum"
  threshold          = var.daily_cost_threshold
  treat_missing_data = "notBreaching"

  dimensions = {
    Environment = var.environment
  }

  alarm_actions = [aws_sns_topic.mcp_alerts.arn]

  tags = {
    Severity = "Medium"
    Team     = "Security-Architecture"
    CostCenter = var.cost_center
  }
}

# Composite Alarm for Service Health
resource "aws_cloudwatch_composite_alarm" "service_health" {
  alarm_name          = "security-mcp-${var.environment}-service-health"
  alarm_description   = "Overall health of Security Architect MCP Server"
  actions_enabled     = true

  alarm_rule = join(" OR ", [
    "ALARM(${aws_cloudwatch_metric_alarm.high_error_rate.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.high_latency.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.concurrent_execution_limit.alarm_name})",
    "ALARM(${aws_cloudwatch_metric_alarm.security_validation_failures.alarm_name})"
  ])

  alarm_actions = [
    aws_sns_topic.mcp_alerts.arn,
    aws_sns_topic.pagerduty_critical.arn  # Page on-call for composite alarm
  ]

  tags = {
    Severity = "Critical"
    Team     = "Security-Architecture"
    Composite = "true"
  }
}

# Variables
variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
}

variable "daily_cost_threshold" {
  description = "Daily cost threshold in USD"
  type        = number
  default     = 10
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "security-architecture"
}

# Outputs
output "sns_topic_arn" {
  value = aws_sns_topic.mcp_alerts.arn
  description = "ARN of SNS topic for MCP alerts"
}

output "dashboard_url" {
  value = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=Security-Architect-MCP-Server"
  description = "URL to CloudWatch dashboard"
}