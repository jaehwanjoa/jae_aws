1. 소개:
애플리케이션에 보내는 웹 요청을 모니터링하고 콘텐츠에 대한 액세스를 제어하는데 사용할 수 있는 웹애플리케이션 방화벽으로써, L3/L4와 L7에서 AWS 리소스에 대한 DDoS 공격에 대응합니다(Shield 통합)
2. 리소스 보호 대상: 글로벌 또는 지역 리소스 유형을 보호할 수 있음. 웹ACL은 관련 리소스가 위치한 지역에 있어야함
- Amazon CloudFront Distribution(관리형 CDN 서비스)
- Amazon API Gateway REST API
- Application Load Balancer
- AWS APpSync GaphQL API
- Amazon Cognito 사용자 풀(관리형 사용자 인증 서비스)
- AWS App Runner 서비스(관리형 컨테이너 및 서버리스 배포 서비스)
- AWS Verified Access Instance
3. 지원 기능
- 지정한 요청을 제외한 모든 요청 허용: 공개 웹사이트의 콘텐츠를 제공하되 공격자의 요청도 차단하려는 경우 유용
- 지정 항목을 제외하고 모든 요청 차단: 웹 사이트를 검색하기 위해 사용하는 IP와 웹 요청의 속성을 통해 사용자를 즉시 식별할 수 있는 제한된 웹사이트에 콘텐츠를 서비스하려는 경우 유용
- 기준에 맞는 요청 수 계산: 처리 방법을 수정하지 않고도 카운트 작업을 사용하여 웹 트래픽을 추적. 이를 일반 모니터링에 사용할 수 있으며, 새 웹 요청 처리 규칙을 테스트하는데도 사용할 수 있음. 웹 요청의 새 속성을 기반으로 요청을 허용하거나 차단하려는 경우 먼저 해당 속성과 일치하는 요청을 AWS WAF 계산하도록 구성할 수 있음. 이렇게하면 일치 요청을 허용하거나 차단하도록 규칙을 전환하기 전에 새 구성 설정을 확인할 수 있음
- 기준에 맞는 요청에 대한 CAPTCHA 또는 챌린지 검사 실행: 요청에 대해 CAPTCHA 및 자동 챌린지 제어를 구현하여 보호된 리소스로 향하는 봇 트래픽을 줄일 수 있음
- 웹 요청의 특성을 사용하여 기준 정의: 요청이 시작되는 IP 주소/국가/헤더 값/문자열(특정 또는 정규식), 요청 길이, 악성일 가능성이 있는 SQL 코드의 존재, 악성일 가능성이 있는 스크립트의 존재(XSS)
- 지정 기준을 충족하는 웹 요청을 허용/차단할 수 있는 규칙 생성: 1분 또는 5분 내 지정된 요청 수를 초과하는 웹 요청을 차단하거나 카운트할 수 있는 정책을 생성할 수 있음
  
4. 작동 방식
![image](https://github.com/user-attachments/assets/a204caa0-b67f-4af4-a4f0-029c5886d170)
5. WCU: AWS WAF 웹 ACL 용량 단위를 지칭. 규칙 그룹 및 웹 ACL을 실행하는 데 필요한 운영 리소스를 계산하고 제어해야 합니다.
- 규칙 WCU: 규칙을 생성, 업데이트할 때 규칙 용량을 계산함. 실행 비용이 적게 드는 간단한 규칙은 처리 능력을 더 많이 사용하는 복잡한 규칙에 비해 WCU를 적게 사용함
- 규칙 그룹 WCU: 최대 용량은 5000WCU로써 규칙 그룹을 수정할 떄 해당 용량 내에 유지되도록 해야함
- 웹 ACL WCU: 웹 ACL의 기본 가격에는 1500 WCU가 포함되며, 최대 용량은 5000WCU. 그 이상 사용 시 추가 요금이 발생함
6. 로깅 및 모니터링 방법
AWS WAF > Web ACLs > 로깅 및 메트릭 활성화, 활성화한 s3 버킷이름 체크
![image](https://github.com/user-attachments/assets/975c7777-ced6-4b02-96d8-5917c9a47e88)
s3 + Athena 확인방안: s3에서 s3 uri 체크(년/월/일 형태의 폴더에서 URI를 체크하면, 해당 기간동안 테이블을 생성할 수 있음)
![image](https://github.com/user-attachments/assets/8410ef40-a1e4-4981-b7aa-74b52c307439)
'https://docs.aws.amazon.com/ko_kr/athena/latest/ug/waf-logs.html' <- 분할없이 WAF 로그 테이블 생성 참조
서버리스 쿼리 서비스인 Athena에서 WAF 로그 테이블 생성(추가 액션이 없는한 영구적으로 생성, 1회만 수행). 아까 체크한 s3 url를 쿼리내 수정 후 실행
![image](https://github.com/user-attachments/assets/22d44157-0496-48c0-9889-3b52955fe0ae)
생성한 WAF 로그 테이블을 쿼리하면 로깅된 이벤트 정보를 확인할 수 있음
![image](https://github.com/user-attachments/assets/95295f6f-ca79-448c-bbe6-ef5fd3084e23)

다음은 AWS WAF의 로그 필드이다. 참고할 것!
1. timestamp: 이벤트가 발생한 시간과 날짜입니다. 일반적으로 UTC 시간으로 기록됩니다.
2. action: AWS WAF에서 수행된 액션(허용, 차단, CAPTCHA 또는 챌린지)입니다.
3. httpMethod: 요청의 HTTP 메소드
4. httprequest: 요청에 대한 메타데이터.
5. httpsourceid: 연결된 리소스의 ID입니다.
6. httpSourceName: ex)CF=CloudFront, APIGW=API Gateway 등
7. httpVersion: HTTP 버전
8. ja3Fingerprint: 요청의 JA3 지문. 클라이언트 TLS 구성의 고유 식별자 역할을 하며, 웹 ACL 규칙에서 JA3 지문 일치를 구성할 때 이 값을 제공.
9. labels: 웹 요청을 평가하는 데 사용된 규칙에 따라 적용. AWS WAF 처음 100개의 레이블을 기록함
10. nonterminatingmatchingrules: 요청과 일치하는 종료되지 않는 규칙 목록.
11. oversizeFields: 웹 ACL에서 검사한 웹 요청 중 검사 한도를 초과한 필드 목록.
12. ratebasedrulelist: 속도 기반 규칙의 목록
13. requestHeadersInserted: 사용자 지정 요청 처리를 위해 삽입된 헤더 목록.
14. requestId: 기본 호스트 서비스에 생성되는 요청ID. ALB 경우 추적 ID입니다. 
15. responseCodeSent: 사용자 지정 응답과 함께 전송된 응답 코드.
16. ruleGroupId: 규칙 그룹ID. 규칙에서 요청을 차단한 경우 ruleGroupID는 terminatingRuleId의 ID와 동일함.
17. ruleGroupList: 일치 정보가 포함된 이 요청에 작용하는 규칙 그룹 목록.
18. terminatingRule: 요청을 종료한 규칙. 
19. terminatingRuleId: 요청을 종료한 규칙ID. 요청을 종료하는 규칙이 없으면 Default_Action.
20. terminatingrulematchdetails: 웹 요청에 대한 검사 프로세스를 종료하는 작업이 포함되어 있음
ex)SQL 명령어 삽입 및 크로스 사이트 스크립팅(XSS) 일치 규칙 문에 대해서만 채워집니다. 
21. terminatingRuleType: 요청을 종료한 규칙의 유형. ex)RATE_BASED, REGULAR, GROUP 및 MANAGED_RULE_GROUP.
22. uri: 요청의 URL
23. webaclid: 웹 ACL의 GUID

