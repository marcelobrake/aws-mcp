# AWS MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides Claude Desktop with tools to interact with AWS services using your machine's configured AWS profiles.

## Features

- **208 AWS tools** across 57 services: EC2, S3, IAM, Lambda, CloudWatch, ECS, RDS, DynamoDB, SQS, SNS, SES, ECR, ElastiCache, API Gateway, CloudFront, Route53, Cost Explorer, Cognito, MemoryDB, DocumentDB, OpenSearch, EKS, Athena, Glue, MWAA, Firehose, Secrets Manager, SSM, Lake Formation, CloudTrail, CloudFormation, KMS, ACM, Kinesis, EMR, SageMaker, VPC, Organizations, Resource Groups, EventBridge, ELB v2, Auto Scaling, Step Functions, WAF v2, GuardDuty, Security Hub, CodePipeline, CodeBuild, CodeDeploy, Redshift, EFS, AWS Backup, and more
- **Multi-profile support** — use any AWS profile from `~/.aws/config`
- **Readonly mode** (`--readonly`) — blocks all mutating operations; uses `DryRun` where the AWS API supports it
- **Structured JSONL logging** — every operation is logged to `logs/aws_mcp.jsonl`
- **OpenTelemetry tracing** — distributed traces for every tool invocation, exportable via OTLP
- **Cross-platform** — works on Ubuntu/Linux, macOS, and Windows

## Requirements

- Python 3.12+
- AWS CLI configured with profiles (`~/.aws/config` and `~/.aws/credentials`)

## Quick Start

### 1. Setup

```bash
cd aws-mcp
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
pip install -e .
```

### 2. Test the server

```bash
# Verify it starts (will wait for MCP input on stdin, Ctrl+C to stop)
.venv/bin/python main.py --readonly
```

### 3. Configure Claude Desktop

Edit your Claude Desktop configuration file:

| OS      | Config file path                                                         |
|---------|--------------------------------------------------------------------------|
| Linux   | `~/.config/Claude/claude_desktop_config.json`                            |
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json`        |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json`                            |

Add the server to the `mcpServers` section:

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "/absolute/path/to/aws-mcp/.venv/bin/python",
      "args": [
        "/absolute/path/to/aws-mcp/main.py",
        "--readonly"
      ]
    }
  }
}
```

> See [`claude_desktop_config.example.json`](claude_desktop_config.example.json) for a full example with multiple configurations.

#### Windows configuration

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "C:\\path\\to\\aws-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\aws-mcp\\main.py",
        "--readonly"
      ]
    }
  }
}
```

### 4. Restart Claude Desktop

After saving the configuration, restart Claude Desktop. The AWS tools will appear in the tools menu.

## CLI Options

| Flag           | Description                                      | Default |
|----------------|--------------------------------------------------|---------|
| `--readonly`   | Block mutations; use DryRun where supported       | Off     |
| `--log-dir`    | Directory for JSONL log files                    | `logs`  |
| `--log-level`  | Log verbosity: DEBUG, INFO, WARNING, ERROR       | `INFO`  |

## Available Tools (208 total)

### Profile Management

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_list_profiles` | List all configured AWS profiles and their regions | Allowed |
| `aws_get_caller_identity` | Get STS caller identity for a profile | Allowed |

### EC2

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_ec2_describe_instances` | List/describe EC2 instances | Allowed |
| `aws_ec2_describe_security_groups` | Describe security groups | Allowed |
| `aws_ec2_manage_instances` | Start/stop/reboot instances | DryRun=True |

### S3

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_s3_list_buckets` | List S3 buckets | Allowed |
| `aws_s3_list_objects` | List objects in a bucket | Allowed |
| `aws_s3_get_object` | Download and read an object | Allowed |
| `aws_s3_put_object` | Upload an object | Blocked |
| `aws_s3_delete_objects` | Delete objects | Blocked |

### IAM

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_iam_list_users` | List IAM users | Allowed |
| `aws_iam_list_roles` | List IAM roles | Allowed |
| `aws_iam_list_policies` | List IAM policies | Allowed |

### Lambda

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_lambda_list_functions` | List Lambda functions | Allowed |
| `aws_lambda_get_function` | Get function config and metadata | Allowed |
| `aws_lambda_invoke` | Invoke a function | InvocationType=DryRun |

### CloudWatch Logs

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_logs_describe_log_groups` | List log groups | Allowed |
| `aws_logs_get_log_events` | Get events from a log stream | Allowed |
| `aws_logs_filter_log_events` | Search logs with a filter pattern | Allowed |

### CloudWatch Metrics & Alarms

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_cloudwatch_describe_alarms` | List alarms with state and threshold config | Allowed |
| `aws_cloudwatch_list_metrics` | List available metrics by namespace | Allowed |
| `aws_cloudwatch_get_metric_data` | Retrieve time-series data for multiple metrics | Allowed |
| `aws_cloudwatch_get_metric_statistics` | Get statistics for a single metric | Allowed |

### ECS

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_ecs_list_clusters` | List ECS clusters | Allowed |
| `aws_ecs_describe_clusters` | Describe cluster details | Allowed |
| `aws_ecs_list_services` | List services in a cluster | Allowed |
| `aws_ecs_describe_services` | Describe service details | Allowed |
| `aws_ecs_list_tasks` | List tasks in a cluster | Allowed |
| `aws_ecs_describe_tasks` | Describe task details | Allowed |

### RDS

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_rds_describe_db_instances` | Describe RDS instances | Allowed |
| `aws_rds_describe_db_clusters` | Describe Aurora clusters | Allowed |

### DynamoDB

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_dynamodb_list_tables` | List DynamoDB tables | Allowed |
| `aws_dynamodb_describe_table` | Describe table schema and settings | Allowed |
| `aws_dynamodb_query` | Query a table by key condition | Allowed |
| `aws_dynamodb_scan` | Scan a table (use sparingly) | Allowed |

### SQS

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_sqs_list_queues` | List SQS queues | Allowed |
| `aws_sqs_get_queue_attributes` | Get queue attributes (message count, DLQ, etc.) | Allowed |
| `aws_sqs_receive_message` | Peek messages without deleting | Allowed |
| `aws_sqs_send_message` | Send a message to a queue | Blocked |
| `aws_sqs_purge_queue` | Purge all messages from a queue | Blocked |

### SNS

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_sns_list_topics` | List SNS topics | Allowed |
| `aws_sns_get_topic_attributes` | Get topic attributes | Allowed |
| `aws_sns_list_subscriptions` | List subscriptions | Allowed |
| `aws_sns_publish` | Publish a message to a topic | Blocked |

### SES

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_ses_list_identities` | List verified email addresses and domains | Allowed |
| `aws_ses_get_send_statistics` | Get sending stats (deliveries, bounces, etc.) | Allowed |
| `aws_ses_get_send_quota` | Get sending quota and current usage | Allowed |
| `aws_ses_get_identity_verification_attributes` | Get verification status | Allowed |
| `aws_ses_send_email` | Send an email | Blocked |

### ECR

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_ecr_describe_repositories` | List and describe ECR repositories | Allowed |
| `aws_ecr_list_images` | List images in a repository | Allowed |
| `aws_ecr_describe_images` | Get image metadata (size, scan status, vulns) | Allowed |
| `aws_ecr_get_lifecycle_policy` | Get repository lifecycle policy | Allowed |

### ElastiCache (Redis / Memcached)

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_elasticache_describe_cache_clusters` | Describe clusters (engine, node type, endpoints) | Allowed |
| `aws_elasticache_describe_replication_groups` | Describe Redis replication groups | Allowed |
| `aws_elasticache_describe_serverless_caches` | Describe serverless caches | Allowed |
| `aws_elasticache_describe_events` | Get recent events (maintenance, failover, etc.) | Allowed |

### ELB v2 (ALB / NLB)

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_elbv2_describe_load_balancers` | List ALBs, NLBs, and Gateway LBs | Allowed |
| `aws_elbv2_describe_target_groups` | List target groups | Allowed |
| `aws_elbv2_describe_target_health` | Get health of targets in a target group | Allowed |
| `aws_elbv2_describe_listeners` | List listeners for a load balancer | Allowed |

### Auto Scaling

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_autoscaling_describe_auto_scaling_groups` | List ASGs with capacity and instance details | Allowed |
| `aws_autoscaling_describe_scaling_policies` | List scaling policies | Allowed |
| `aws_autoscaling_describe_scaling_activities` | Get recent scale-out/in events | Allowed |
| `aws_autoscaling_describe_launch_configurations` | List launch configurations | Allowed |

### API Gateway

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_apigateway_get_rest_apis` | List REST APIs (v1) | Allowed |
| `aws_apigateway_get_resources` | List resources/paths for a REST API | Allowed |
| `aws_apigateway_get_stages` | List stages for a REST API | Allowed |
| `aws_apigatewayv2_get_apis` | List HTTP/WebSocket APIs (v2) | Allowed |
| `aws_apigatewayv2_get_routes` | List routes for an HTTP/WS API | Allowed |
| `aws_apigatewayv2_get_stages` | List stages for an HTTP/WS API | Allowed |

### CloudFront

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_cloudfront_list_distributions` | List distributions with domains/origins | Allowed |
| `aws_cloudfront_get_distribution` | Get full distribution configuration | Allowed |
| `aws_cloudfront_list_invalidations` | List cache invalidation requests | Allowed |
| `aws_cloudfront_create_invalidation` | Create a cache invalidation | Blocked |

### Route53

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_route53_list_hosted_zones` | List hosted zones (DNS domains) | Allowed |
| `aws_route53_get_hosted_zone` | Get zone details and NS records | Allowed |
| `aws_route53_list_resource_record_sets` | List DNS records in a zone | Allowed |
| `aws_route53_change_resource_record_sets` | Create/update/delete DNS records | Blocked |

### VPC

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_vpc_describe_vpcs` | Describe VPCs | Allowed |
| `aws_vpc_describe_subnets` | Describe subnets | Allowed |
| `aws_vpc_describe_nat_gateways` | Describe NAT gateways | Allowed |
| `aws_vpc_describe_internet_gateways` | Describe internet gateways | Allowed |
| `aws_vpc_describe_route_tables` | Describe route tables | Allowed |
| `aws_vpc_describe_vpc_peering_connections` | Describe VPC peering connections | Allowed |

### Cost Explorer

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_ce_get_cost_and_usage` | Get cost and usage data for a date range | Allowed |
| `aws_ce_get_cost_forecast` | Forecast future AWS costs | Allowed |

### KMS

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_kms_list_keys` | List KMS keys | Allowed |
| `aws_kms_describe_key` | Describe a KMS key | Allowed |
| `aws_kms_list_aliases` | List KMS key aliases | Allowed |

### ACM (Certificate Manager)

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_acm_list_certificates` | List ACM certificates | Allowed |
| `aws_acm_describe_certificate` | Get full certificate details | Allowed |

### Secrets Manager

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_secretsmanager_list_secrets` | List secrets (names/metadata, not values) | Allowed |
| `aws_secretsmanager_describe_secret` | Get secret metadata and rotation info | Allowed |
| `aws_secretsmanager_get_secret_value` | Retrieve actual secret value | Blocked |

### SSM (Systems Manager)

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_ssm_describe_parameters` | List Parameter Store parameters | Allowed |
| `aws_ssm_get_parameter` | Get a parameter value (decrypts SecureString) | Allowed |
| `aws_ssm_get_parameters_by_path` | Get parameters under a path hierarchy | Allowed |
| `aws_ssm_describe_instance_information` | List SSM-managed instances | Allowed |
| `aws_ssm_put_parameter` | Create/update a parameter | Blocked |

### Cognito

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_cognito_list_user_pools` | List Cognito user pools | Allowed |
| `aws_cognito_describe_user_pool` | Get user pool configuration details | Allowed |
| `aws_cognito_list_users` | List users in a user pool | Allowed |
| `aws_cognito_list_groups` | List groups in a user pool | Allowed |

### EKS

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_eks_list_clusters` | List EKS clusters | Allowed |
| `aws_eks_describe_cluster` | Describe cluster details | Allowed |
| `aws_eks_list_nodegroups` | List node groups in a cluster | Allowed |
| `aws_eks_describe_nodegroup` | Describe node group details | Allowed |
| `aws_eks_list_fargate_profiles` | List Fargate profiles | Allowed |

### Kinesis

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_kinesis_list_streams` | List Kinesis data streams | Allowed |
| `aws_kinesis_describe_stream` | Describe a stream | Allowed |
| `aws_kinesis_list_shards` | List shards in a stream | Allowed |

### Firehose

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_firehose_list_delivery_streams` | List delivery streams | Allowed |
| `aws_firehose_describe_delivery_stream` | Describe stream configuration | Allowed |

### Step Functions

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_sfn_list_state_machines` | List state machines | Allowed |
| `aws_sfn_describe_state_machine` | Get state machine definition | Allowed |
| `aws_sfn_list_executions` | List executions for a state machine | Allowed |
| `aws_sfn_describe_execution` | Get execution status and output | Allowed |
| `aws_sfn_get_execution_history` | Get execution event history | Allowed |

### EventBridge

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_events_list_event_buses` | List event buses | Allowed |
| `aws_events_list_rules` | List rules on an event bus | Allowed |
| `aws_events_describe_rule` | Get full rule configuration | Allowed |
| `aws_events_list_targets_by_rule` | List targets attached to a rule | Allowed |

### WAF v2

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_wafv2_list_web_acls` | List Web ACLs (REGIONAL or CLOUDFRONT) | Allowed |
| `aws_wafv2_get_web_acl` | Get full Web ACL configuration | Allowed |
| `aws_wafv2_get_web_acl_for_resource` | Get Web ACL associated with a resource | Allowed |
| `aws_wafv2_list_ip_sets` | List IP sets (allow/block lists) | Allowed |
| `aws_wafv2_list_rule_groups` | List rule groups | Allowed |

### GuardDuty

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_guardduty_list_detectors` | List detector IDs | Allowed |
| `aws_guardduty_get_detector` | Get detector configuration | Allowed |
| `aws_guardduty_list_findings` | List finding IDs (filter by severity/type) | Allowed |
| `aws_guardduty_get_findings` | Get full finding details | Allowed |
| `aws_guardduty_get_findings_statistics` | Get findings count by severity | Allowed |

### Security Hub

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_securityhub_describe_hub` | Get Security Hub configuration | Allowed |
| `aws_securityhub_get_findings` | Get findings from all integrated services | Allowed |
| `aws_securityhub_get_findings_summary` | Get findings count by severity | Allowed |
| `aws_securityhub_list_standards_subscriptions` | List enabled security standards | Allowed |
| `aws_securityhub_list_enabled_products_for_import` | List active integrations | Allowed |

### CodePipeline

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_codepipeline_list_pipelines` | List pipelines | Allowed |
| `aws_codepipeline_get_pipeline` | Get pipeline structure | Allowed |
| `aws_codepipeline_get_pipeline_state` | Get current stage execution state | Allowed |
| `aws_codepipeline_list_pipeline_executions` | List recent executions | Allowed |

### CodeBuild

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_codebuild_list_projects` | List build project names | Allowed |
| `aws_codebuild_batch_get_projects` | Get project configuration details | Allowed |
| `aws_codebuild_list_builds_for_project` | List recent build IDs for a project | Allowed |
| `aws_codebuild_batch_get_builds` | Get build details (status, phases, logs) | Allowed |

### CodeDeploy

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_codedeploy_list_applications` | List application names | Allowed |
| `aws_codedeploy_list_deployment_groups` | List deployment groups | Allowed |
| `aws_codedeploy_list_deployments` | List deployments with status filter | Allowed |
| `aws_codedeploy_get_deployment` | Get full deployment details | Allowed |

### Athena

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_athena_list_work_groups` | List Athena workgroups | Allowed |
| `aws_athena_list_databases` | List databases in a catalog | Allowed |
| `aws_athena_list_table_metadata` | List tables in a database | Allowed |
| `aws_athena_start_query_execution` | Start a SQL query | Blocked |
| `aws_athena_get_query_execution` | Get query status | Allowed |
| `aws_athena_get_query_results` | Get query results | Allowed |

### Glue

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_glue_get_databases` | List Glue Data Catalog databases | Allowed |
| `aws_glue_get_tables` | List tables in a database | Allowed |
| `aws_glue_get_jobs` | List Glue ETL jobs | Allowed |
| `aws_glue_get_job_runs` | Get runs for a specific job | Allowed |
| `aws_glue_get_crawlers` | List Glue crawlers | Allowed |
| `aws_glue_start_job_run` | Start a Glue ETL job | Blocked |

### MWAA (Managed Airflow)

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_mwaa_list_environments` | List MWAA environments | Allowed |
| `aws_mwaa_get_environment` | Get environment details | Allowed |

### Lake Formation

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_lakeformation_get_data_lake_settings` | Get data lake settings | Allowed |
| `aws_lakeformation_list_permissions` | List permissions on resources | Allowed |
| `aws_lakeformation_list_resources` | List registered resources | Allowed |

### CloudTrail

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_cloudtrail_describe_trails` | Describe trails in the account | Allowed |
| `aws_cloudtrail_get_trail_status` | Get trail logging status | Allowed |
| `aws_cloudtrail_lookup_events` | Look up recent management events | Allowed |

### CloudFormation

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_cfn_list_stacks` | List stacks with status filter | Allowed |
| `aws_cfn_describe_stacks` | Get detailed stack info | Allowed |
| `aws_cfn_list_stack_resources` | List resources in a stack | Allowed |
| `aws_cfn_get_template` | Get stack template body | Allowed |
| `aws_cfn_describe_stack_events` | Get stack events (for debugging) | Allowed |

### Redshift

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_redshift_describe_clusters` | List clusters with status and endpoint | Allowed |
| `aws_redshift_describe_cluster_snapshots` | List manual and automated snapshots | Allowed |
| `aws_redshift_describe_cluster_parameters` | List parameter group settings | Allowed |

### EFS (Elastic File System)

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_efs_describe_file_systems` | List EFS file systems | Allowed |
| `aws_efs_describe_mount_targets` | List mount targets | Allowed |
| `aws_efs_describe_access_points` | List access points | Allowed |

### AWS Backup

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_backup_list_backup_plans` | List backup plans | Allowed |
| `aws_backup_list_backup_vaults` | List backup vaults | Allowed |
| `aws_backup_list_backup_jobs` | List backup jobs with status | Allowed |
| `aws_backup_list_recovery_points_by_backup_vault` | List recovery points in a vault | Allowed |

### EMR

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_emr_list_clusters` | List EMR clusters | Allowed |
| `aws_emr_describe_cluster` | Describe cluster details | Allowed |
| `aws_emr_list_steps` | List steps in a cluster | Allowed |

### SageMaker

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_sagemaker_list_endpoints` | List inference endpoints | Allowed |
| `aws_sagemaker_describe_endpoint` | Get endpoint configuration | Allowed |
| `aws_sagemaker_list_notebook_instances` | List notebook instances | Allowed |
| `aws_sagemaker_list_training_jobs` | List training jobs | Allowed |

### OpenSearch

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_opensearch_list_domain_names` | List OpenSearch domain names | Allowed |
| `aws_opensearch_describe_domain` | Describe domain configuration | Allowed |
| `aws_opensearch_describe_domain_health` | Get domain cluster health | Allowed |

### DocumentDB

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_docdb_describe_db_clusters` | Describe DocumentDB clusters | Allowed |
| `aws_docdb_describe_db_instances` | Describe DocumentDB instances | Allowed |

### MemoryDB

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_memorydb_describe_clusters` | Describe MemoryDB clusters | Allowed |
| `aws_memorydb_describe_snapshots` | Describe MemoryDB snapshots | Allowed |

### Organizations

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_organizations_describe_organization` | Describe the AWS Organization | Allowed |
| `aws_organizations_list_accounts` | List all accounts in the organization | Allowed |
| `aws_organizations_list_organizational_units` | List OUs for a parent | Allowed |
| `aws_organizations_list_roots` | List organization roots | Allowed |

### Resource Groups & Tag Manager

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_tagging_get_resources` | Find resources by tag across all services | Allowed |
| `aws_tagging_get_tag_keys` | List all tag keys in the account/region | Allowed |
| `aws_tagging_get_tag_values` | List all values for a tag key | Allowed |
| `aws_resourcegroups_list_groups` | List Resource Groups | Allowed |

### General

| Tool | Description | Readonly |
|------|-------------|----------|
| `aws_execute` | Execute any AWS API call | Depends on operation |

## Readonly Mode

When `--readonly` is passed, the server enforces these rules:

1. **Read-only operations** (`list*`, `describe*`, `get*`, etc.) — always allowed
2. **Mutating operations with DryRun support** (e.g., EC2 start/stop, Lambda invoke) — executed with `DryRun=True` to validate permissions without making changes
3. **Mutating operations without DryRun** (e.g., S3 put/delete, SSM put, SQS send) — blocked with a clear error message

This makes it safe to give Claude access to production AWS accounts for observation and troubleshooting.

## Logging

All operations are logged in JSONL format to `logs/aws_mcp.jsonl`. Each line is a JSON object with fields:

```json
{
  "timestamp": "2025-03-25T12:00:00.000000+00:00",
  "level": "INFO",
  "logger": "aws_mcp",
  "message": "Tool 'aws_ec2_describe_instances' completed successfully",
  "tool_name": "aws_ec2_describe_instances",
  "duration_ms": 342.15,
  "aws_profile": "production",
  "aws_region": "sa-east-1"
}
```

## Telemetry (OpenTelemetry)

Every tool invocation creates an OpenTelemetry span with attributes like `tool.name`, `aws.profile`, `aws.region`, and `duration_ms`.

To export traces to an observability backend (Jaeger, Grafana Tempo, etc.):

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 .venv/bin/python main.py
```

Without the environment variable, traces are emitted to stderr in a human-readable format.

## Project Structure

```text
aws-mcp/
├── main.py                     # Entry point
├── aws_mcp/
│   ├── __init__.py             # App initialization
│   ├── server.py               # MCP server and tool dispatch
│   ├── config.py               # CLI argument parsing
│   ├── aws_client.py           # boto3 session management
│   ├── readonly_guard.py       # Readonly mode enforcement
│   ├── logging_config.py       # JSONL logging setup
│   ├── telemetry.py            # OpenTelemetry setup
│   └── tools/
│       ├── __init__.py         # Tool registry and loader
│       ├── profiles.py         # AWS profile / STS tools
│       ├── ec2.py              # EC2 tools
│       ├── s3.py               # S3 tools
│       ├── iam.py              # IAM tools
│       ├── lambda_tool.py      # Lambda tools
│       ├── cloudwatch.py       # CloudWatch Logs, Metrics & Alarms
│       ├── ecs.py              # ECS tools
│       ├── rds.py              # RDS tools
│       ├── dynamodb.py         # DynamoDB tools
│       ├── sqs.py              # SQS tools
│       ├── sns.py              # SNS tools
│       ├── ses.py              # SES tools
│       ├── ecr.py              # ECR tools
│       ├── elasticache.py      # ElastiCache (Redis/Memcached)
│       ├── elbv2.py            # ALB / NLB / Gateway LB
│       ├── autoscaling.py      # Auto Scaling Groups
│       ├── apigateway.py       # API Gateway v1 + v2
│       ├── cloudfront.py       # CloudFront
│       ├── route53.py          # Route53
│       ├── vpc.py              # VPC, subnets, gateways
│       ├── kms.py              # KMS keys and aliases
│       ├── acm.py              # ACM certificates
│       ├── cost_explorer.py    # Cost Explorer
│       ├── secretsmanager.py   # Secrets Manager
│       ├── ssm.py              # SSM Parameter Store
│       ├── cognito.py          # Cognito user pools
│       ├── eks.py              # EKS clusters and node groups
│       ├── kinesis.py          # Kinesis Data Streams
│       ├── firehose.py         # Kinesis Firehose
│       ├── stepfunctions.py    # Step Functions
│       ├── eventbridge.py      # EventBridge
│       ├── wafv2.py            # WAF v2
│       ├── guardduty.py        # GuardDuty
│       ├── securityhub.py      # Security Hub
│       ├── codepipeline.py     # CodePipeline
│       ├── codebuild.py        # CodeBuild
│       ├── codedeploy.py       # CodeDeploy
│       ├── athena.py           # Athena
│       ├── glue.py             # Glue
│       ├── mwaa.py             # MWAA (Managed Airflow)
│       ├── lakeformation.py    # Lake Formation
│       ├── cloudtrail.py       # CloudTrail
│       ├── cloudformation.py   # CloudFormation
│       ├── redshift.py         # Redshift
│       ├── efs.py              # EFS
│       ├── backup.py           # AWS Backup
│       ├── emr.py              # EMR
│       ├── sagemaker.py        # SageMaker
│       ├── opensearch.py       # OpenSearch
│       ├── documentdb.py       # DocumentDB
│       ├── memorydb.py         # MemoryDB
│       ├── organizations.py    # Organizations
│       ├── resourcegroups.py   # Resource Groups & Tag Manager
│       └── general.py          # General-purpose AWS executor
├── logs/                       # JSONL log output
├── pyproject.toml              # Package metadata and dependencies
├── setup.sh                    # Setup script
├── claude_desktop_config.example.json
├── LICENSE
└── README.md
```

## License

BSD 3-Clause — see [LICENSE](LICENSE) for details.
