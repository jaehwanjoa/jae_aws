# AWS WAF IaC(Terraform) 기반 배포 자동화 가이드

운용 및 관리 효율성 확대를 위해 IaC(Terraform) 기반 AWS WAF 배포 자동화 방안을 기술하였습니다.<br>
환경은 Identity Center를 활용하는 SSO 환경으로써 액세스 키 인증 방식이 아닌 Role 기반 인증방식을 채택하였고 코드상의 보안성을 확대시켰습니다. 

---

## 1. 사전 요구조건 확인(Idetntity Center에서 역할 부여)

Identity Center 권한 세트에서는 아래와 같은 권한을 필요로 합니다.<br>
해당 권한 세트를 WAF가 구축되는 대상 어카운트에 사용자와 매핑하여 권한을 할당합니다.

```bash
AmazonAthenaFullAccess(선택적/보안운영시 필요)
AWSWAFFullAccess(필요)
ReadOnlyAccess(필요)
```
AWS 액세스 포탈에 접속해서 부여된 자격 증명을 확인합니다.<br>
AWS 액세스 포탈 > 대상 어카운트 선택 > 부여된 Role 액세스 키 확인
```bash
ex)
SSO 시작 URL: https://<id값>.awsapps.com/start
SSO 리전: ap-northeast-2
```

## 2. IaC(Terraform) 파일 구조

WAF 특성 상 CDN용 Global 서비스, ALB용 regional 서비스로 구분되며, 파일 구조 또한 이러한 구조로 분리되어 있습니다.<br>
S3는 같은 리전으로 전송 시 무료라는 특성을 고려하여 Global/regional 로 구분하였습니다. 만약 단일 구조라면 하나로 통일하시면 됩니다.<br>
regional은 서울로 구성되어 있지만, 만약 오사카나 싱가폴이라면 regional/production.tf, provider.tf에서 리전 정보를 변경해야 합니다.

```bash
	terraform
	└─ envs
	   ├─ cloudfront
	   │  ├─ provider.tf
	   │  ├─ variables.tf
	   │  ├─ production.tf   
	   │  └─ terraform.tfvars #CloudFront용 WAF WebACL Name 및 S3 경로 지정
	   └─ regional
	      ├─ production.tf 
	      ├─ provider.tf 
	      ├─ variables.tf
	      ├─ terraform.tf      
	      └─ terraform.tfvars #Regional용 WAF WebACL Name 및 S3 경로 지정
	
	modules
	└─ waf
	   ├─ main.tf #메인 실행 파일
   └─ variables.tf
```
## 3. 실행 방법

aws configure sso 로 인증을 수행합니다.

```bash

aws configure sso

SSO session name (Recommended): session name 입력
SSO start URL [None]: AWS 액세스 포탈 시작 URL 입력
SSO region ap-northeast-2
SSO registration scopes [sso:account:access]:

Attempting to automatically open the SSO authorization page in your default browser.
If the browser does not open, open the following URL

```
Identity Center에서 부여된 Role을 선택합니다.
```bash

Using the account ID <AccouontID>
There are 2 roles available to you.

AWSAdministratorAccess
AWSOrganizationsFullAccess

```
SSO 프로파일 이름을 입력합니다. 
```bash
CLI default client Region [ap-northeast-2]:
CLI default output format CLI profile name [AWSAdministratorAccess-<AccountID>]: ons-waf

```
이후 전체적인 흐름은 아래와 같습니다.<br>
아래 내용 수행 시 WAF가 자동 배포됩니다.

```bash
SSO 로그인: aws sso login --profile ons-waf
Terraform 시작: terraform init
Terraform 배포 적용: terraform apply (WAF 적용할 유형별 CloudFront/Regional 폴더로 이동해야 합니다.)  

```

## 참고용. envs/cloudfront/prodection.tf 설명
```bash
CF용 WAF는 변경사항 없습니다. 만약 regional 서비스라면 리전 정보를 변경하시면 됩니다. ex)aws = aws.singapore

module "cloudfront_waf" {
  source = "../../modules/waf"

  providers = {
    aws = aws.global
  }

  waf_name   = var.waf_name
  waf_scope  = var.waf_scope
  waf_s3_arn = var.waf_s3_arn
}

```
## 참고용. envs/cloudfront/provider.tf 설명
```bash
WAF 이벤트가 저장되는 대상 S3 경로를 지정합니다. 

aws_profile = "waf-1"
waf_name    = "PRD-WAFACL"
waf_scope   = "CLOUDFRONT"
waf_s3_arn  = "arn:aws:s3:::<버킷이름>"

```
## 참고용. envs/cloudfront/terraform.tfvars 설명
```bash
CF용 WAF는 변경사항 없습니다. 만약 regional 서비스라면 리전 정보를 변경하시면 됩니다. ex)region = aws.singapore

aws_profile = "waf-1"
waf_name    = "PRD-WAFACL"
waf_scope   = "CLOUDFRONT"
waf_s3_arn  = "arn:aws:s3:::aws-waf-logs-jaehwan251124"

```
## 참고용. Cross-Account 환경에서 S3 로그 중앙화 구조시 아래 내용을 참고합니다.<br>
S3 버킷은 RAM 구조로 구성할 수 없으며, Cross-Accouont 접근을 위해 아래와 같이 버킷 정책을 적용합니다.
```bash
		{
		    "Version": "2012-10-17",
		    "Statement": [
		        {
		            "Sid": "WAFDirectPut",
		            "Effect": "Allow",
		            "Principal": {
		                "Service": "wafv2.amazonaws.com"
		            },
		            "Action": "s3:PutObject",
		            "Resource": "arn:aws:s3:::<버킷이름 입력>/AWSLogs/*", 
		            "Condition": {
		                "StringEquals": {
		                    "aws:SourceAccount": [
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>".
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>" 
		                    ],
		                    "s3:x-amz-acl": "bucket-owner-full-control"
		                }
		            }
		        },
		        {
		            "Sid": "WAFGetBucketAcl",
		            "Effect": "Allow",
		            "Principal": {
		                "Service": "wafv2.amazonaws.com"
		            },
		            "Action": "s3:GetBucketAcl",
		            "Resource": "arn:aws:s3:::<버킷이름 입력>", 
		            "Condition": {
		                "StringEquals": {
		                    "aws:SourceAccount": [
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>", 
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>" 
		                    ]
		                }
		            }
		        },
		        {
		            "Sid": "AWSLogDeliveryWrite",
		            "Effect": "Allow",
		            "Principal": {
		                "Service": "delivery.logs.amazonaws.com"
		            },
		            "Action": "s3:PutObject",
		            "Resource": "arn:aws:s3:::<버킷이름 입력>/AWSLogs/*", 
		            "Condition": {
		                "StringEquals": {
		                    "aws:SourceAccount": [
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>", 
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>" 
		                    ],
		                    "s3:x-amz-acl": "bucket-owner-full-control"
		                }
		            }
		        },
		        {
		            "Sid": "AWSLogDeliveryAclCheck",
		            "Effect": "Allow",
		            "Principal": {
		                "Service": "delivery.logs.amazonaws.com"
		            },
		            "Action": "s3:GetBucketAcl",
		            "Resource": "arn:aws:s3:::<버킷이름 입력>", 
		            "Condition": {
		                "StringEquals": {
		                    "aws:SourceAccount": [
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>",
		                        "<버킷으로 접근이 필요한 어카운트ID 입력>" 
		                    ]
		                }
		            }
		        }
		    ]
		}


```

## 참고용. modules/waf/main.tf 설명
```bash
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
# ----------------------------------------------------------------------------------------------------------------------
# IP Sets
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_wafv2_ip_set" "Allow_IPSets_Rule" {
  name               = "allow_ipset"
  description        = "Allowed IPs"
  scope              = var.waf_scope
  ip_address_version = "IPV4"
  addresses          = []
}

resource "aws_wafv2_ip_set" "Block_IPSets_Rule" {
  name               = "block_ipset"
  description        = "Blocked IPs"
  scope              = var.waf_scope
  ip_address_version = "IPV4"
  addresses          = []
}

resource "aws_wafv2_ip_set" "host_allow_ips" {
  name               = "host_allow_ipset"
  description        = "Host IP Allowlist"
  scope              = var.waf_scope
  ip_address_version = "IPV4"
  addresses          = ["{허용 IP 입력}"]
}
# ----------------------------------------------------------------------------------------------------------------------
# Regex Pattern Sets
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_wafv2_regex_pattern_set" "regex_ip_deny" {
  name        = "regex_ip_deny"
  description = "IP Deny Pattern"
  scope       = var.waf_scope

  regular_expression {
    regex_string = "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
  }
}

resource "aws_wafv2_regex_pattern_set" "regex_user_agent" {
  name        = "regex_user_agent1"
  description = "Blocked User Agents"
  scope       = var.waf_scope

  regular_expression {
    regex_string = ".*acunetix.*|.*nikto.*|.*nmap.*|.*nuclei.*|.*openvaS.*|.*sqlmap.*|.*wpscan.*|.*zmeu.*|.*zgrab.*"
  }
}

resource "aws_wafv2_regex_pattern_set" "regex_uri_path" {
  name        = "regex_uri_path"
  description = "Blocked URI Paths"
  scope       = var.waf_scope

  regular_expression {
    regex_string = ".*\\.env.*"
  }
  regular_expression {
    regex_string = ".*\\/boaform\\/admin\\/formLogin.*"
  }
  regular_expression {
    regex_string = ".*\\/etc\\/hosts.*|.*\\/etc\\/passwd.*|.*\\/windows\\/win\\.ini.*"
  }
  regular_expression {
    regex_string = ".*\\/xmlrpc\\.php.*|.*phpmyadmin.*|.*phpunit.*"
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# Rule Group
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_wafv2_rule_group" "custom_rule_group" {
  name        = "WAF-Custom-RuleGroup"
  description = "Custom WAF RuleGroup"
  scope       = var.waf_scope
  capacity    = 150

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WAF-Custom-RuleGroup"
    sampled_requests_enabled   = true
  }

  rule {
    name     = "WAF-Host-IP-Allow"
    priority = 0
    action {
      block {}
    }
    statement {
      not_statement {
        statement {
          ip_set_reference_statement {
            arn = aws_wafv2_ip_set.host_allow_ips.arn
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "WAF-Host-IP-Allow"
      sampled_requests_enabled    = true
    }
  }

  rule {
    name     = "URIpath"
    priority = 1

    statement {
      regex_pattern_set_reference_statement {
        arn = aws_wafv2_regex_pattern_set.ons_regex_uri_path.arn
        field_to_match {
          uri_path {}
        }
        text_transformation {
          priority = 0
          type     = "NONE"
        }
      }
    }

    action {
      block {}
    }

    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "URIpath"
    }
  }

  rule {
    name     = "UserAgent"
    priority = 2

    statement {
      regex_pattern_set_reference_statement {
        arn = aws_wafv2_regex_pattern_set.ons_regex_user_agent.arn
        field_to_match {
          single_header {
            name = "user-agent"
          }
        }
        text_transformation {
          priority = 0
          type     = "NONE"
        }
      }
    }

    action {
      block {}
    }

    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "UserAgent"
    }
  }

  rule {
    name     = "IPPatternDeny"
    priority = 3

    statement {
      regex_pattern_set_reference_statement {
        arn = aws_wafv2_regex_pattern_set.ons_regex_ip_deny.arn
        field_to_match {
          single_header {
            name = "host"
          }
        }
        text_transformation {
          priority = 0
          type     = "NONE"
        }
      }
    }

    action {
      count {}
    }

    visibility_config {
      sampled_requests_enabled   = true
      cloudwatch_metrics_enabled = true
      metric_name                = "IPPatternDeny"
    }
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# Web ACL
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_wafv2_web_acl" "WafWebAcl" {
  name        = var.waf_name
  scope       = var.waf_scope
  description = "WAF for ${var.waf_name}"
  default_action {
    allow {}
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = var.waf_name
    sampled_requests_enabled    = true
  }

  # Allowed IPs Rule
  rule {
    name     = "Allow_IPSets_Rule"
    priority = 0
    action {
      allow {}
    }
    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.Allow_IPSets_Rule.arn
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "Allow_IPSets_Rule"
      sampled_requests_enabled    = true
    }
  }

  # Blocked IPs Rule
  rule {
    name     = "Block_IPSets_Rule"
    priority = 1
    action {
      block {}
    }
    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.Block_IPSets_Rule.arn
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "Block_IPSets_Rule"
      sampled_requests_enabled    = true
    }
  }

  # Custom RuleGroup 
  rule {
    name     = "WAF-Custom-RuleGroup"
    priority = 2
    override_action {
      none {}
    }
    statement {
      rule_group_reference_statement  {
        arn = aws_wafv2_rule_group.ONS_custom_rule_group.arn
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "WAF-Custom-RuleGroup"
      sampled_requests_enabled    = true
    }
  }

  # Common Rule Set
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 3
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
        version = "Version_1.17"

        rule_action_override {
          action_to_use {
            count {}
          }
          name = "NoUserAgent_HEADER"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "UserAgent_BadBots_HEADER"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "SizeRestrictions_QUERYSTRING"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "SizeRestrictions_Cookie_HEADER"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SizeRestrictions_BODY"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SizeRestrictions_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "EC2MetaDataSSRF_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "EC2MetaDataSSRF_COOKIE"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "EC2MetaDataSSRF_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "EC2MetaDataSSRF_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "GenericLFI_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "GenericLFI_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "GenericLFI_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "RestrictedExtensions_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "RestrictedExtensions_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "GenericRFI_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "GenericRFI_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "GenericRFI_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "CrossSiteScripting_COOKIE"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "CrossSiteScripting_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "CrossSiteScripting_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "CrossSiteScripting_URIPATH"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled    = true
    }
  }

  # Known Bad Inputs Rule Set
  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 4
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
        version = "Version_1.24"

        rule_action_override {
          action_to_use {
            block {}
          }
          name = "JavaDeserializationRCE_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "JavaDeserializationRCE_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "JavaDeserializationRCE_QUERYSTRING"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "JavaDeserializationRCE_HEADER"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "Host_localhost_HEADER"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "PROPFIND_METHOD"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "ExploitablePaths_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "Log4JRCE_QUERYSTRING"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "Log4JRCE_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "Log4JRCE_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "Log4JRCE_HEADER"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "ReactJSRCE_BODY"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled    = true
    }
  }

  # AdminProtection Rule Set
  rule {
    name     = "AWS-AWSManagedRulesAdminProtectionRuleSet"
    priority = 5
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAdminProtectionRuleSet"
        vendor_name = "AWS"
        version = "Version_1.1"

        rule_action_override {
          action_to_use {
            count {}
          }
          name = "AdminProtection_URIPATH"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAdminProtectionRuleSet"
      sampled_requests_enabled    = true
    }
  }

 # Linux Rule Set
  rule {
    name     = "AWS-AWSManagedRulesLinuxRuleSet"
    priority = 6
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
        version = "Version_2.6"

        rule_action_override {
          action_to_use {
            block {}
          }
          name = "LFI_URIPATH"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "LFI_QUERYSTRING"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "LFI_HEADER"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesLinuxRuleSet"
      sampled_requests_enabled    = true
    }
  }

  # Unix Rule Set
  rule {
    name     = "AWS-AWSManagedRulesUnixRuleSet"
    priority = 7
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesUnixRuleSet"
        vendor_name = "AWS"
        version = "Version_3.0"

        rule_action_override {
          action_to_use {
            count {}
          }
          name = "UNIXShellCommandsVariables_QUERYSTRING"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "UNIXShellCommandsVariables_BODY"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "UNIXShellCommandsVariables_HEADER"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesUnixRuleSet"
      sampled_requests_enabled    = true
    }
  }

  # SQL Injection Rule Set
  rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 8
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
        version = "Version_1.3"

        rule_action_override {
          action_to_use {
            block {}
          }
          name = "SQLiExtendedPatterns_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SQLi_QUERYARGUMENTS"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "SQLi_BODY"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "SQLi_COOKIE"
        }
        rule_action_override {
          action_to_use {
            block {}
          }
          name = "SQLi_URIPATH"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled    = true
    }
  }

  # AmazonIpReputationList Rule Set
  rule {
    name     = "AWS-AWSManagedRulesAmazonIpReputationList"
    priority = 9
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"

        rule_action_override {
          action_to_use {
            count {}
          }
          name = "AWSManagedIPReputationList"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "AWSManagedReconnaissanceList"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "AWSManagedIPDDoSList"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAmazonIpReputationList"
      sampled_requests_enabled    = true
    }
  }

  # Anonymous IP List Rule
  rule {
    name     = "AWS-AWSManagedRulesAnonymousIpList"
    priority = 10
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"
        
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "AnonymousIPList"
        }
        rule_action_override {
          action_to_use {
            count {}
          }
          name = "HostingProviderIPList"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesAnonymousIpList"
      sampled_requests_enabled    = true
    }
  }
}

# ----------------------------------------------------------------------------------------------------------------------
# Web ACL Logging Configuration
# ----------------------------------------------------------------------------------------------------------------------
resource "aws_wafv2_web_acl_logging_configuration" "web_acl_logging" {
  log_destination_configs = [var.waf_s3_arn]
  resource_arn           = aws_wafv2_web_acl.WafWebAcl.arn

  depends_on = [
    aws_wafv2_web_acl.WafWebAcl
  ]
}

```

