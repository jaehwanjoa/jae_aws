IAM은 자격증명(사용자, 그룹 및 역할)에서 AWS 관리형 정책을 사용할 수 있으며, 해당 정책은 모든 IAM 자격 증명에 연결할 수 있음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/99b019cf-c970-4f8e-b204-05919f100058)

1. AdministratorAccess: AWS 모든 서비스 및 리소스에 액세스 권한을 가지며 위임할 수 있음
2. Billing: 결제 직무로써 결제 정보와 누적 사용 비용을 확인하고 승인해야하는 사용자에게 부여할 수 있음. 청구/비용/지불방법/예산 및 보고서를 관리함.
3. DatabaseAdministrator: 데이터베이스 관리자직무로 DB를 만들고 구성하고 유지관리함. 기본적으로 DB 서비스에 액세스가 포함(DynamoDB, RDS등)됨
4. DataScientist: EMR 클러스터에서 쿼리 생성, 관리 및 실행하고 데이터 분석을 수행함. Data Pipeline, EC2, Kinesis, ML 및 SageMaker 액세스가 포함됨
5. NetworkAdministrator: 네트워크 관리자 직무로 AWS 네트워크 리소스 설정 및 유지관리를 수행함. EC2, auto scaling, Route 53등의 서비스에 액세스가 포함됨
6. PowerUserAccess: 개발자 직무로 애플리케이션 개발을 수행함. NotAction 요소를 사용하여 Identity and Access Management를 제외한 모든 리소스에 대한 작업을 허용함
7. ReadOnlyAccess: 나열하고 가져오고 설명하고 해당 속성을 볼 수 있지만 create/delete와 같은 권한은 포함하지 않음. AWS 리소스에 대한 액세스를 요청할때 정책의 권한을 검사하여 허용 여부를 결정할 수 있음. ViewOnlyAccess와 차이점은 기본 메타데이터 포함 상세 정보까지 확인할 수 있 
8. SecurityAudit: 로그 및 이벤트에 액세스하여 계정이 보안 요구사항을 준수하는지 모니터링하며 위반 또는 잠재적인 악의적활동을 감사합니다. 
9. SupportUser: AWS Support에 연락하여 지원 서비스 케이스를 확인하고 기존 서비스 케이스의 상태를 확인합니다. 사용자 지원 직무에 해당
10. SystemAdministrator: 개발 작업에 대한 리소스를 설정하고 유지관리합니다. AWS CloudTrail, CloudWatch, Confing, EC2, IAM, Route53등 다양한 서비스에서 리소스를 생성하고 유지관리함
11. ViewOnlyAccess: 서비스 전반에 걸쳐 AWS 리소스에 대한 정보를 나열합니다. 리소스의 상태를 변경하거나 수정할 수 없음.
