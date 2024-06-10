1. 설명:
AWS 환경을 지속적으로 모니터링하는 위협 탐지 서비스로써 잠재적인 보안 위험에 대비할 수 있습니다. 

2. 필요 데이터원본:
AWS CloudTrail 이벤트 로그: AWS CloudTrail은 AWS API 호출 기록을 제공합니다. AWS Management Console, AWS SDK, 커맨드를 사용하여 수행된 API 호출 도구 및 특정 AWS 서비스등.
AWS CloudTrail 관리 이벤트: 컨트롤 플레인 이벤트라고도 합니다. AWS 계정의 리소스에 대해 수행되는 관리작업을 뜻합니다. 보안 구성 작업(IAttachRolePolicy), 데이터 라우팅을 위한 규칙 구성, 로깅 설정 등
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/a2f2e7ed-7c1a-486a-bc4d-0b6865f5f813)

!!대부분의 CloudTrail 이벤트는 리전에 생성되지만, AWS Identity and Access Management(IAM), AWS Security Token Service(AWS STS), AWS S3, Amazon Roue 53과 같은 글로벌 서비스는
해당 이벤트를 복제하여 GuardDuty를 활성화한 리전에서 처리합니다. 

VPC Flow log: AWS 환경 내의 EC2 인스턴스에 연결된 네트워크 인터페이스에서 사용됩니다. GuardDuty를 활성화하면 계정 내 EC2 인스턴스의 VPC 흐름 로그 분석이 즉시 시작됩니다. 
DNS 로그: EC2 인스턴스에 AWS DNS resolver를 사용하는 경우 GuardDuty는 AWS DNS resolver를 통해 요청 및 응답 DNS 로그에 액세스하고 처리할 수 있습니다.
OpenDNS 또는 구글DNS와 같은 퍼블릭 DNS를 사용하는 경우 GuardDuty는 해당 DNS 로그에 액세스하고 처리할 수 없습니다.

3. 부가 기능:
GuardDuty Lambda 보호: 잠재적인 보안 위협으로부터 Lambda 함수를 보호합니다. AWS Lambda 함수가 호출될 때 잠재적인 보안 위협을 식별하는데 도움이 됩니다. 활성화를 시작하면 lambda 네트워크 활동 모니터링을
시작하며, 계정에 대한 모든 Lambda 함수의 VPC Flow Log, VPC 네트워킹을 사용하지 않으며, Lambda 함수가 호출됩니다.GuardDuty가 의심스러운 네트워크 트래픽을 식별하는 경의 Lambda 함수에서 잠재적으로
악의적인 코드 조각이 있는 경우 GuardDuty가 결과를 생성합니다.

GuardDuty 런타임 모니터링:
