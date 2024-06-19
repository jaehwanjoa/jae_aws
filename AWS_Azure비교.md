1. Accounts:
- AWS는 특정 Account에 모든 리소스가 연결되는 반면, Azure의 경우 구독이란 명칭이 있고 구독을 소유하는 소유자 계정이 독립적으로 존재하며, 필요에 따라 새로운 소유자에게 할당할 수 있음. Azure Account는 청구 관계를 나타내며 구독은 Azure 리소스에 대한 액세스를 구성하는데 도움이 됨. Account에서 대표적인 역할은 아래 내용을 참고
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/9e93f1a4-5a3f-4a76-a5c2-717b9aabbac8)
- 계정 관리자: 구독 소유자 및 구독에 사용된 리소스에 대한 청구 소유자. 구독 소유권을 양도하며 계정 관리자를 변경하는 것만 가능. 계정당 한명의 계정 관리자만 할당됨
- 서비스 관리자: 구독에서 리소스를 만들고 관리할 수 있는 권한이 있지만, 청구에 대한 책임은 없음. 기본적으로 새 구독은 계정 관리자가 서비스 관리자이며, 계정 관리자는 구독의 기술 및 운영 측면을 관리하기 위해 서비스 관리자에게 별도의 사용자를 할당할 수 있음. 구독당 서비스 관리자를 한명만 할당할 수 있음.
- 공동 관리자: 구독에 할당된 공동 관리자는 여러 명일 수 있음. 서비스 관리자와 동일한 액세스 권한을 갖지만 서비스 관리자를 변경할 수 없음.
  
- AWS에서 Identity and Access Management(IAM) 사용자 및 그룹에 권한을 부여하는 방식과 유사하게 구독 수준 아래 사용자 역할 및 개별 권한을 특정 리소스에 할당할 수 있음. Azure에서 모든 사용자 계정은 MSFT 계정 또는 조직 계정(MSFT Entra ID를 통해 관리되는 계정)과 연결됩니다. 

2. Computing Services:
- 가상 머신 및 서버
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/06b6359c-8b34-442f-be58-136f159d73a9)
- 스토리지
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/08a4d257-fbe7-409b-99ff-43fde8ba9401)
- 데이터베이스
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/74d05c45-525d-4ff5-a9ec-c84423fa577b)
- 지역 및 영역
Azure는 한 영역이 두개 이상의 가용성 영역(Availiability Zones)으로 나뉘며, 가용성 영역은 지리적 지역에 물리적으로 격리된 데이터센터와 일치함. 다음은 제공되는 여러 옵션을 설명
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/2f622242-6894-4cb1-9ead-cb12b42d4ac5)
1) Availiability Set): 디스크 또는 네트워크 전환이 실패한 경우 하드웨어 오류를 보호하려면 가용성 집합에 둘이상 VM이 배포되며, 반드시 VM 신규 배포시에만 추가되므로 변경이 불가하다는 에러사항이 있음(주의!)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/c5956c70-7ef1-4965-ae7f-266f8fa10db9)
둘 이상의 VM 생성 시 99.95% SLA 보장. 월간 가동 중지(대략 21분), 연간 가동 중지 시(대략 4시간 20분)
Fault Domain은 데이터센터내 동일한 전원과 네트워크 스위치를 사용하는 하나의 물리적 RACK을 지칭하며, 하나의 장애 도메인 이슈나 유지보수 작업은 다른 Fault Domain에 영향을 끼치지 않음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/b499c495-2e43-48b4-9172-2e110c9899b2)
예약된 유지관리 및 보안 업데이트는 Update Domain을 통해 순서가 정해집니다. 동시에 두개의 Update Domain에서 업데이트하지 않습니다.
즉, Availiability Zone의 Fault Domain과 Update Domain에 가상머신을 분산 배포시키면, 유지관리 및 보안 업데이트로부터 동시에 업데이트 하지 않는한 가용성을 보장받게 됩니다. 
 


