AWS Organizations은 Account를 단일 단위로 관리하도록 통합하기 위해 생성하는 개체이며, Organizations은 관리 Account 하나와 0개 이상의 멤버 계정을 가짐.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/08d81822-14ba-4eae-b194-253a3002d5cf)
- Root: Organizations의 모든 계정에 대한 상위 컨테이너로 정책을 루트에 적용하면, 해당 정책은 조직의 모든 OU(조직단위)와 Account에 적용됨. AWS Organizations은 사용자가 조직을 만들때 루트를 자동 생성함
