버킷 정책 추가 시 주의 사항
1. 정책에 의한 허용: S3의 액세스 제어 모델은 기본적으로 모든 것을 거부한다. 즉 명시적으로 허용되지 않는 한 모든 액세스는 거부됨
2. 명시적 Deny가 가장 최우선 적용: 명시적으로 Deny가 설정된 경우 Allow 정책이 있어도 해당 요청은 차단됨
![image](https://github.com/user-attachments/assets/966db25f-a153-482d-add8-b343ef9978c8)
3. S3에 대한 접근 차단 테스트
- 특정 사용자 계정에 한해, S3 버킷에 대한 업로드를 허용함
![image](https://github.com/user-attachments/assets/c8466205-f0d3-455d-aab5-458c1e26dadf)
- 테스트 방법: 대상 사용자 Credential을 갖는 액세스키 부여
 ![image](https://github.com/user-attachments/assets/0dab3b78-f021-4bb4-bc7c-aaea5ec19a4a)
![image](https://github.com/user-attachments/assets/c3bcf4c6-a309-46a0-8bb2-f48c30dba31d)

