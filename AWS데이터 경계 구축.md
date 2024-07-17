기존 온프렘 데이터 센터 환경에서 신뢰할 수 있는 네트워크와 강력한 인증은 보안의 기초입니다. 높은 수준의 경계를 구축하여 신뢰할 수 없는 엔터티가 들어오고 데이터가 외부로 나가는 것을 방지합니다. AWS 경계를 정의하는 원은 일반적으로 AWS OU로 표시됩니다. 즉, Organizations에서 관리된다는 것을 의미합니다. AWS 자격 증명, 리소스 및 네트워크등 AWS 조직은 이러한 모든 항목을 단일 항목으로 그룹화합니다. 경계는 의도하거나 발생할 것으로 예상되는 것을 정의합니다. 당신이 허용하고자하는 ID, 리소스, 네트워크 간의 액세스 패턴을 참고하고, 3가지 요소를 사용하여 신뢰할 수 있는 경우에만 액세스를 허용하고, 하나라도 거짓이면 액세스는 거부되어야합니다.
![image](https://github.com/user-attachments/assets/81b1ff7d-e9ed-40c5-9752-c61d8a5a2f2f)

1. AWS 경계의 목표: 다음과 같은 경우에만 액세스가 허용되도록 구성
- 신뢰할 수 있는 ID만 허용
- 신뢰할 수 있는 리소스만
- 필요한 네트워크만
  
2. 경계 개요:
- AWS 서비스: AWS Organizations SCP를 적용하여 사용 가능한 최대 권한을 제어합니다. 즉, SCP에서 리소스 또는 소스 네트워크에 대한 액세스 범위를 제한합니다. 다만, AWS 서비스 보안 주체(역할)에는 적용되지 않는 점을 유의해야합니다.
- 리소스 기반 정책: AWS 리소스에 적용할 수 있으며 인라인 정책으로 구성됩니다(https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/reference_aws-services-that-work-with-iam.html)
- VPC 엔드포인트 정책: 특정 유형의 리소스 기반 정책으로, 해당 VPC 엔드포인트를 통해 리소스에 액세스할 때 액세스를 제어하는 엔드포인트입니다. VPC 네트워크 트래픽은 AWS DNS를 사용하는 경우 자동으로 VPC 엔드포인트로 라우팅됩니다. 온프렘 네트워크의 경우 VPC 엔드포인트를 통해 AWS 트래픽을 라우팅할 수 있습니다.

3. 경계 구현:
- 신뢰할 수 있는 ID만 허용: 리소스 기반 정책 또는 VPC 엔드포인트 정책을 사용하여 액세스가 허용되는 보안 주체를 제한합니다.
![image](https://github.com/user-attachments/assets/55c6cef1-8b18-400f-9e02-f51a50c63367)
- 신뢰할 수 있는 리소스만 허용: 내 네트워크 및 리소스에만 액세스해야합니다. SCP 및 VPC 엔드포인트 정책을 활용할 수 있습니다.
![image](https://github.com/user-attachments/assets/7b72001c-631e-466a-b370-86baadab150f)
- 필요한 네트워크만 허용: SCP 내 IAM 정책 조건 또는 VPC 식별자를 조건으로 다음과 같은 IP 주소를 사용하여 예상 네트워크를 정의할 수 있습니다. 
![image](https://github.com/user-attachments/assets/d019b71b-25bb-4412-b44b-9b9eac18259c)
