# Deployment Guide

## 개요

Security AI Agent Platform 배포 절차를 정의한다.

본 문서는 다음 환경을 대상으로 한다.

```text
Local Development

Dev Environment

Production Environment
```

---

# 전체 구성

```text
User

↓

S3 Web UI

↓

API Gateway

↓

AI Agent Lambda

↓

MCP Orchestrator

├── Athena MCP
├── Cortex MCP
└── PAN-OS MCP
```

---

# 로컬 개발 환경

## 필수 구성요소

```text
Python 3.13+

Docker

AWS CLI

Git
```

---

## Repository Clone

```bash
git clone https://github.com/<repository>.git
```

---

## Python Virtual Environment

```bash
python -m venv .venv
```

활성화

```bash
source .venv/bin/activate
```

또는

```powershell
.venv\Scripts\activate
```

---

# AWS 인증 설정

## Local

권장

```bash
aws configure
```

또는

```bash
aws sso login
```

---

## 확인

```bash
aws sts get-caller-identity
```

---

# Athena MCP

## 인증 방식

```text
IAM Role

AWS Credential Profile
```

---

## 동작 확인

Database 목록 조회

```bash
aws athena list-data-catalogs
```

---

# Cortex MCP

## 다운로드

```text
Settings

→ Configurations

→ Integrations

→ Cortex MCP Server
```

【1-795635】

---

## API Key 생성

```text
Settings

→ Configurations

→ Integrations

→ API Keys
```【1-795635】

---

## .env

```env
CORTEX_MCP_PAPI_URL=https://tenant-url

CORTEX_MCP_PAPI_AUTH_HEADER=api-key

CORTEX_MCP_PAPI_AUTH_ID=api-key-id
```

---

## Docker 실행

```bash
docker build -t cortex-mcp .
```

```bash
docker run \
 --env-file .env \
 -it cortex-mcp
```

【1-795635】

---

## 검증

정상 동작 시

```text
MCP Server 실행

오류 없음

대기 상태
```

---

# PAN-OS MCP

## Repository

```text
https://github.com/apius-tech/Palo-MCP
```

Community MCP

공식 Palo Alto MCP 아님【2-f4de0d】

---

## 인증

```env
PANOS_HOST=firewall.example.com

PANOS_API_KEY=xxxxxxxx
```

---

## 검증

```text
Threat Log 조회

Traffic 조회
```

---

# Secrets Manager

## 생성

### Cortex

```text
security-ai/cortex
```

예시

```json
{
  "api_url": "",
  "api_key": "",
  "api_key_id": ""
}
```

---

### PAN-OS

```text
security-ai/panos
```

예시

```json
{
  "host": "",
  "api_key": ""
}
```

---

# Lambda 배포

## Lambda 역할

```text
AI Agent

MCP Orchestrator
```

---

## 환경 변수

```env
AWS_REGION=ap-northeast-2

LOG_LEVEL=INFO
```

---

## Lambda 권한

### Athena

```text
Query Execution
```

### Glue

```text
Metadata Read
```

### S3

```text
WAF Log Read
```

### Secrets Manager

```text
GetSecretValue
```

---

# API Gateway

## Endpoint

```text
POST /chat
```

---

## Request

```json
{
  "prompt": "최근 공격 트렌드 분석"
}
```

---

## Response

```json
{
  "answer": "..."
}
```

---

# S3 Web Hosting

## 역할

```text
Frontend Hosting
```

---

## 배포

```bash
aws s3 sync ./frontend s3://security-ai-ui
```

---

# CloudWatch

## 수집 대상

```text
AI Agent Lambda

MCP Orchestrator

Athena Query

API Error
```

---

# 운영 환경

## Production

```text
Multi-AZ

Version Control

CloudWatch Monitoring

CloudTrail Auditing
```

---

## 로깅 보관

```text
90일 이상 보관
```

---

# 장애 대응

## Athena 실패

대응

```text
Retry

Error Response

Fallback Message
```

---

## Cortex API 실패

대응

```text
Retry

Graceful Degradation
```

---

## PAN-OS API 실패

대응

```text
Threat Analysis Skip

Warning 반환
```

---

# 배포 순서

## Phase 1

```text
Athena MCP 검증
```

## Phase 2

```text
Cortex MCP 검증
```

## Phase 3

```text
PAN-OS MCP 검증
```

## Phase 4

```text
Orchestrator 개발
```

## Phase 5

```text
Bedrock 연동
```

## Phase 6

```text
API Gateway 연결
```

## Phase 7

```text
Frontend 연결
```

## Phase 8

```text
Production 운영
```
