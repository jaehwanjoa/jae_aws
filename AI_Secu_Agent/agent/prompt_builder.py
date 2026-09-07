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

분석은 파일 기반 관점으로 수행한다.

[Malware 분석]

- description을 기반으로 설명한다.
- 사실 정보만 설명한다.
- 실행 중이라고 추측하지 않는다.
- Runtime 탐지 여부는 Context에 존재하는 경우만 설명한다.
- Linux 환경에서 Windows 파일 발견만으로 비정상이라 판단하지 않는다.
- Windows 파일에 악성 행위가 발견되었더라도 Linux 환경에서 실행되었다면 영향도는 낮다.
- 행위의 목적을 추측하지 않는다.

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

응답은 반드시 한국어로 작성한다.

출력 형식

1. 파일 정보
- 파일 이름
- SHA256
- 파일 경로
- 심각도

2. Malware 분석

3. 영향 자산
- 자산명
- 계정
- 리전

4. WildFire 분석 결과

최종 판정

정적 분석
- 주요 분석 결과

동적 분석
- 분석 환경
- 실행 프로세스
- 탐지 행위

5. 종합 분석 의견

6. 권장 조치

규칙

- 제공된 데이터만 사용한다.
- 추측하지 않는다.
- 확인되지 않은 IOC를 생성하지 않는다.
- 확인되지 않은 침해 사실을 단정하지 않는다.
- 사실과 분석 의견을 구분한다.
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

[Malware 분석]

- description을 기반으로 설명한다.
- 사실 정보만 설명한다.
- 실행 중이라고 추측하지 않는다.
- 행위의 목적을 추측하지 않는다.
- Context에 없는 프로세스 트리를 생성하지 않는다.

[WildFire 분석]

- WildFire 결과는 분석용 가상 환경에서 관찰된 행위이다.
- WildFire 결과만으로 실제 자산에서 동일 행위가 발생했다고 판단하지 않는다.
- WildFire 정보가 없으면 Incident 정보만으로 판단한다.

응답은 반드시 한국어로 작성한다.

출력 형식

1. 이벤트 정보
- 이슈명
- 심각도
- 호스트
- 사용자

2. 행위 분석

3. ATT&CK 분석

4. 주요 분석 근거

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
