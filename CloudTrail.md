CloudTrail의 이벤트는 AWS 계정의 활동 기록으로써 IAM 자격 증명 또는 CloudTrail에서 모니터링할 수 있는 서비스에서 수행 작업에 대한 이벤트를 로깅합니다.
CloudTrail 로그 파일은 퍼블릭 API 호출의 정렬된 스택 트레이서가 아니므로, 이벤트가 특정 순서로 표시되지 않습니다. 모두 Json 형태로 사용됨.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/83821812-72ae-409e-a32d-cc0f5170832c)

1. 관리 이벤트:
컨트롤 플레인 작업이라고 부름. 보안 구성(AWS Identity and Access Management API 작업), 디바이스 등록(EC2 API 작업), 데이터 라우팅 규칙 구성, 로깅 설정등이 해당됩니다.
관리 이벤트에는 계정에서 발생하는 비 API 이벤트도 포함됩니다. 예로 AWS Management 콘솔 로그인 이벤트, AWS 서비스 이벤트
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/159e781e-a79b-492d-8220-74d6e51b203a)

2. 데이터 이벤트:
리소스 작업에 대한 정보를 제공합니다. 데이터 평면 작업이라고도 합니다.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/3d3bbaf2-8223-481d-906d-159b674e58e4)

#제어평면 및 데이터평면: 제어 평면 작업은 스토리지 계정에 대한 액세스 관리, 컨테이너 만들기/삭제등을 의미. 데이터평면 작업은 데이터에 대한 읽기 쓰기와 같은 작업 권한을 다룸. 기본적으로 로깅되지 않음
즉 Alice는 컨테이너를 읽기/쓰기/삭제가 가능하지만 데이터평면 작업 불가, Bob은 컨트롤플레인과 데이터 평면 작업 모두를 수행할 수 있음

![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/f014feb5-9f80-4365-8c3e-8d079311a453)

4. 인사이트 이벤트:
AWS에서 비정상적인 API 호출 속도 또는 API 오류 율 활동을 캡처함. 인사이트 이벤트는 추가 요금이 적용되며, 활성화시 별도로 요금이 청구됨. 인사이트는 활용 예는 다음과 같음.
![image](https://github.com/jaehwanjoa/jae_aws/assets/90813478/f533a887-f69d-474d-83e4-af49abeac7e7)
ex)계정은 일반적으로 분당 20개 이하의 S3 API 호출을 기록하지만, 분당 평균 100개의 API 호출을 기록하기 시작함. 정상 활동과 비정상 활동을 비교하기 위함



