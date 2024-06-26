AWS EKS는 설치, 운영 및 AWS에서 자체 kubernetes 제어 플레인을 유지 관리합니다. AWS IAM과 통합하여 안전한 인증 기능을 제공합니다. 다음 설명은 EKS에서 감사로그 모니터링 방안을 설명하고 있음.

![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/68d3cb1f-4fa3-48e4-addf-57d00d54d06a)
1. AWS EKS Control Plane Logging: 기본적으로 해당 로그는 CloudWatch로 전송되지 않습니다. 각 로그를 설정해서 개별적으로 클러스터에 대한 로깅을 설정해야하며, 최대 5개의 사용가능한 항목이 있음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/1d4cd2ad-9d84-4e5d-bf07-7877ec6e02aa)
사전 필요사항: CloudWatch > Application Signals > Application Signals 활성화 선택
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/c5b36726-fb6c-4b46-91ab-519741c9ca51)
EKS 클러스터 선택 및 CloudWatch Observablility EKS 에드온 이동 선택 후 에이전트 설치 구성(IAM 권한 필요함)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/38b99aff-2752-42cb-9836-70a0524e95aa)
Container Insights에서 로깅 여부 확인
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/d60206cc-27a0-4ffe-afd1-d04d8fb9b316)

