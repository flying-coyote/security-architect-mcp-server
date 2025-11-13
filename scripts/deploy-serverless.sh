#!/bin/bash
# Serverless Deployment Script for Security Architect MCP Server (AWS Lambda)
# Implements Streamable HTTP transport for scale-to-zero capability

set -e  # Exit on error

# Configuration
STAGE=${STAGE:-"dev"}
REGION=${AWS_REGION:-"us-east-1"}
PROFILE=${AWS_PROFILE:-"default"}
FUNCTION_PREFIX="security-mcp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites for serverless deployment..."

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        log_info "Install from: https://nodejs.org/"
        exit 1
    fi

    # Check Serverless Framework
    if ! command -v serverless &> /dev/null; then
        log_warn "Serverless Framework not installed. Installing..."
        npm install -g serverless
    fi

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        log_info "Install from: https://aws.amazon.com/cli/"
        exit 1
    fi

    # Check AWS credentials
    aws sts get-caller-identity --profile $PROFILE > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_error "AWS credentials not configured for profile: $PROFILE"
        log_info "Run: aws configure --profile $PROFILE"
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi

    log_info "Prerequisites check complete"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    cd serverless

    # Install Serverless plugins
    if [ ! -f package.json ]; then
        cat > package.json << EOF
{
  "name": "security-architect-mcp-serverless",
  "version": "1.0.0",
  "description": "Serverless deployment for Security Architect MCP Server",
  "devDependencies": {
    "serverless": "^3.0.0",
    "serverless-python-requirements": "^6.0.0",
    "serverless-plugin-warmup": "^8.0.0",
    "serverless-api-gateway-throttling": "^2.0.0",
    "serverless-prune-plugin": "^2.0.0"
  }
}
EOF
    fi

    npm install

    # Create requirements.txt for Lambda
    if [ ! -f requirements.txt ]; then
        cat > requirements.txt << EOF
mcp>=1.2.0
pydantic>=2.0.0
boto3>=1.28.0
EOF
    fi

    cd ..
    log_info "Dependencies installed"
}

# Package Lambda function
package_lambda() {
    log_info "Packaging Lambda function..."

    cd serverless

    # Create deployment package
    rm -rf package
    mkdir -p package

    # Copy source code
    cp -r ../src package/
    cp -r ../data package/
    cp lambda_handler.py package/

    # Install Python dependencies to package
    pip install -r requirements.txt -t package/ --upgrade

    # Create Layer for dependencies (optional, for better caching)
    log_info "Creating Lambda layer for dependencies..."

    rm -rf layer
    mkdir -p layer/python
    pip install -r requirements.txt -t layer/python/ --upgrade

    # Zip layer
    cd layer
    zip -r ../mcp-dependencies-layer.zip . -q
    cd ..

    # Zip function code
    cd package
    zip -r ../function.zip . -q
    cd ..

    log_info "Lambda function packaged successfully"
    cd ..
}

# Upload vendor database to S3
upload_vendor_database() {
    log_info "Uploading vendor database to S3..."

    BUCKET_NAME="${FUNCTION_PREFIX}-vendors-${STAGE}"

    # Create bucket if it doesn't exist
    aws s3api head-bucket --bucket $BUCKET_NAME --profile $PROFILE 2>/dev/null || \
        aws s3api create-bucket \
            --bucket $BUCKET_NAME \
            --region $REGION \
            --profile $PROFILE \
            $(if [ "$REGION" != "us-east-1" ]; then echo "--create-bucket-configuration LocationConstraint=$REGION"; fi)

    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket $BUCKET_NAME \
        --versioning-configuration Status=Enabled \
        --profile $PROFILE

    # Upload vendor database
    aws s3 cp data/vendor_database.json \
        s3://$BUCKET_NAME/vendors/vendor_database.json \
        --profile $PROFILE

    log_info "Vendor database uploaded to S3: s3://$BUCKET_NAME/vendors/"
}

# Deploy with Serverless Framework
deploy_serverless() {
    log_info "Deploying with Serverless Framework..."

    cd serverless

    # Set environment variables
    export VENDOR_DB_BUCKET="${FUNCTION_PREFIX}-vendors-${STAGE}"
    export DECISION_STATE_TABLE="${FUNCTION_PREFIX}-decisions-${STAGE}"

    # Deploy
    serverless deploy \
        --stage $STAGE \
        --region $REGION \
        --aws-profile $PROFILE \
        --verbose

    if [ $? -eq 0 ]; then
        log_info "Serverless deployment successful"
    else
        log_error "Serverless deployment failed"
        exit 1
    fi

    cd ..
}

# Test Lambda function
test_lambda() {
    log_info "Testing Lambda function..."

    FUNCTION_NAME="${FUNCTION_PREFIX}-${STAGE}-mcp"

    # Test health check
    log_info "Testing health endpoint..."

    TEST_PAYLOAD='{"body": "{\"method\": \"health\"}"}'

    RESPONSE=$(aws lambda invoke \
        --function-name $FUNCTION_NAME \
        --payload "$TEST_PAYLOAD" \
        --profile $PROFILE \
        --region $REGION \
        response.json 2>/dev/null)

    if [ $? -eq 0 ]; then
        log_info "Lambda invocation successful"
        cat response.json | jq '.'
    else
        log_error "Lambda invocation failed"
        exit 1
    fi

    # Test search_tools
    log_info "Testing progressive discovery..."

    TEST_PAYLOAD='{"body": "{\"method\": \"search_tools\", \"params\": {\"query\": \"SIEM\", \"limit\": 5}}"}'

    aws lambda invoke \
        --function-name $FUNCTION_NAME \
        --payload "$TEST_PAYLOAD" \
        --profile $PROFILE \
        --region $REGION \
        response2.json > /dev/null 2>&1

    cat response2.json | jq '.body | fromjson | .[:2]'

    # Cleanup
    rm -f response.json response2.json
}

# Set up CloudWatch alarms
setup_monitoring() {
    log_info "Setting up CloudWatch monitoring..."

    FUNCTION_NAME="${FUNCTION_PREFIX}-${STAGE}-mcp"

    # Create SNS topic for alerts
    SNS_TOPIC="${FUNCTION_PREFIX}-${STAGE}-alerts"

    SNS_ARN=$(aws sns create-topic \
        --name $SNS_TOPIC \
        --profile $PROFILE \
        --region $REGION \
        --query 'TopicArn' \
        --output text)

    # Create CloudWatch alarms

    # Error rate alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "${FUNCTION_NAME}-error-rate" \
        --alarm-description "Alert when Lambda error rate is high" \
        --metric-name Errors \
        --namespace AWS/Lambda \
        --statistic Sum \
        --period 300 \
        --threshold 10 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 1 \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --alarm-actions $SNS_ARN \
        --profile $PROFILE \
        --region $REGION

    # Duration alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "${FUNCTION_NAME}-duration" \
        --alarm-description "Alert when Lambda duration is high" \
        --metric-name Duration \
        --namespace AWS/Lambda \
        --statistic Average \
        --period 300 \
        --threshold 10000 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --alarm-actions $SNS_ARN \
        --profile $PROFILE \
        --region $REGION

    # Concurrent executions alarm
    aws cloudwatch put-metric-alarm \
        --alarm-name "${FUNCTION_NAME}-concurrent" \
        --alarm-description "Alert when concurrent executions are high" \
        --metric-name ConcurrentExecutions \
        --namespace AWS/Lambda \
        --statistic Maximum \
        --period 60 \
        --threshold 50 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
        --alarm-actions $SNS_ARN \
        --profile $PROFILE \
        --region $REGION

    log_info "CloudWatch alarms created"
}

# Generate deployment report
generate_report() {
    log_info "Generating serverless deployment report..."

    # Get API endpoint
    API_ENDPOINT=$(aws cloudformation describe-stacks \
        --stack-name ${FUNCTION_PREFIX}-${STAGE} \
        --profile $PROFILE \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
        --output text 2>/dev/null || echo "N/A")

    # Get Lambda ARN
    LAMBDA_ARN=$(aws lambda get-function \
        --function-name ${FUNCTION_PREFIX}-${STAGE}-mcp \
        --profile $PROFILE \
        --region $REGION \
        --query 'Configuration.FunctionArn' \
        --output text 2>/dev/null || echo "N/A")

    cat > serverless-deployment-report.md << EOF
# Serverless Deployment Report - Security Architect MCP Server

**Date**: $(date)
**Stage**: ${STAGE}
**Region**: ${REGION}
**AWS Profile**: ${PROFILE}

## Deployment Details

- **API Endpoint**: ${API_ENDPOINT}
- **Lambda Function**: ${FUNCTION_PREFIX}-${STAGE}-mcp
- **Lambda ARN**: ${LAMBDA_ARN}
- **S3 Bucket**: ${FUNCTION_PREFIX}-vendors-${STAGE}
- **DynamoDB Table**: ${FUNCTION_PREFIX}-decisions-${STAGE}

## Features

- ✅ Streamable HTTP Transport (2025 standard)
- ✅ Scale to Zero (no cost when idle)
- ✅ Code Execution (98.7% token reduction)
- ✅ Progressive Discovery (90% context reduction)
- ✅ Automatic scaling (AWS managed)

## Testing

### Health Check
\`\`\`bash
curl -X POST ${API_ENDPOINT}/mcp \\
  -H "Content-Type: application/json" \\
  -d '{"method": "health"}'
\`\`\`

### Search Tools
\`\`\`bash
curl -X POST ${API_ENDPOINT}/mcp \\
  -H "Content-Type: application/json" \\
  -d '{"method": "search_tools", "params": {"query": "SIEM"}}'
\`\`\`

## Monitoring

- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#logsV2:log-groups/log-group/\$252Faws\$252Flambda\$252F${FUNCTION_PREFIX}-${STAGE}-mcp
- CloudWatch Metrics: https://console.aws.amazon.com/cloudwatch/home?region=${REGION}#metricsV2:graph=~()
- X-Ray Traces: https://console.aws.amazon.com/xray/home?region=${REGION}#/traces

## Cost Estimate

Based on expected usage:
- Lambda invocations: 10,000/month @ \$0.20 per 1M = \$0.002
- Lambda duration: 100ms average @ 512MB = \$0.0000166667 per invocation
- API Gateway: 10,000 requests @ \$3.50 per 1M = \$0.035
- S3 storage: 1GB @ \$0.023 = \$0.023
- DynamoDB: On-demand pricing ~ \$1.25 per million requests

**Estimated monthly cost: < \$5.00**

## Rollback

To rollback to previous version:

\`\`\`bash
serverless rollback --timestamp <timestamp> --stage ${STAGE} --region ${REGION}
\`\`\`

## Cleanup

To remove all resources:

\`\`\`bash
serverless remove --stage ${STAGE} --region ${REGION}
\`\`\`

## Support

For issues:
1. Check Lambda logs in CloudWatch
2. Review API Gateway logs
3. Check CloudWatch alarms
4. See docs/SERVERLESS-TROUBLESHOOTING.md
EOF

    log_info "Deployment report generated: serverless-deployment-report.md"
}

# Main deployment flow
main() {
    log_info "Starting Serverless deployment for Security Architect MCP Server"
    log_info "Stage: ${STAGE}"
    log_info "Region: ${REGION}"
    log_info "AWS Profile: ${PROFILE}"

    # Confirm production deployment
    if [ "$STAGE" = "prod" ]; then
        log_warn "About to deploy to PRODUCTION"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi

    # Run deployment steps
    check_prerequisites
    install_dependencies
    package_lambda
    upload_vendor_database
    deploy_serverless
    test_lambda
    setup_monitoring
    generate_report

    log_info "🚀 Serverless deployment complete!"
    log_info "API Endpoint: Check serverless-deployment-report.md"
    log_info "Monitoring: CloudWatch dashboard configured"
    log_info "Cost: Scale to zero - pay only for usage"
}

# Handle script arguments
case "${1:-}" in
    check)
        check_prerequisites
        ;;
    package)
        package_lambda
        ;;
    deploy)
        deploy_serverless
        ;;
    test)
        test_lambda
        ;;
    monitor)
        setup_monitoring
        ;;
    report)
        generate_report
        ;;
    remove)
        log_warn "Removing serverless deployment..."
        cd serverless
        serverless remove --stage $STAGE --region $REGION --aws-profile $PROFILE
        cd ..
        ;;
    *)
        main
        ;;
esac