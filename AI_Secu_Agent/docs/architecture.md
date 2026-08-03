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

# 7. 분석 시나리오

## 특정 URI 공격 분석

사용자 질문

```text
/api/login URI에 대한 공격 내역을 분석해줘
```

Workflow

```text
사용자 요청

    ↓

AI Agent

    ↓

MCP Orchestrator

    ↓

Athena MCP

    ↓

AWS WAF 로그 조회

URI = /api/login

    ↓

공격 통계 분석

- Block Count
- Allow Count
- Source IP
- Country
- User-Agent
- Matched Rule

    ↓

PAN-OS MCP

    ↓

동일 Source IP 검색

- Traffic Log
- Threat Log
- Session Log

    ↓

Correlation Engine

    ↓

Bedrock

    ↓

최종 분석 결과 생성
```

---

### Athena MCP 결과 예시

```json
{
  "uri": "/api/login",
  "blocked_requests": 341,
  "allowed_requests": 12,
  "top_source_ips": [
    "1.2.3.4",
    "5.6.7.8"
  ],
  "top_countries": [
    "RU",
    "CN"
  ],
  "matched_rule": "AWSManagedRulesKnownBadInputsRuleSet"
}
```

---

### PAN-OS MCP 결과 예시

```json
{
  "source_ip": "1.2.3.4",
  "session_count": 52,
  "threat_count": 14,
  "top_application": "web-browsing"
}
```

---

### Correlation 결과 예시

```text
/api/login URI에 대해 최근 24시간 동안
341건의 공격 시도가 탐지되었습니다.

주요 공격 Source IP는

1.2.3.4
5.6.7.8

이며 AWS WAF에서 차단되었습니다.

Palo Alto Firewall 로그 분석 결과
1.2.3.4 IP에 대한 통신 세션이
52건 확인되었습니다.

방화벽 Threat 로그에서도
14건의 위협 이벤트가 확인되었습니다.

해당 URI는 현재 공격 집중도가 높은
고위험 웹 애플리케이션 경로입니다.
```

---

## 특정 URI 정책 검증

사용자 질문

```text
/payment URI는 WAF에서 차단되고 있는데
Firewall에서도 차단되고 있는가?
```

Workflow

```text
MCP Orchestrator

    ↓

WAF MCP

    ↓

Web ACL 조회

Rule 조회

차단 IP 식별

    ↓

PAN-OS MCP

    ↓

Security Policy 조회

Traffic Log 조회

허용 정책 확인

    ↓

Correlation Engine

    ↓

Bedrock
```

---

### 결과 예시

```text
/payment URI에 대한 공격은
AWS WAF에서 정상적으로 차단되고 있습니다.

그러나 공격 Source IP 중
3개는 Firewall 정책

Allow-Web-Traffic

규칙에 의해 허용되고 있습니다.

방화벽 정책 검토를 권장합니다.
```

---

## URI 기반 공격 트렌드 분석

사용자 질문

```text
최근 공격이 가장 많이 발생한 URI Top 10 분석
```

Workflow

```text
Athena MCP

    ↓

WAF Log Aggregation

    ↓

URI별 공격 건수 집계

    ↓

상위 공격자 분석

    ↓

PAN-OS Traffic 확인

    ↓

Bedrock 보고서 생성
```

---

### 결과 예시

```text
최근 24시간 기준

TOP 10 공격 URI

1. /api/login
2. /administrator
3. /wp-login.php
4. /cgi-bin/test.cgi
5. /actuator/env
6. /phpmyadmin
7. /login.jsp
8. /api/auth
9. /xmlrpc.php
10. /console
```

---

## Cortex EDR 위협 분석

사용자 질문

```text
최근 Critical Alert를 분석해줘
```

Workflow

```text
AI Agent

    ↓

Cortex MCP

    ↓

Alert 조회

Incident 조회

Endpoint 조회

Process 조회

Command Line 조회

File Hash 조회

    ↓

Bedrock
```

---

### 결과 예시

```text
최근 24시간 동안
Critical Alert가 12건 탐지되었습니다.

가장 많이 탐지된 유형은

- Malware
- Credential Access
- Lateral Movement

입니다.

특정 Endpoint에서는

powershell.exe

프로세스를 통해 의심 명령 실행이
확인되었습니다.

관련 SHA256 Hash는
위협 인텔리전스 DB에 등록되어 있습니다.
```

---

## Cortex Incident 분석

사용자 질문

```text
최근 Incident를 요약해줘
```

Workflow

```text
Cortex MCP

    ↓

Incident 조회

Alert 연관분석

Host 분석

User 분석

    ↓

Bedrock
```

---

### 결과 예시

```text
최근 7일 동안
총 8건의 Incident가 생성되었습니다.

이 중 3건은

Credential Theft

관련 이벤트로 분류되었습니다.

가장 많이 영향을 받은
Endpoint는

HOST-001
HOST-002

입니다.
```
