1. Conformance Pack 배포
![image](https://github.com/user-attachments/assets/4a9a155e-7b98-4421-8865-84e44864972e)
2. COnformance Pack 출력
![image](https://github.com/user-attachments/assets/3e05aff7-3f56-42ad-9dde-ac76148689d6)
만약 json으로 저장하고자 한다면 다음 명령어로 실행
aws configservice get-conformance-pack-compliance-details --conformance-pack-name AwsWAF-SecurityPillar --output json --next-token  --profile jaehwan.myeong > compliance3.json
3. S3 저장
aws s3 cp /root/compliance3.json s3://202040710-jaehwan-test/prowler/ --profile jaehwan.myeong
4. csv 변환
엑셀로 실행 시 레코드가 깨져서 식별이 어려운 경우가 있다. 다음 파이썬 코드 실행(소스 코드는 'aws_config_conver_csv.py'에서 확인할 것)
![image](https://github.com/user-attachments/assets/41e81175-cab8-4efc-ab9f-4a8adf4a2582)
5. 결과 출력
![image](https://github.com/user-attachments/assets/58e09661-1188-49cd-99b0-00077d65e179)
6. 주의 사항
출력 결과가 많으면 AWS는 Next Token을 요구함. 이게 싫으면 Cloudtrail을 활용하거나 다른 방법을 강구해야함
![image](https://github.com/user-attachments/assets/2fbd00f7-fc21-4254-b3e3-6e9c397000ff)
![image](https://github.com/user-attachments/assets/bed9dcea-7739-4dda-82e8-afec3c0085b3)
다음과 같이 실행하면 다음 페이지 정보를 출력할 수 있다(만약 10개 페이지면 노가다..)
aws configservice get-conformance-pack-compliance-details --conformance-pack-name AwsWAF-SecurityPillar --output json --next-token []  --profile jaehwan.myeong > compliance3.json
![image](https://github.com/user-attachments/assets/9520137c-e483-4a67-be9e-7c22c1e5d28b)



