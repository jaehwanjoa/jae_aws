# MCP Orchestrator Design

## 개요

MCP Orchestrator는 Security AI Agent Platform의 중앙 제어 계층이다.

사용자의 자연어 요청을 분석하여 적절한 MCP Tool을 선택하고 호출하며,
결과를 수집하여 최종 분석 결과를 생성한다.

---

# 역할

## Tool Routing

사용자 질문에 따라 적절한 MCP를 선택한다.

예)

```text
/api/login 공격 분석
```

↓

```text
Athena MCP
```

---

## Workflow Control

복수 MCP 호출 순서를 관리한다.

예)

```text
URI 분석

↓

Athena

↓

Source IP 추출

↓

PAN-OS Threat Log 조회

↓

결과 통합
```

---

## Correlation Analysis

여러 MCP 결과를 기반으로 상관관계 분석 수행

예)

```text
WAF 공격자 IP

+

Firewall Threat Event

=

고위험 공격 추정
```

---

## Response Enrichment

Bedrock이 이해하기 쉬운 형태로 데이터 정규화

---

# MCP Mapping

## Athena MCP

사용 목적

```text
WAF 로그 분석

URI 분석

IP 분석

공격 트렌드 분석
```

---

## Cortex MCP

사용 목적

```text
Issue 조회

Incident 조회

Endpoint 조회

XQL 분석
```

---

## PAN-OS MCP

사용 목적

```text
Threat Log 조회
```

---

# Workflow 1

## URI 공격 분석

사용자 요청

```text
/api/login 공격 분석
```

실행 흐름

```text
Athena MCP

search_uri()

↓

공격 통계 수집

↓

Source IP 수집

↓

PAN-OS MCP

search_threat()

↓

위협 여부 확인

↓

Correlation Engine

↓

분석 결과 생성
```

출력 예시

```text
최근 24시간 동안
/api/login URI에 대해

341건의 공격이 발생했습니다.

상위 공격 Source IP

1.2.3.4

5.6.7.8

중 1.2.3.4 IP는
Firewall Threat Log에서도 탐지되었습니다.
```

---

# Workflow 2

## 공격자 IP 분석

사용자 요청

```text
1.2.3.4 분석해줘
```

실행 흐름

```text
Athena MCP

search_source_ip()

↓

접근 URI 조회

↓

PAN-OS MCP

search_threat()

↓

위협 이벤트 수집

↓

Correlation Engine
```

출력 예시

```text
1.2.3.4는

/api/login

/wp-login.php

를 대상으로 공격을 시도했습니다.

Firewall Threat Log에서도
14건의 이벤트가 확인되었습니다.
```

---

# Workflow 3

## 공격 트렌드 분석

사용자 요청

```text
최근 공격 트렌드 보여줘
```

실행 흐름

```text
Athena MCP

top_attacked_uri()

↓

top_attacker_ip()

↓

top_rule_match()

↓

통계 생성
```

출력 예시

```text
최근 24시간 동안

가장 많이 공격받은 URI

1. /api/login

2. /administrator

3. /wp-login.php
```

---

# Workflow 4

## Cortex Issue 분석

사용자 요청

```text
Critical Issue 보여줘
```

실행 흐름

```text
Cortex MCP

get_issues()

↓

Severity=Critical

↓

결과 요약
```

출력 예시

```text
Critical Issue

12건 발견

가장 높은 위험도 항목

Issue #12345
Issue #12346
```

---

# Workflow 5

## Cortex Incident 분석

사용자 요청

```text
최근 Incident 분석
```

실행 흐름

```text
Cortex MCP

search_incident()

↓

Incident 집계

↓

요약 생성
```

---

# Intent Routing Table

| 사용자 의도 | MCP |
|------------|------|
| URI 분석 | Athena |
| 공격자 IP 분석 | Athena + PANOS |
| 공격 트렌드 | Athena |
| Threat 확인 | PANOS |
| Issue 분석 | Cortex |
| Incident 분석 | Cortex |
| Endpoint 분석 | Cortex |
| XQL 실행 | Cortex |

---

# Future Expansion

향후 추가 예정 MCP

```text
Security Hub MCP

GuardDuty MCP

CloudTrail MCP

Prisma Cloud MCP
```

추가 시 Orchestrator Routing Table만 확장한다.

---

# Design Principle

1. MCP는 서로 직접 호출하지 않는다.

2. 모든 MCP 호출은 Orchestrator를 통해 수행한다.

3. MCP는 데이터 수집 역할만 수행한다.

4. 상관관계 분석은 Orchestrator가 수행한다.

5. 최종 자연어 응답 생성은 Bedrock이 수행한다.
