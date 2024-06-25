AWS Control Tower는 안전한 멀티 계정 AWS 환경을 설정하고 관리할 수 있는 가장 쉬운 방법을 제공함. 모범 사례를 기반으로 랜딩존을 설정하고 패키지된 리스트를 설정해서 보안, 규정 준수 및 운영에 대한 거버넌스 규칙을 구현
모든 영역이 직접 구축된 랜딩존 형태를 Customized 라고 호칭
랜딩존이라는 통합형 구조의 아키텍트는 오직 엔터프라이즈급 기업에만 필요한 것은 아님. 가장 중요한 것은 확장될 수 있는 유연성(Flexibility)과 민첩성(Agility)를 확보하고 안정성(Security)을 보장하는 것이 중요함
EC2 10대든 100든 권한 통제, 로그 관리, 모니터링, 알람 설정 등 아키텍트에 반영된 정책과 방향성이 일관성있게 적용되어야만
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/fa1897b4-a002-427f-8ebe-07d559c818d5)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/bf1c27ba-c6fc-445a-b13f-39b40e95178e)

1. Customized Landing Zone
- Account: Organization, IAM, Identity Center
- Network: VPC, Subnet, Route Table, Endpoint, Trasit GW, Direct Connect, CloudFront, Route53 등
- Security: 3rd Party UTM, WAF or Network Firewall, AWS WAF, Shield
- 랜딩존 기반 서비스: CloudTrail, Config, CloudWatch, SecuirtyHub, GuardDuty, Macie, Athena Detective, System Manager + Contorl Tower(CloudFormation)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/a5055914-d7e3-4d34-b14c-3f3bd3e81d3b)

2. 주요 고려사항:
- Account: OU 구조 결정. 필요성/확장 가능성/미래 전략에 따라 Accouont 생성 및 역할 부여, 중요한 것은 구축 시스템 담당자가 IAM을 통해 권한을 부여받고, Action을 수행하는 실질적 업무와 연계하여 구축하는 것(권한 통제 핵심)
- Network: 인터넷 통신, VPN, 온프렘 서비스, 보안 솔루션등 VPC subnet routing, CIDR 크기, DNS 구조, VPC간 통신 방안 등 구축 시스템의 요구사항, 네트워크 운영 정책을 고려한 네트워크망 구축
- Security: IAM을 통한 User 및 AWS 콘솔, AWS 리소스 접근 방식, EC2 접근 및 Role, Policy를 통한 최소 권한 부여 정책, egress/ingress 통제 방식 등 주요 보안 요구 사항 고려, 더불어 로그 저장 대상 및 보관 방법과 저장기간, 모니터링 알람 방식을 고려해야함
- Operation: 시스템 운영 인력, 운영 대상, 운영 방식, 절차, 프로세스에 맞춰 랜딩존을 운영하고, 용이한 관리가 가능하도록 정책 수립 및 서비스 패치. 중요한 것은 Security를 고려할때 운영을 함께 고려해야

2. AWS Control Tower 활성화
대략 60분 소요
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/2239eba3-0be9-449d-a125-8b28bf2657cf)
- 초기 선택사항: '기존 조직에서 AWS Control Tower 시작' or '새 조직에서 AWS Control Tower 시작'
- OU(조직 단위) 구성: 기본적으로 로그 아카이브 Account 및 보안 감사 Account가 포함된 마스터 역할의 'Securty OU'와, 프로덕션 또는 개발 용의 추가 'Sandbox OU'를 구성함 - 추가 OU는 생성 후에 삭제 가능하지만, 기본 OU는 불가
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/97edb6fc-8d68-4bce-9225-d61c1b0fdfe3)
- 공유 계정 및 암호화 구성: 각 항목을 관리할 Account를 설정함. '로그 아카이브 Account는 Cloud Trail에 대한 로그 관리'를, '감사 Account는 다른 계정의 보안 준수 여부를 관리'하며 'KMS 암호화는 AWS Control Tower 리소스를 KMS로 암호화로 관리'하는데 사용
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/2d601c1b-2c9a-431a-af57-63067ef967a3)
- 생성 확인:
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/93a769d0-d02d-4a09-bdc8-75679bb26393)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/68595c71-3a17-4ee3-b43f-339ede10c2ca)

3. 주요 특징
- 가드레일: 전반적인 AWS 환경에 대한 상위 수준 규칙으로 예방과 탐지 두 가지 종류가 있으며, 예방 SCP를 통해서 하고, 지는 AWS Config 규칙으로 구현함. 두 종료의 가드레일에는 필수/권장/선택의 세가지 범주가 적용됨
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/42007e32-b13e-4f6d-ada2-4c142cab5c58)
1)선제적 제어: AWS CloudFormation 작업을 통해 리소스 생성, 업데이트시 리소스를 확인. AWS를 통해 직접 이루어지는 요청에 영향을 미치지 않을 수 있음(AWS API, AWS SDK 등 코드내 문자열을 감사) - AWS CloudFormation Hook으로 구현
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/6ac28d8b-5ea5-4a27-b239-291e262c3793)
2)예방적(차단) 통제: 작업을 허용하지 않으며 규정을 유지하도록 함. 통제의 상태는 시행 또는 시행되지 않습니다로 표현됨(모든 AWS 지역에서 지원됨) - AWS SCP로 구현됨(Organizations의 일부)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/49d39f12-2f4c-4f85-bb24-efc514d14a28)
3)탐지 제어: Account 내 리소스의 규정 미준수를 감지합니다. 위반하면 대시보드를 통해 경고를 제공합니다. - AWS Config로 구현
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/450ac798-2b05-4ffa-ba36-2d0bf3928b2f)
    
- Account Factory: 새로운 계정을 미리 설정된 구성으로 프로비저닝하는 계정관련 템플릿
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/32f7d69a-afee-4aa9-8b2e-3a7bc6f5dde2)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/d2fc65e9-e07f-4428-9fc3-f2413c15b9e5)
- 대시보드: 랜딩존을 관리할 수 있는 대시보드
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/6701ecc5-cefb-48f0-983b-a690a0b336df)



참고 링크: https://medium.com/@hesjeong/%EC%A7%81%EC%A0%91-%EA%B5%AC%EC%B6%95-%EA%B3%BC-control-tower-%EA%B8%B0%EB%B0%98-%EB%9E%9C%EB%94%A9%EC%A1%B4-%EC%B0%A8%EC%9D%B4-%EB%B6%84%EC%84%9D-e85bd9989fe2
