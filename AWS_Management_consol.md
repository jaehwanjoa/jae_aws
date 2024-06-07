AWS Management Consol은 AWS 리소스 관리를 위한 광범위한 서비스 콘솔 모음으로 구성된 웹 애플리케이션이다. 
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/01bca760-d8bc-474b-a821-ba2b63a4c2e2)
다음은 주요 다섯 개의 컨트롤이 있다.

1. AWS 걔정 정보
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/f6adcc1b-7fb9-486f-9bc3-9575db2cd53c)
   - Accounts: 주소, 연락처 정보, 결제 설정 등 계정에 대한 세부 정보를 다룸
   - Organization: AWS 계정을 사용자가 생성하고 중앙에서 관리하는 단일 조직으로 통합할 수 있는 계정 관리 서비스
   - Service Quotas: 서비스 한도라고 하는 할당량은 AWS 계정의 리소스, 작업 및 항목에 대한 최댓값으로 예를 들어 탄력적 IP 주소 5개를 할당하는 것과 같은 기본 값이 있다. 이러한 한도를 늘릴 수 있다.
   - Billing Dashboard: AWS 지출을 전반적으로 파악할 수 있다.
   - Security credentials: IAM 사용자 페이지로 이동하여 암호 변경, 2단계 인증, AWS API 키 생성 등을 수행할 수 있음
   - Settings: 일반 설정 구성 페이지로 이동함. 기본 언어 및 리전은 물론 콘솔 글로벌 설정을 관리할 수 있다.
  
2. AWS 리전: AWS 글로벌 인프라는 리전별로 그룹화되고, 각 서비스는 한 리전에서 호스팅됨. 단, AWS IAM 또는 Route 53과 같은 서비스는 리전별이 아닌 글로벌로 명시됨
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/dd20493c-4a20-4ea9-80c4-c0db96143928)

3. AWS CloudShell(Azure CLI): 콘솔 보안 인증 정보로 사전 인증된 브라우저 기반 셀 환경을 시작할 수 있다. 쉘 왼쪽 상단에 현재 리전 정보를 표시함
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/93a69818-3c73-43aa-b6d8-0d82495f5d01)
