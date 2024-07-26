![image](https://github.com/user-attachments/assets/c9ed4636-a465-4459-b259-18c27fcc3014)
1. 로그 스트리밍을 위한 기본 계정의 Amazon CloudWatch Log가 대상입니다.
2. (선택사항)AWS CloudTrail, VPC Flow Log 및 EC2 웹서버에 대한 샘플 CloudWatch Logs
3. 로그 이벤트를 인덱싱하기 위한 Amazon Kinesis Data Streams
4. AWS Lambda를 사용하여 각 로그 이벤트를 변환
5. Kinesis Data Firehose를 사용하여 문서를 인덱싱
6. 저렴한 로그 레코드 스토리지를 위한 S3 버킷 사용.
7. 로그 인덱싱 및 데이터 시각화를 위한 Amazon OpenSearch Service 활용
8. Kibana 대시보드에 대한 퍼블릭 액세스를 방지하기 위한 Amazon ES 도메인용 VPC
9. Kibana 대시보드에 액세스하기 위한 인증 및 권한 부여를 위한 Amazon Cognito 적용
