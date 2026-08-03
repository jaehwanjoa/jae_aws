# Authentication Design

## 개요

Security AI Agent Platform에서 사용하는 MCP 인증 방식을 정의한다.

보안 원칙:

```text
1. Access Key 하드코딩 금지

2. Secrets Manager 사용

3. Least Privilege 적용

4. IAM Role 우선 사용

5. API Key 주기적 교체
```

---

# 인증 구성도

```text
AI Agent Lambda
        │
        ▼

AWS Secrets Manager

        │
        ├──────── Cortex API Key
        │
        └──────── PAN-OS API Key

        │
        ▼

MCP Orchestrator

 ├── Athena MCP
 ├── Cortex MCP
 └── PAN-OS MCP
```

---

# Athena MCP

## 인증 방식

```text
IAM Role
```

## Source

AWS Data Processing MCP

## 사용 서비스

```text
Athena

Glue Data Catalog

S3
```

## 인증 구조

```text
Athena MCP

↓

Lambda Execution Role

↓

AWS STS

↓

Athena
```

## 필요 권한

### Athena

```json
{
  "Action": [
    "athena:StartQueryExecution",
    "athena:GetQueryExecution",
    "athena:GetQueryResults",
    "athena:StopQueryExecution"
  ]
}
```

### Glue

```json
{
  "Action": [
    "glue:GetDatabase",
    "glue:GetDatabases",
    "glue:GetTable",
    "glue:GetTables"
  ]
}
```

### S3

```json
{
  "Action": [
    "s3:GetObject",
    "s3:ListBucket"
  ]
}
```

---

# Cortex MCP

## 인증 방식

```text
Cortex API Key

Cortex API Key ID
```

## Source

```text
Cortex Cloud

Settings
→ Configurations
→ Integrations
→ API Keys
```

## 저장 위치

```text
AWS Secrets Manager
```

Secret Name

```text
security-ai/cortex
```

예시

```json
{
  "api_url": "https://tenant-url",
  "api_key": "xxxxxxxx",
  "api_key_id": "xxxxxxxx"
}
```

## Runtime 구조

```text
Lambda

↓

Secrets Manager

↓

Cortex MCP

↓

Cortex Cloud API
```

## 최소 권한

권장 Role

```text
Viewer
```

또는

```text
Read Only Custom Role
```

## 사용 기능

```text
Issue 조회

Incident 조회

Endpoint 조회

XQL 조회
```

---

# PAN-OS MCP

## 인증 방식

```text
PAN-OS API Key
```

## Source

PanOS MCP

Repository

https://github.com/apius-tech/Palo-MCP
```

## 저장 위치

```text
AWS Secrets Manager
```

Secret Name

```text
security-ai/panos
```

예시

```json
{
  "host": "firewall.example.com",
  "api_key": "xxxxxxxx"
}
```

## Runtime 구조

```text
Lambda

↓

Secrets Manager

↓

PAN-OS MCP

↓

Firewall XML API
```

## 사용 기능

```text
Threat Log 조회
```

## 최소 권한

권장

```text
Read Only Admin
```

또는

```text
Custom Read Only Role
```

---

# Secrets Manager

## 구조

```text
security-ai

├── cortex
└── panos
```

---

## 권한

Lambda Role 에만 허용

```json
{
  "Action": [
    "secretsmanager:GetSecretValue"
  ]
}
```

---

# Lambda Execution Role

## 목적

AI Agent 및 MCP Orchestrator 실행

---

## AWS 권한

### Athena

```text
Athena Query
```

### Glue

```text
Database Metadata
```

### S3

```text
WAF Log Access
```

### CloudWatch

```text
Application Logging
```

### Secrets Manager

```text
Retrieve API Credentials
```

---

# 보안 원칙

## 금지 사항

```text
API Key 소스코드 저장

API Key Git Commit

환경변수 평문 저장

관리자 권한 API Key 사용
```

---

## 권장 사항

```text
Secrets Manager 활용

Viewer 권한 사용

Read Only API Key 사용

90일 주기 교체

CloudTrail 감사 적용
```

---

# 인증 매트릭스

| MCP | 인증 방식 | 저장 위치 |
|------|------|------|
| Athena MCP | IAM Role | 없음 |
| Cortex MCP | API Key + API Key ID | Secrets Manager |
| PAN-OS MCP | API Key | Secrets Manager |

---

# 향후 확장

## GuardDuty MCP

```text
IAM Role
```

---

## Security Hub MCP

```text
IAM Role
```

---

## Prisma Cloud MCP

```text
API Key

Secrets Manager
```

---

## CrowdStrike MCP

```text
API Client

Secrets Manager
```
