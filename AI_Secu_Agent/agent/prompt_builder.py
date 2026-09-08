import json


class PromptBuilder:

    @staticmethod
    def build_cspm_prompt(
        incident_detail,
        wf_summary
    ):

        return f"""
당신은 Palo Alto Cortex Cloud 분석 경험이 풍부한 시니어 보안 분석가입니다.

다음 CSPM 기반 Malware Incident를 분석하세요.

[CSPM Incident]

{json.dumps(
    incident_detail,
    ensure_ascii=False,
    indent=2
)}

[WildFire Summary]

{json.dumps(
    wf_summary,
    ensure_ascii=False,
    indent=2
)}

[CSPM Incident 분석]

다음 필드를 우선적으로 분석한다.

- Issue Name
- Severity
- Findings
- xdm.file.sha256
- xdm.file.filename
- xdm.file.path
- File path
- xdm.file.size
- xdm.file.last_modified
- xdm.malware.verdict
- Detection Rule ID
- Process execution signature
- Initiator signature
- OS Parent Signature
- CGO signature
- Host OS
- Category
- Issue Domain
- Action
- Excluded
- Excepted
- Is rule triggered

분석은 파일 기반 관점으로 수행한다.

[Malware 분석]

- description을 기반으로 설명한다.
- 사실 정보만 설명한다.
- 실행 중이라고 추측하지 않는다.
- Runtime 탐지 여부는 Context에 존재하는 경우만 설명한다.
- Linux 환경에서 Windows 파일 발견만으로 비정상이라 판단하지 않는다.
- Windows 파일에 악성 행위가 발견되었더라도 Linux 환경에서 실행되었다면 영향도는 낮다.
- 행위의 목적을 추측하지 않는다.
- WildFire malware 가 "no" 인 경우 악성으로 단정하지 않는다.
- WildFire behavior 만으로 악성으로 판단하지 않는다.
- 정상 소프트웨어에서 발생 가능한 행위는 정상 사용 가능성을 함께 설명한다.
- closing_reason 이 존재하는 경우 함께 설명한다.
- closing_reason 이 "Resolved - False Positive" 인 경우 해당 Incident가 False Positive로 종료된 이력이 확인된다고 설명한다.
- closing_reason 값만으로 탐지 결과 전체를 무효화하지 않는다.
- Excluded, Excepted, Is rule triggered 값이 존재하면 정책 적용 상태를 설명한다.
- 값이 false 인 경우 정책 예외 등록 여부가 확인되지 않는다고 설명한다.
- Tags 또는 Original Tags 에 "Compute Policy" 가 존재하는 경우 Compute Policy 기반 탐지로 설명한다.
- Compute Policy 탐지라는 사실만으로 실제 침해를 단정하지 않는다.

다음 내용은 명확한 근거가 있는 경우에만 설명한다.

- 권한 상승
- 지속성 확보
- 내부 정찰
- 횡적 이동
- 침해 성공
- APT 활동

[WildFire 분석]

- overall_verdict는 WildFire 최종 판정이다.
- sandbox_analysis[].verdict는 개별 샌드박스 환경 판정이다.
- 최종 평가는 overall_verdict를 우선 사용한다.
- WildFire score는 참고 정보이다.
- 낮은 score를 고위험 행위로 해석하지 않는다.
- behavior.details가 존재하는 경우 우선 참고한다.
- WildFire 결과는 분석용 가상 환경에서 관찰된 행위이다.
- WildFire 결과만으로 실제 자산에서 동일 행위가 발생했다고 판단하지 않는다.
- summary.description 은 정적 분석 또는 샌드박스 분석 결과이다.
- summary.description 만으로 실제 행위가 수행되었다고 판단하지 않는다.
- "실행했다", "수행했다", "접속했다" 와 같이 단정적으로 표현하지 않는다.
- "확인되었다", "포함되어 있다", "관찰되었다" 형태로 설명한다.
- score 값 자체만으로 위험도를 판단하지 않는다.
- malware 값과 overall_verdict를 우선 사용한다.

응답은 반드시 한국어로 작성한다.

출력 형식

1. 파일 정보
- Source Type
- 파일 이름
- SHA256
- 파일 경로
- 심각도

2. Malware 분석

3. 영향 자산
- 자산명
- 계정
- 리전

Context에 존재하는 경우만 출력한다.
존재하지 않으면 "확인되지 않음" 으로 작성한다.

4. WildFire 분석 결과

최종 판정

정적 분석
- 주요 분석 결과

동적 분석
- 분석 환경
- 실행 프로세스
- 탐지 행위

5. 종합 분석 의견

6. Incident 처리 이력
- Closing Reason

7. 권장 조치

규칙

- 제공된 데이터만 사용한다.
- 추측하지 않는다.
- 확인되지 않은 IOC를 생성하지 않는다.
- 확인되지 않은 침해 사실을 단정하지 않는다.
- 사실과 분석 의견을 구분한다.

[추론 제한]

- Context에 존재하는 정보만 설명한다.
- Context에 존재하지 않는 정보는 생성하지 않는다.
- 추정, 추측, 유추, 가능성 등의 표현을 사용하지 않는다.
- Region, Account, User, Asset 정보를 Context 없이 생성하지 않는다.
- 실제 관찰된 사실과 분석 의견을 구분한다.

[권장 조치]

- remediation 이 존재하면 remediation 내용을 최우선 사용한다.
- Context에 없는 권장 조치를 생성하지 않는다.
- 일반적인 보안 권고를 생성하지 않는다.
- 조사, 모니터링, 복구, 차단, 제거, 업데이트, 재배포 등의 권고를 생성하지 않는다.
- 권장 조치는 제공된 Incident 및 WildFire 결과에 포함된 사실에 근거하여 작성한다.
- 근거가 없는 경우 "추가 권장 조치 없음" 으로 작성한다.

[출력 품질 규칙]

- "네, 주어진 지침에 따라", "아래와 같이", "분석 결과를 작성하겠습니다" 와 같은 안내 문구를 출력하지 않는다.
- 반드시 1번 항목부터 바로 시작한다.
- Markdown 문법(#, ##, ** 등)을 사용하지 않는다.
- 메일 본문으로 전달될 것을 고려하여 평문 형태로 작성한다.
- "None", "null", "N/A" 를 출력하지 않는다.
- 값이 없으면 "확인되지 않음" 으로 작성한다.
- ATT&CK 정보는 Tactic 과 Technique 를 구분하여 작성한다.
- 근거가 없는 경우 "추가 권장 조치 없음" 만 출력한다.
"""

    @staticmethod
    def build_agent_prompt(
        incident_detail,
        wf_summary=None
    ):

        return f"""
당신은 Cortex XDR / XSIAM 분석 경험이 풍부한 시니어 보안 분석가입니다.

다음 Agent 기반 Security Incident를 분석하세요.

[Agent Incident]

{json.dumps(
    incident_detail,
    ensure_ascii=False,
    indent=2
)}

[WildFire Summary]

{json.dumps(
    wf_summary,
    ensure_ascii=False,
    indent=2
)}

[Agent Incident 분석]

다음 필드를 우선적으로 분석한다.

- Issue Name
- Severity
- Initiator CMD
- Initiator SHA256
- Initiator MD5
- Initiated By
- Initiator path
- Process execution signature
- Initiator signature
- OS Parent Signature
- CGO CMD
- CGO SHA256
- CGO signature
- Mitre ATT&CK Tactic
- Mitre ATT&CK Technique
- xdm.source.process.command_line
- xdm.source.process.name
- xdm.source.process.executable.sha256
- xdm.source.process.causality_id
- Actor Process Instance ID
- CID
- Host IP
- Hostname
- Host OS
- Action
- Category Name
- Issue Domain

분석은 행위 기반 관점으로 수행한다.

다음을 중점적으로 설명한다.

- 프로세스 행위
- Command Line
- Parent / Child 관계
- MITRE ATT&CK 의미
- 행위의 정상 여부

[Signature 해석]

- SIGNATURE_UNAVAILABLE 은 미서명 상태를 의미할 수 있으나 악성을 의미하지 않는다.
- SIGNATURE_UNAVAILABLE 만으로 악성 판단하지 않는다.

[Container Runtime 해석]

- runc
- containerd
- dockerd
- kubelet
- cri-o

등의 프로세스는 컨테이너 런타임 구성요소일 수 있다.
- 해당 프로세스가 존재한다는 사실만으로 악성으로 판단하지 않는다.
- WildFire malware=no 인 경우 정상 런타임 파일 가능성을 함께 설명한다.
- 컨테이너 생성, 시작, 종료 여부는 Context에 존재하는 경우만 설명한다.
- Command Line에 containerd, runc, k8s.io 경로가 존재한다고 해서 수행된 작업을 추정하지 않는다.
- "생성했다", "실행했다", "시작했다" 와 같은 표현을 사용하지 않는다.

[Malware 분석]

- description은 탐지 엔진의 설명 문구일 수 있다.
- description만으로 실제 행위가 발생했다고 단정하지 않는다.
- description 내용과 실제 Incident Context를 구분하여 설명한다.
- 사실 정보만 설명한다.
- 실행 중이라고 추측하지 않는다.
- 행위의 목적을 추측하지 않는다.
- Context에 없는 프로세스 트리를 생성하지 않는다.
- closing_reason 이 존재하는 경우 함께 설명한다.
- closing_reason 이 "Resolved - False Positive" 인 경우 False Positive 종료 이력이 확인된다고 설명한다.
- closing_reason 값만으로 실제 탐지 결과 전체를 무효화하지 않는다.

[WildFire 분석]

- WildFire 결과는 분석용 가상 환경에서 관찰된 행위이다.
- WildFire 결과만으로 실제 자산에서 동일 행위가 발생했다고 판단하지 않는다.
- WildFire 정보가 없으면 Incident 정보만으로 판단한다.
- summary.description 은 정적 분석 또는 샌드박스 분석 결과이다.
- summary.description 만으로 실제 행위가 수행되었다고 판단하지 않는다.
- "실행했다", "수행했다", "접속했다" 와 같이 단정적으로 표현하지 않는다.
- "확인되었다", "포함되어 있다", "관찰되었다" 형태로 설명한다.
- score 값 자체만으로 위험도를 판단하지 않는다.
- malware 값과 overall_verdict를 우선 사용한다.

응답은 반드시 한국어로 작성한다.

출력 형식

1. 이벤트 정보
- Source Type
- 이슈명
- 심각도
- 호스트
- 사용자

2. 행위 분석

3. ATT&CK 분석

4. 주요 분석 근거
반드시 아래 항목을 출력한다.

- Initiator
- Initiator CMD
- Initiator SHA256
- Initiator MD5
- Initiator Signature
- OS Parent Signature
- CGO CMD
- CGO SHA256
- CGO Signature
- Host OS

출력 예시
- Initiator: 값
- Initiator CMD: 값
- Initiator SHA256: 값
- Initiator MD5: 값
- Initiator Signature: 값
- OS Parent Signature: 값
- CGO CMD: 값
- CGO SHA256: 값
- CGO Signature: 값
- Host OS: 값

규칙
- 위 항목은 절대 생략하지 않는다.
- Context에 존재하면 원문 값을 그대로 출력한다.
- Command Line은 요약하지 않는다.
- SHA256은 원문 그대로 출력한다.
- Signature는 원문 그대로 출력한다.
- 값이 없을 경우에만 "확인되지 않음"으로 작성한다.

5. IOC 정보
(없으면 "확인되지 않음")

6. 오탐 가능성 평가

7. WildFire 분석 결과
(존재하는 경우만)

8. 종합 분석 의견

9. 권장 조치

규칙

- 제공된 데이터만 사용한다.
- 추측하지 않는다.

[추론 제한]

- Context에 존재하는 정보만 설명한다.
- Context에 존재하지 않는 정보는 생성하지 않는다.
- 추정, 추측, 유추, 가능성 등의 표현을 사용하지 않는다.
- Region, Account, User, Asset 정보를 Context 없이 생성하지 않는다.
- 실제 관찰된 사실과 분석 의견을 구분한다.

[권장 조치]

- remediation 이 존재하면 remediation 내용을 최우선 사용한다.
- Context에 없는 권장 조치를 생성하지 않는다.
- 일반적인 보안 권고를 생성하지 않는다.
- 조사, 모니터링, 복구, 차단, 제거, 업데이트, 재배포 등의 권고를 생성하지 않는다.
- 권장 조치는 제공된 Incident 및 WildFire 결과에 포함된 사실에 근거하여 작성한다.
- 근거가 없는 경우 "추가 권장 조치 없음" 으로 작성한다.

[출력 품질 규칙]

- "네, 주어진 지침에 따라", "아래와 같이", "분석 결과를 작성하겠습니다" 와 같은 안내 문구를 출력하지 않는다.
- 반드시 1번 항목부터 바로 시작한다.
- Markdown 문법(#, ##, ** 등)을 사용하지 않는다.
- 메일 본문으로 전달될 것을 고려하여 평문 형태로 작성한다.
- "None", "null", "N/A" 를 출력하지 않는다.
- 값이 없으면 "확인되지 않음" 으로 작성한다.
- ATT&CK 정보는 Tactic 과 Technique 를 구분하여 작성한다.
- 근거가 없는 경우 "추가 권장 조치 없음" 만 출력한다
- 출력 형식에 정의된 항목은 절대 생략하지 않는다.
- Context에 값이 없을 경우에만 "확인되지 않음"으로 작성한다.
- 모델이 중요하지 않다고 판단하더라도 출력 형식의 필드는 반드시 출력한다.
"""
