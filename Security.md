1. S3에 대한 퍼블릭 액세스 차단하기
 1)버킷 수준에서 퍼블릭 액세스 차단: S3 버킷에 대해서단 퍼블릭 액세스를 차단함(모든 퍼블릭 액세스 차단 활성화는 개별 기능을 모두 활성화한것과 같다)
   ![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/41e4b94f-0d9b-4837-ac35-4a0e0178e758)
 2)계정 수준에서 퍼블릭 액세스 차단: AWS Account에 적용되며 모든 S3 버킷에 대한 퍼블릭 액세스 차단이 활성화된다(중앙집중적 통제가 이점)
   ![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/1f1ea912-d16b-495a-b8b2-ff8252cdf871)

2. Trusted Advisor: AWS Accounts에 대한 권장 사항 및 잠재적인 문제를 확인할 수 있습니다.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/818bffba-7768-4a9e-99cc-36d565128224)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/f6ac6ef1-61ed-499f-b656-8a6646cd9a4a)

3. AWS Inspector
   1)AWS EC2 인스턴스, 컨테이너 및 Lambda 함수와 같은 워크로드를 자동으로 검색하고 소프트웨어 취약성과 의도하지 않은 네트워크 노출이 있는지 스캔합니다. #Azure MDE 취약성 관리 서비스(서버용, 컨테이너용 포함)와 유사함
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/6dd0d573-2dfa-4f34-a992-ce1cfb0fe265)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/f981403a-0ac7-4add-baea-37fe288f44bb)
   2)취약성 결과
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/bbee0777-f250-48f1-9136-5f8be202a526)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/eb47e4aa-58e7-4b74-9948-6b56c83bfade)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/d3465f46-1cda-4944-be18-24d6aec78e20)
   3)정책 추가
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/1e036733-7e42-4150-b9e3-2c03679c68f7)


