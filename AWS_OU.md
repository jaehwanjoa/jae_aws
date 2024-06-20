AWS Organizations은 Account를 단일 단위로 관리하도록 통합하기 위해 생성하는 개체이며, Organizations은 하나의 관리 Account 가짐.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/08d81822-14ba-4eae-b194-253a3002d5cf)
- Root: Organizations의 모든 계정에 대한 상위 컨테이너로 정책을 루트에 적용하면, 해당 정책은 조직의 모든 OU(조직단위)와 Account에 적용됨. AWS Organizations은 사용자가 조직을 만들때 루트를 자동 생성함
- Organization Unit(OU): 루트에 있는 Account를 위한 컨테이너로 각 OU는 상위 OU 하나를 가질 수 있고, 현재 각 Account는 한 OU의 멤버만 될 수 있음
- Account: Organization의 Account는 AWS 리소스를 포함하는 표준 AWS Account로 이러한 리소스에 액세스할 수 있는 자격증명을 말함
- Service Control Policy(SCP): Account에서 User와 Role이 사용할 수 있는 서비스와 작업을 지정하는 정책을 말함. 일반적으로 권한을 부여하지 않는다는 점을 제외하면 IAM Policy와 유사함. 대신 SCP는 Organization, OU 또는 Account에 대한 최대 권한을 지정하며, SCP를 Organization Root 또는 OU에 연결하면 SCP가 Account의 멤버 개체애 대한 권한을 제한할 수 있음
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/cc59d247-1069-47c3-a349-5ffac8293f8b)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/e43721f3-1912-4059-9abf-f16c78e55e1c)
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/973b9775-4917-40c3-b11f-f4df8a2b103c)
