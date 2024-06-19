AWS Organizations은 Account를 단일 단위로 관리하도록 통합하기 위해 생성하는 개체이며, Organizations은 관리 Account 하나와 0개 이상의 멤버 계정을 가짐.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/08d81822-14ba-4eae-b194-253a3002d5cf)
- Root: Organizations의 모든 계정에 대한 상위 컨테이너로 정책을 루트에 적용하면, 해당 정책은 조직의 모든 OU(조직단위)와 Account에 적용됨. AWS Organizations은 사용자가 조직을 만들때 루트를 자동 생성함
- Organization Unit(OU): 루트에 있는 Account를 위한 컨테이너로 각 OU는 상위 OU 하나를 가질 수 있고, 현재 각 Account는 한 OU의 멤버만 될 수 있음
- Account: Organization의 Account는 AWS 리소스를 포함하는 표준 AWS Account로 이러한 리소스에 액세스할 수 있는 자격증명을 말
