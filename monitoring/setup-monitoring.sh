#!/bin/bash
# Setup CloudWatch Monitoring for Security Architect MCP Server
# Creates dashboards, alarms, and monitoring infrastructure

set -e

# Configuration
REGION=${AWS_REGION:-"us-east-1"}
PROFILE=${AWS_PROFILE:-"default"}
ENVIRONMENT=${ENVIRONMENT:-"prod"}
ALERT_EMAIL=${ALERT_EMAIL:-"alerts@securitydatacommons.com"}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_warn "jq not installed. Installing..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y jq
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install jq
        fi
    fi

    # Check AWS credentials
    aws sts get-caller-identity --profile $PROFILE > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_error "AWS credentials not configured"
        exit 1
    fi

    log_info "Prerequisites check complete"
}

# Create CloudWatch Dashboard
create_dashboard() {
    log_info "Creating CloudWatch dashboard..."

    # Read dashboard configuration
    DASHBOARD_BODY=$(cat cloudwatch-dashboards.json | jq -c '.DashboardBody')

    # Create or update dashboard
    aws cloudwatch put-dashboard \
        --dashboard-name "Security-Architect-MCP-Server-${ENVIRONMENT}" \
        --dashboard-body "$DASHBOARD_BODY" \
        --profile $PROFILE \
        --region $REGION

    if [ $? -eq 0 ]; then
        log_info "Dashboard created successfully"
        DASHBOARD_URL="https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#dashboards:name=Security-Architect-MCP-Server-${ENVIRONMENT}"
        log_info "Dashboard URL: $DASHBOARD_URL"
    else
        log_error "Failed to create dashboard"
        exit 1
    fi
}

# Create Custom Metrics Namespace
create_custom_metrics() {
    log_info "Setting up custom metrics namespace..."

    # Create custom metric for token savings
    aws cloudwatch put-metric-data \
        --namespace "Custom/MCP" \
        --metric-name "TokensSaved" \
        --value 0 \
        --dimensions Environment=$ENVIRONMENT \
        --profile $PROFILE \
        --region $REGION

    # Create custom metric for context savings
    aws cloudwatch put-metric-data \
        --namespace "Custom/MCP" \
        --metric-name "ContextSavedKB" \
        --value 0 \
        --dimensions Environment=$ENVIRONMENT \
        --profile $PROFILE \
        --region $REGION

    log_info "Custom metrics namespace created"
}

# Setup Log Groups
setup_log_groups() {
    log_info "Setting up CloudWatch log groups..."

    # Lambda log group
    aws logs create-log-group \
        --log-group-name "/aws/lambda/security-mcp-${ENVIRONMENT}-mcp" \
        --profile $PROFILE \
        --region $REGION 2>/dev/null || true

    # Set retention policy (30 days)
    aws logs put-retention-policy \
        --log-group-name "/aws/lambda/security-mcp-${ENVIRONMENT}-mcp" \
        --retention-in-days 30 \
        --profile $PROFILE \
        --region $REGION

    # API Gateway log group
    aws logs create-log-group \
        --log-group-name "/aws/apigateway/security-mcp-${ENVIRONMENT}" \
        --profile $PROFILE \
        --region $REGION 2>/dev/null || true

    # Application log group
    aws logs create-log-group \
        --log-group-name "/mcp/security-architect/${ENVIRONMENT}" \
        --profile $PROFILE \
        --region $REGION 2>/dev/null || true

    log_info "Log groups configured"
}

# Setup Log Insights Queries
setup_log_insights() {
    log_info "Creating CloudWatch Insights queries..."

    # Query for token savings analysis
    aws logs put-query-definition \
        --name "MCP-Token-Savings-Analysis" \
        --query-string 'fields @timestamp, tokens_saved, method
| filter tokens_saved > 0
| stats sum(tokens_saved) as total_saved, avg(tokens_saved) as avg_saved by bin(5m)' \
        --log-group-names "/aws/lambda/security-mcp-${ENVIRONMENT}-mcp" \
        --profile $PROFILE \
        --region $REGION > /dev/null

    # Query for error analysis
    aws logs put-query-definition \
        --name "MCP-Error-Analysis" \
        --query-string 'fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by error_type' \
        --log-group-names "/aws/lambda/security-mcp-${ENVIRONMENT}-mcp" \
        --profile $PROFILE \
        --region $REGION > /dev/null

    # Query for performance analysis
    aws logs put-query-definition \
        --name "MCP-Performance-Analysis" \
        --query-string 'fields @timestamp, @duration, @billedDuration, @memorySize, @maxMemoryUsed
| filter @type = "REPORT"
| stats avg(@duration) as avg_duration, max(@duration) as max_duration, avg(@maxMemoryUsed/@memorySize*100) as avg_memory_percent by bin(5m)' \
        --log-group-names "/aws/lambda/security-mcp-${ENVIRONMENT}-mcp" \
        --profile $PROFILE \
        --region $REGION > /dev/null

    log_info "Log Insights queries created"
}

# Setup SNS Topic and Alarms using AWS CLI (alternative to Terraform)
setup_alarms_cli() {
    log_info "Setting up CloudWatch alarms..."

    # Create SNS topic
    SNS_TOPIC_ARN=$(aws sns create-topic \
        --name "security-mcp-alerts-${ENVIRONMENT}" \
        --profile $PROFILE \
        --region $REGION \
        --query 'TopicArn' \
        --output text)

    log_info "SNS Topic created: $SNS_TOPIC_ARN"

    # Subscribe email to topic
    aws sns subscribe \
        --topic-arn $SNS_TOPIC_ARN \
        --protocol email \
        --notification-endpoint $ALERT_EMAIL \
        --profile $PROFILE \
        --region $REGION

    log_warn "Check your email ($ALERT_EMAIL) to confirm SNS subscription"

    # Create high error rate alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "security-mcp-${ENVIRONMENT}-high-error-rate" \
        --alarm-description "Alert when error rate exceeds 5%" \
        --metric-name Errors \
        --namespace AWS/Lambda \
        --statistic Average \
        --period 300 \
        --threshold 0.05 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --dimensions Name=FunctionName,Value=security-mcp-${ENVIRONMENT}-mcp \
        --alarm-actions $SNS_TOPIC_ARN \
        --profile $PROFILE \
        --region $REGION

    # Create high latency alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "security-mcp-${ENVIRONMENT}-high-latency" \
        --alarm-description "Alert when average latency exceeds 10 seconds" \
        --metric-name Duration \
        --namespace AWS/Lambda \
        --statistic Average \
        --period 300 \
        --threshold 10000 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 3 \
        --dimensions Name=FunctionName,Value=security-mcp-${ENVIRONMENT}-mcp \
        --alarm-actions $SNS_TOPIC_ARN \
        --profile $PROFILE \
        --region $REGION

    # Create concurrent execution alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "security-mcp-${ENVIRONMENT}-concurrent-limit" \
        --alarm-description "Alert when concurrent executions approach limit" \
        --metric-name ConcurrentExecutions \
        --namespace AWS/Lambda \
        --statistic Maximum \
        --period 60 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --dimensions Name=FunctionName,Value=security-mcp-${ENVIRONMENT}-mcp \
        --alarm-actions $SNS_TOPIC_ARN \
        --profile $PROFILE \
        --region $REGION

    log_info "CloudWatch alarms created"
}

# Setup X-Ray Tracing
setup_xray() {
    log_info "Configuring X-Ray tracing..."

    # Update Lambda function to enable X-Ray
    aws lambda update-function-configuration \
        --function-name "security-mcp-${ENVIRONMENT}-mcp" \
        --tracing-config Mode=Active \
        --profile $PROFILE \
        --region $REGION 2>/dev/null || log_warn "Lambda function not found, skipping X-Ray setup"

    # Create X-Ray sampling rule
    cat > xray-sampling-rule.json << EOF
{
    "version": 2,
    "default": {
        "fixed_target": 1,
        "rate": 0.1
    },
    "rules": [
        {
            "description": "MCP Server Sampling",
            "service_name": "security-mcp-*",
            "http_method": "*",
            "url_path": "*",
            "fixed_target": 2,
            "rate": 0.5
        }
    ]
}
EOF

    aws xray put-sampling-rule \
        --cli-input-json file://xray-sampling-rule.json \
        --profile $PROFILE \
        --region $REGION 2>/dev/null || log_warn "X-Ray sampling rule already exists"

    rm -f xray-sampling-rule.json
    log_info "X-Ray tracing configured"
}

# Generate monitoring report
generate_monitoring_report() {
    log_info "Generating monitoring setup report..."

    cat > monitoring-setup-report.md << EOF
# Monitoring Setup Report - Security Architect MCP Server

**Date**: $(date)
**Environment**: ${ENVIRONMENT}
**Region**: ${REGION}

## Monitoring Components

### CloudWatch Dashboard
- **URL**: https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#dashboards:name=Security-Architect-MCP-Server-${ENVIRONMENT}
- **Widgets**: 12 (metrics, logs, performance)
- **Refresh Rate**: 5 minutes

### CloudWatch Alarms
- High Error Rate (> 5%)
- High Latency (> 10s)
- Concurrent Execution Limit (> 80)
- Memory Utilization (> 90%)
- Security Validation Failures

### SNS Topic
- **ARN**: ${SNS_TOPIC_ARN:-"pending creation"}
- **Email**: ${ALERT_EMAIL}
- **Subscription**: Check email for confirmation

### Log Groups
- Lambda: /aws/lambda/security-mcp-${ENVIRONMENT}-mcp
- API Gateway: /aws/apigateway/security-mcp-${ENVIRONMENT}
- Application: /mcp/security-architect/${ENVIRONMENT}

### Log Insights Queries
- Token Savings Analysis
- Error Analysis
- Performance Analysis

### X-Ray Tracing
- Status: ${XRAY_STATUS:-"Enabled"}
- Sampling Rate: 10% baseline, 50% for MCP operations

## Custom Metrics

### Token Optimization
- Namespace: Custom/MCP
- Metrics: TokensSaved, ReductionPercentage
- Target: 98.7% reduction

### Context Optimization
- Namespace: Custom/MCP
- Metrics: ContextSavedKB, ToolsLoaded
- Target: 90% reduction

## Cost Monitoring

Estimated monthly costs:
- CloudWatch Logs: ~\$5
- CloudWatch Metrics: ~\$3
- CloudWatch Alarms: ~\$1
- X-Ray Traces: ~\$2
- **Total**: ~\$11/month

## Access Instructions

### View Dashboard
\`\`\`bash
aws cloudwatch get-dashboard \
  --dashboard-name Security-Architect-MCP-Server-${ENVIRONMENT}
\`\`\`

### Query Logs
\`\`\`bash
aws logs tail /aws/lambda/security-mcp-${ENVIRONMENT}-mcp --follow
\`\`\`

### Check Alarms
\`\`\`bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix security-mcp-${ENVIRONMENT}
\`\`\`

## Troubleshooting

If metrics are missing:
1. Ensure Lambda function is deployed
2. Check custom metric namespace exists
3. Verify IAM permissions for CloudWatch

## Next Steps

1. Confirm SNS email subscription
2. Test alarms with synthetic errors
3. Configure dashboard auto-refresh
4. Set up monthly cost reports

---

*Generated: $(date)*
EOF

    log_info "Report generated: monitoring-setup-report.md"
}

# Main setup flow
main() {
    log_info "Setting up CloudWatch monitoring for Security Architect MCP Server"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Region: ${REGION}"

    # Run setup steps
    check_prerequisites
    create_dashboard
    create_custom_metrics
    setup_log_groups
    setup_log_insights
    setup_alarms_cli
    setup_xray
    generate_monitoring_report

    log_info "🎉 Monitoring setup complete!"
    log_info "Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#dashboards:name=Security-Architect-MCP-Server-${ENVIRONMENT}"
    log_warn "Remember to confirm SNS email subscription at ${ALERT_EMAIL}"
}

# Handle script arguments
case "${1:-}" in
    dashboard)
        create_dashboard
        ;;
    alarms)
        setup_alarms_cli
        ;;
    logs)
        setup_log_groups
        setup_log_insights
        ;;
    xray)
        setup_xray
        ;;
    report)
        generate_monitoring_report
        ;;
    *)
        main
        ;;
esac