첫 액세스에만 루트 사용자 자격 증명 
- AWS Account를 생성할때 AWS 서비스 및 리소스에 대해 완전한 액세스 권한이 있는 단일 로그인ID로 시작하며 ID/PW로 로그인
- 가급적 사용을 자재하도록하고, 루트 사용자 보안 인증 정보를 보호하고, SCP를 통해 루트 사용자에게 부여되는 권한을 제한하도록 정책화 필요.

AWS 로그인 URL 정보
- AWS Account 루트 사용자 로그인, AWS Access Portal, IAM User 로그인(관리 콘솔), 페더레이션 ID 로그인, AWS 빌더 ID 로그인이 있다.

AWS 계정에 대한 Security Best Practices
- 루트 사용자에 대한 MFA를 적용하고, 일상적인 작업에 사용하지 않도록하며, 이메일/연락처 정보를 최신화하여 중요 알림을 받을수 있도록 함
- 사용자를 생성하고 반드시 최소 권한 부여 원칙을 적용하도록 함(Administrator Access 적용 제한)
- ID 권한 추가 또는 제거
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/6bc4585f-1d26-47e6-905d-d9d5311d142c)

IAM > 액세스 관리 > 사용자
- 별도의 Account가 아니며, AWS Account 내 User를 지칭. AWS Management Console 액세스 위해 자체 암호가 필요하며 개별 액세스 권한을 만들수있음
- IAM User에게는 AWS 리소스에 대한 장기 자격 증명이 부여되며 모범사례로, 인간 사용자에게 장기자격 증명 생성을 권고하지 않음(임시 자격 증명 사용)
- 관리 콘솔 로그인(https://console.aws.amazon.com) 루트 사용자 또는 IAM 사용자로 로그인할 수 있음

IAM Identity Center > 인스턴스 관리 > 사용자
- AWS Organizations의 멤버이며 여러 AWS 액세스 포털을 통해 AWS 계정 및 앱에 액세스할 수 있음. 조직의 특정 로그인 URL인 AWS 액세스 포탈을 사용
- IAM Identity Center User에게는 단기 자격 증명이 부여됨
- AWS Access Portal 로그인(https://yourdomain.awsapps.com/start)
- IAM Identity Center 사용자로 로그인시 단기 자격 증명으로 액세스할 수 있는 기간(세션)이 부여. 기본 사용자는 8시간(최소 15분, 최대90일 커스텀가능)

IAM 구분
- IAM Policy: 권한을 부여하는 방법으로 하나 이상의 AWS 리소스에 대한 어떤 작업을 수행할 수 있는지 허용 규칙을 JSON 형태로 작성하며, 이렇게 만들어진 Policy는 IAM User, Goup, Role에 연결된다.
- IAM User: 실제 사용자 단 한명의 의미하며, AWS Account를 처음 만들때 Root Account와 다름을 주의할 것(Root Account에서 IAM 사용자를 만들어 AdministratorAccess를 부여하는 것을 권장)
- IAM Group: 다수의 IAM User를 모아놓은 그룹으로 매번 IAM User에게 Policy를 직접 연결해야하는 번거로움을 그룹에 일괄 부여함으로써 과 관리 포인트를 줄이는 것이 목적이다.
- IAM Role: AWS 서비스를 요청하기 위한 권한 세트를 정의하는 기능으로 일반적으로 Policy에 부여하는 권한과 같을 수 있다. 차이점은 IAM User, Group에 연결되지 않는다는 것이다. 대신 신뢰할 수 있는 IAM User나 앱, AWS 서비스가 역할을 맡는다. 여기서 신뢰할 수 있다는 말은 MFA와 같이 추가 인증을 통해 자격증명이 완료된 상태를 의미함.

IAM Policy vs Role 차이점 정의
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/8f36f5f9-84c1-4028-8099-b1303886770e)
- Policy는 IAM User, Group 단위로 할당되지만, Role은 다수의 User에 부여할 수 있음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/4c002626-3a09-4d31-ac45-c75d04beffa6)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/b3d39f52-48b3-474e-8828-09aa64e20f91)
- Policy는 회수하지않는한 장기 또는 영구적 자격 증명을 부여하지만, Role은 대상 User에게 세션을 위한 임시 보안 자격 증명을 제공함. 즉 유예시간동안만 액세스가 허용되고 이후에는 Role을 반납하고 다시 자격증명 절차요구(자격증명 절차는 ID/PW 및 MFA인증을 지칭)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/5814eacd-4223-4185-be84-dd21f9a76e2d)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/ab729d34-1946-48cd-94aa-3531dd107ef3)
- 정리하면 Policy는 명시적 허용 정책을 통해 AWS 리소스에 대한 거의 영구적으로 액세스 권한을 부여하고 해당 권한을 회수하거나 재부여하는 절차가 필요하며, 자연히 관리 리소스가 증가할 가능성이 높음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/3429dbe5-7312-4015-b835-dc8b75bb093f)
- Role은 비영구적이지만 일정 기간동안 AWS 리소스에 대한 액세스 권한을 부여하기 때문에, 회수 절차가 필요하지 않다는 장점이 있음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/96b449e7-04f9-46bf-9ce0-33770ded9fd8)

AWS Organizations vs AWS IAM Policy 차이점
- Organizations는 AWS Account를 생성하고 그룹화(OU)하고 정책(SCP)을 적용한다면, IAM Policy는 리소스에 대한 액세스를 제어하고 사용자 및 그룹을 만들고 Access/deny를 설정할 수 있다.
- 적용 범위: Organizations은 AWS Account가 대상이지만, IAM Policy는 사용자를 대상으로한다. Organizations에 SCP 적용 시 Account의 모든 사용자도 영향받기에 Organizations의 SCP 정책이 IAM Policy보다 우선시된다.
- 추가 기능: Organizations은 OU별 거버넌스 경계를 만들고 백업/리소스/보안 정책 등을 중앙집중적으로 관리한다면, IAM Policy는 리소스에 대한 액세스 제어가 목적이다. 따라서 조직 단위 Account별 정책(백업, 리소스, 보안등)을 조정하고자한다면 Organizations SCP를, 사용자별 리소스 세부 권한을 조정하고자 한다면 IAM Policy를 사용한다.
