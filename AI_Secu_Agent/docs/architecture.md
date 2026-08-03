# Security AI Agent Platform Architecture

## 1. 개요

본 프로젝트는 AWS, Palo Alto Networks, Cortex 데이터를 통합 분석하는 AI 기반 보안 운영 플랫폼이다.

사용자는 자연어로 보안 질의를 수행하며, AI Agent는 MCP(Model Context Protocol) 기반 Tool을 호출하여 분산된 보안 솔루션의 데이터를 수집하고 상관관계 분석을 수행한다.

---

# 2. 목표

## 주요 기능

- AWS WAF 운영 및 정책 관리
- Athena 기반 로그 분석
- Cortex 보안 이벤트 조회 및 분석
- Palo Alto Firewall 정책 및 로그 조회
- 보안 이벤트 상관관계 분석
- Amazon Bedrock 기반 자연어 응답 생성

---

# 3. 전체 아키텍처

```text
                    User
                      │
                      ▼

                 S3 Web UI
                 (Frontend)

                      │
                      ▼

                 API Gateway

                      │
                      ▼

                AI Agent Lambda
                  (Bedrock)

                      │
                      ▼

               MCP Orchestrator

       ┌──────────┬──────────┬──────────┬──────────┐
       │          │          │          │
       ▼          ▼          ▼          ▼

 Athena MCP   WAF MCP   Cortex MCP  PAN-OS MCP

       │          │          │          │
       ▼          ▼          ▼          ▼

    Athena      AWS WAF   Cortex      Palo Alto
                         XDR/XSIAM     Firewall
```

---

# 4. 설계 원칙

## MCP 독립성

각 MCP는 서로 직접 통신하지 않는다.

예)

```text
Athena MCP
  ↓
Cortex MCP
```

구조 아님

올바른 구조

```text
               Orchestrator

      ┌─────────┼─────────┐

   Athena    Cortex    PANOS
```

모든 MCP 호출은 Orchestrator를 통해 수행한다.

---

# 5. 주요 구성 요소

## Frontend

서비스

```text
AWS S3 Static Web Hosting
```

역할

```text
질의 입력

응답 출력

분석 결과 시각화
```

---

## API Gateway

역할

```text
REST API 제공

Lambda 연동

인증 처리
```

---

## AI Agent Lambda

역할

```text
Amazon Bedrock 호출

질의 분석

Tool 선택

MCP Orchestrator 호출

최종 응답 생성
```

---

## MCP Orchestrator

프로젝트 핵심 컴포넌트

역할

```text
Tool Routing

Workflow 제어

MCP 호출

결과 수집

상관관계 분석

최종 데이터 생성
```

예)

```text
1.2.3.4 IP 분석
```

↓

```text
Athena MCP 호출

WAF MCP 호출

Cortex MCP 호출

PAN-OS MCP 호출

결과 통합

Bedrock 응답 생성
```

---

# 6. MCP 서버 설계

## 6.1 Athena MCP

구현 방식

```text
AWS Official Data Processing MCP
```

주요 서비스

```text
Athena

Glue

EMR
```

주요 Tool

```text
execute_query

get_query_result

list_databases

list_tables

search_logs
```

사용 사례

```text
WAF 로그 조회

CloudTrail 조회

보안 로그 검색

공격자 IP 검색
```

---

## 6.2 AWS WAF MCP

목적

```text
AWS WAF 운영 관리
```

주요 Tool

```text
list_web_acl

get_web_acl

list_rules

list_ip_set

create_ip_set

update_ip_set
```

사용 사례

```text
ACL 조회

Rule 조회

IP 차단

예외 IP 등록
```

---

## 6.3 Cortex MCP

목적

```text
Cortex XDR

Cortex XSIAM
```

주요 Tool

```text
search_alert

search_incident

search_endpoint

search_ioc

run_xql
```

사용 사례

```text
IOC 조회

EDR 이벤트 분석

Incident 조사

XQL 검색
```

---

## 6.4 PAN-OS MCP

목적

```text
Palo Alto Firewall 운영
```

주요 Tool

```text
search_policy

search_traffic

search_threat

search_system_log

search_nat
```

사용 사례

```text
정책 조회

트래픽 분석

Threat 분석

시스템 로그 조회
```

---

# 7. 상관관계 분석 시나리오

## 공격 IP 분석

사용자 질문

```text
1.2.3.4 공격자 분석
```

Workflow

```text
Orchestrator

    ↓

Athena MCP
