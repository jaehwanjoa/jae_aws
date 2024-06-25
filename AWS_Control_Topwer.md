![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/c88a9b73-b065-4144-a6f3-81e819b39b8d)
AWS Control Tower는 안전한 멀티 계정 AWS 환경을 설정하고 관리할 수 있는 가장 쉬운 방법을 제공함. 모범 사례를 기반으로 랜딩존을 설정하고 패키지된 리스트를 설정해서 보안, 규정 준수 및 운영에 대한 거버넌스 규칙을 구현

1. AWS Control Tower 활성화
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

2. 주요 특징
- 
