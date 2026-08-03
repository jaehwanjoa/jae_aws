# MCP Tool Specification

## 개요

Security AI Agent Platform에서 사용하는 MCP(Model Context Protocol) Tool을 정의한다.

모든 MCP는 독립적으로 동작하며 MCP Orchestrator를 통해 호출된다.

---

# MCP Dependency Matrix

| MCP | Provider | Authentication | Purpose |
|-------|-------|-------|-------|
| Athena MCP | AWS Labs | IAM Role | WAF Log Analytics |
| Cortex MCP | Palo Alto Networks | API Key + API Key ID | Cortex Security Analytics |
| PAN-OS MCP | Community (apius-tech) | API Key | Threat Log Analytics |

---

# MCP Architecture

```text
MCP Orchestrator

├── Athena MCP
├── Cortex MCP
└── PAN-OS MCP
```

---

# Athena MCP

## Source

### MCP Server

AWS Data Processing MCP Server

### Repository

https://github.com/awslabs/mcp/tree/main/src/aws-dataprocessing-mcp-server

### Reference

Athena Query Handler

https://github.com/awslabs/mcp/blob/main/src/aws-dataprocessing-mcp-server/awslabs/aws_dataprocessing_mcp_server/handlers/athena/athena_query_handler.py

### Authentication

```text
IAM Role
```

### Purpose

```text
AWS WAF 로그 분석

CloudTrail 분석

Athena 기반 보안 로그 분석
```

---

## Tool: execute_query

설명

```text
Athena SQL 직접 실행
```

입력

```json
{
  "query": "SELECT * FROM waf_logs LIMIT 100"
}
```

출력

```json
{
  "query_execution_id": "",
  "status": "SUCCEEDED",
  "rows": []
}
```

---

## Tool: get_query_result

설명

```text
Athena Query 결과 조회
```

---

## Tool: list_databases

설명

```text
Athena Database 조회
```

---

## Tool: list_tables

설명

```text
Database 내 Table 조회
```

---

## Tool: describe_table

설명

```text
Table Schema 조회
```

---

## Tool: search_uri

설명

```text
특정 URI 공격 분석
```

입력

```json
{
  "uri": "/api/login",
  "hours": 24
}
```

출력

```json
{
  "uri": "/api/login",
  "blocked_count": 341,
  "allowed_count": 12,
  "top_source_ips": [],
  "top_countries": []
}
```

---

## Tool: search_source_ip

설명

```text
특정 Source IP 분석
```

입력

```json
{
  "source_ip": "1.2.3.4",
  "hours": 24
}
```

---

## Tool: top_attacked_uri

설명

```text
공격이 가장 많은 URI 조회
```

---

## Tool: top_attacker_ip

설명

```text
공격이 가장 많은 Source IP 조회
```

---

## Tool: top_rule_match

설명

```text
가장 많이 탐지된 WAF Rule 조회
```

---

## Tool: attack_trend

설명

```text
시간대별 공격 트렌드 분석
```

---

## Tool: search_user_agent

설명

```text
특정 User-Agent 분석
```

---

# Cortex MCP

## Source

### MCP Server

Cortex MCP Server

### Download Location

```text
Settings
→ Configurations
→ Integrations
→ Cortex MCP Server
```

### Documentation

https://docs-cortex.paloaltonetworks.com/r/Cortex-CLOUD/Cortex-Cloud-Posture-Management-Documentation/Install-the-Cortex-MCP-server

### Authentication

```text
API Key

API Key ID
```

### Relevant Components

```text
src/usecase/builtin_components

src/usecase/custom_components

src/usecase/remote_components
```

### Purpose

```text
Alert 분석

Issue 분석

Incident 분석

Endpoint 분석

XQL 분석
```

---

## Tool: get_issues

설명

```text
Cortex Issue 조회
```

조회 가능 필드

```text
id

external_id

detection_method

issue_domain

severity

status

_insert_time
```

입력 예시

```json
{
  "filters": [
    {
      "field": "severity",
      "operator": "in",
      "value": [
        "critical"
      ]
    }
  ]
}
```

사용 사례

```text
Critical Event 조회

Open Issue 조회

Vulnerability 조회

보안 이벤트 현황 조회
```

---

## Tool: search_incident

설명

```text
Incident 조회
```

---

## Tool: search_endpoint

설명

```text
Endpoint 조회
```

---

## Tool: run_xql

설명

```text
XQL Query 실행
```

---

# PAN-OS MCP

## Source

### MCP Server

PanOS MCP

### Repository

https://github.com/apius-tech/Palo-MCP

### MCP Catalog

https://lobehub.com/ko/mcp/apius-tech-palo-mcp

### Status

```text
Community MCP

Not Official Palo Alto MCP
```

### Authentication

```text
PAN-OS API Key
```

### Purpose

```text
Firewall Threat Log 조회

WAF 공격 Source IP 검증

위협 이벤트 분석
```

---

## Tool: search_threat

설명

```text
Palo Alto Firewall Threat Log 조회
```

입력

```json
{
  "source_ip": "1.2.3.4",
  "hours": 24
}
```

출력

```json
{
  "total_events": 14,
  "threats": [
    {
      "source_ip": "1.2.3.4",
      "severity": "high",
      "threat_name": "Command-And-Control Traffic"
    }
  ]
}
```

---

# MCP Orchestrator

## Purpose

```text
MCP Routing

Workflow Control

Result Aggregation

Correlation Analysis
```

---

## Workflow: URI Attack Analysis

사용 Tool

```text
Athena MCP

PAN-OS MCP
```

분석 흐름

```text
URI 입력

↓

Athena MCP

↓

WAF 로그 검색

↓

Source IP 식별

↓

PAN-OS MCP

↓

Threat Log 확인

↓

Correlation Engine

↓

최종 분석 결과 생성
```

---

## Workflow: Attack Trend Analysis

사용 Tool

```text
Athena MCP
```

분석 흐름

```text
URI 집계

↓

Source IP 집계

↓

Country 집계

↓

Rule Match 집계

↓

공격 트렌드 생성
```

---

## Workflow: Cortex Security Analysis

사용 Tool

```text
Cortex MCP
```

분석 흐름

```text
Issue 조회

↓

Incident 조회

↓

Endpoint 조회

↓

XQL 조회

↓

Security Summary 생성
```
