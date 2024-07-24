1. 설명:
AWS 환경을 지속적으로 모니터링하는 위협 탐지 서비스로써 잠재적인 보안 위험에 대비할 수 있습니다. 
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/fbe8f468-d429-4fec-a222-2f2a9bfe4d8d)

2. 필요 데이터원본:
- AWS CloudTrail 이벤트 로그: AWS CloudTrail은 AWS API 호출 기록을 제공합니다. AWS Management Console, AWS SDK, 커맨드를 사용하여 수행된 API 호출 도구 및 특정 AWS 서비스등.
- AWS CloudTrail 관리 이벤트: 컨트롤 플레인 이벤트라고도 합니다. AWS 계정의 리소스에 대해 수행되는 관리작업을 뜻합니다. 보안 구성 작업(IAttachRolePolicy), 데이터 라우팅을 위한 규칙 구성, 로깅 설정 등
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/a2f2e7ed-7c1a-486a-bc4d-0b6865f5f813)

- VPC Flow log: AWS 환경 내의 EC2 인스턴스에 연결된 네트워크 인터페이스에서 사용됩니다. GuardDuty를 활성화하면 계정 내 EC2 인스턴스의 VPC 흐름 로그 분석이 즉시 시작됩니다.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/4c5f4dc7-8c06-4872-a13c-9aaf1331919d)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/610b9cba-86f2-4116-8c8a-e52145af98fd)

- DNS 로그: EC2 인스턴스에 AWS DNS resolver를 사용하는 경우 GuardDuty는 AWS DNS resolver를 통해 요청 및 응답 DNS 로그에 액세스하고 처리할 수 있습니다.
OpenDNS 또는 구글DNS와 같은 퍼블릭 DNS를 사용하는 경우 GuardDuty는 해당 DNS 로그에 액세스하고 처리할 수 없습니다.

!!대부분의 CloudTrail 이벤트는 리전에 생성되지만, AWS Identity and Access Management(IAM), AWS Security Token Service(AWS STS), AWS S3, Amazon Roue 53과 같은 글로벌 서비스는
해당 이벤트를 복제하여 GuardDuty를 활성화한 리전에서 처리합니다. 


3. GuardDuty 필요 역할
- GuardDuty 서비스 역할
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/d5b646f2-4650-4955-a6a8-00a9107980b8)
- GuardDuty 멀웨어 보호 역할
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/7f088a42-ad8c-405c-96e3-5c7e89ab49a1)

4. 부가 기능:
- 기본 위협 탐지(default): AWS CloudTrail 관리 이벤트 분석, EC2 VPC 흐름 로그 분석, EC2 DNS 쿼리 로그 분석 제공
  
- GuardDuty Lambda Protection: 잠재적인 보안 위협으로부터 Lambda 함수를 보호합니다. AWS Lamda 함수에서 VPC 네트워킹을 사용하도록 구성된 경우 탄력적 네트워크 인터페이스(ENI)에 대한 VPC Flow 로그를 활성화할 필요가 없으며, 악의적인 코드 조각이 Lamda 함수에 포함되어있는 경우 GuardDuty가 결과를 생성합니다.

- GuardDuty EKS Protection: 일반적으로 GuardDuty는 EKS 컨트롤 플레인 로깅을 관리하거나 로그를 생성하지 않습니다. 해당 기능을 사용하려면 EKS 컨트롤 플레인 로깅 활성화가 필수적이며, 활성화 시 즉시 GuardDuty가 모니터링을 시작합니다. 예를 들어 클러스트를 만들고 잠재적으로 악의적이고 의심스러운 활동을 분석합니다. [EKS 문서자료 참조할 것]

- Malware-Protection for EC2 in AWS GuardDuty: EC2 인스턴스 및 컨테이너 워크로드에 연결된 AWS EBS(Azure의 Managed 디스크와 같은 블록 수준 스토리지를 의미) 볼륨을 스캔하여 멀웨어 유무를 탐지합니다. 해당 기능은 EC2 인스턴스를 포함/제외 여부를 결정할 수 있는 스캔 옵션과 스냅샷 보존 기간을 설정하는 옵션을 제공합니다. 스냅샷의 보존은 멀웨어가 발견된 경우에만 보존됩니다.
 1)gdu-initiated-malware-scan: GuardDuty는 자동으로 EC2 인스턴스에 연결된 EBS 볼륨에 대한 에이전트 없는 스캔 또는 컨테이너 워크로드를 사용하여 멀웨어를 감지함. 멀웨어 검사는 24시간마다 한번씩(매일 한번) 호출함
  ![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/db446f6d-6643-4f61-922d-74a7d33adf4e)
 2)on-demand-malware-scan: 연결된 EBS 볼륨에서 멀웨어의 존재를 탐지하며 구성이 필요하지 않은 경우 주문형 멀웨어 검사를 시작할 수 있음. gdu-initiated-malware-scan과 차이점은 24시간 경과까지 기다릴 필요가 없으며, 수동으로 EC2 인스턴스(ARN)에 대한 스캔을 수행합니다. 사용자가 필요할때마다 수행됩니다.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/bd0c7d5f-7ecc-43dc-9592-267e300fcb9a)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/31263d67-c122-4e93-9cc8-c5375629ebf2)

- GuardDuty S3 Protection: AWS S3 버킷에 대해 자동으로 멀웨어 스캔을 시작합니다. 제공되는 주요 작업은 다음과 같음
  1) 스캔 항목 선택: 모든 접두사 또는 특정 접두사에 업로드되는 파일을 스캔합니다(최대 5개)
  2) 업로드된 객체에 대한 자동 검사: 멀웨어 스캔 활성화 후 버컷에 대해 새로 업로드되는 객체에서 자동 스캔을 시작함
  3) Enable through console or using API: S3에 대한 멀웨어 방지를 활성화하는 기본 방법
  4) 스캔한 S3 객체 태깅 지원(selected): 각 멀웨어 스캔 후 GuardDuty에서 태그를 추가합니다. 업로드된 S3 객체의 스캔 상태를 나타내며 태그를 사용하여, 태그 기반 액세스제어(TBAC)를 설정할 수 있음. S3의 경우 예를 들어 악성으로 판명되면 태그 값은 'THREATS_FOUND'로 명시됨
  5) AWS EventBridge 알림: S3 멀에어 검사 상태에 대한 알림을 받음
  6) CloudWatch 지표: GuardDuty 콘솔에 포함된 지표를 봄. 지표에는 S3 객체에 대한 세부 정보가 포함됨 

- GuardDuty RDS Protection: RDS 로그인 활동을 분석하고 프로파일링하여 잠재적 액세스 위협을 확인. AWS Aurora MySQL 및 PostgreSQL 호환, 또는 PostgreSQL용 AWS RDS 해당. 해당 기능은 RDS Protection에 추가 작업을 필요로하지 않으며, 데이터베이스 성능에 영향을 미치지 않도록 설계
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/c9220ce2-c79e-43aa-9f70-f01c9ee00bab)
처음 활성화 시 기본 baseline을 설정하는 학습 시간이 필요한. 최대 2주 동안 관련 비정상적인 로그인 결과가 있어야함.

- GuardDuty 런타임 이벤트 모니터링: 보안 에이전트를 사용하여 파일과 같은 런타임 동작에 가시성을 추가합니다. 액세스, 프로세스 실행, 커맨드 입력 및 네트워크 연결 등 잠재적 위협에 대해 모니터링하려는 각 리소스등에서 보안을 관리할 수 있음. 에이전트를 자동/수동 배포할 수 있음

  1)EC2 인스턴스에서 런타임 모니터링 작동방식: 현재 실행 중인 이벤트 및 Amazon EC2 인스턴스 내 새로운 프로세스 데이터가 보안 에이전트를 통해 수집되며, GuardDuty로 전송합니다. 보안 에이전트는 인스턴스 수준에서 동작하며, 선택적 인스턴스인 경우 보안 에이전트가 선택적으로 설치될 수 있음
  2)EKS 클러스터에서 런타임 모니터링 작동방식: GuardDuty 보안 에이전트인 EKS 추가 기능 aws-guardduty-agent가 구성되며, EKS 클러스터에서 런타임 이벤트를 수신합니다. 자동/수동 배포할 수 있으며 자동 구성 시, Amazon Virtual Private Cloud(VPC) 엔드포인트가 자동 생성됩니다. AWS Fargate(서버리스 Azure 컨테이너 인스턴스와 유사)에서 실행되는 EKS 클러스터는 현재 지원하지 않음!!!
  3)Fargate에서 런타임 모니터링 작동방식(AWS ECS/Elastic Container Service): 현재 런타임 모니터링은 GuardDuty를 통해서만 AWS ECS(Fargate)에 대한 보안 에이전트 관리를 지원합니다(시중에 Container Injection or CaaS Sidcar 방식으로 배포되는 경우가 있음)
  4)배포방식: 런타임 이벤트는 대상 EC2가 SSM(AWS System Manager Agent) 관리 대상이어야 한다는 전제 조건이 필요함. 자동 에이전트는 관련 기능 활성화가 필요하면 태그 값에 'GuardDutyManaged:true/false' 다음 값 입력 시 대상을 포함/제외할 수 있음
  ![image](https://github.com/user-attachments/assets/b512358e-de1f-4190-8915-4b74382e886b)
  수동 에이전트 구성 시
  
  제약 사항
  ![image](https://github.com/user-attachments/assets/890ce692-ca61-4fe3-a184-8b4ea0e8b6d4)
  ![image](https://github.com/user-attachments/assets/a6caedf4-b5d3-4387-8a16-ebc156a8146e)


