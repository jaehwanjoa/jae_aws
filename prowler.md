1. 참고 자료: https://github.com/prowler-cloud/prowler
prowler opensource라고 칭하며, CIS, NIST 800, AWS Well-Architected Framework Security Pillar, AWS Foundational Technical Review(FTR)등 보안 모범 사례 평가 및 모니터링 서비스 제공
2. prowler 시작: AWS 환경에 대한 스캐닝 시작
- pip install prowler
- prowler -v
- aws configure --profile [credential name] #자격증명 프로파일 저장
![image](https://github.com/user-attachments/assets/878cfc48-0a98-4279-b038-7869653795d9)

3. HTML 보고서 생성ex)provider = aws, azure, gcp, kubernetes
![image](https://github.com/user-attachments/assets/098ff4ce-a370-4ba6-a874-ff770fa2e526)
prowler <provider> -M csv json-asff json-ocsf html
prowler <provider> -M csv json-asff -F <custom_report_name>
prowler <provider> -M csv json-asff -o <custom_report_directory>
prowler aws --compliance aws_well_architected_framework_security_pillar_aws --profile jaehwan.myeong
#컴플라이언스 참고
https://docs.prowler.com/projects/prowler-open-source/en/latest/tutorials/compliance/#list-available-compliance-frameworks

5. prowler, security hub 통합
![image](https://github.com/user-attachments/assets/ba8138ef-dbd8-4f95-b96a-40d1e1594a76)
prowler --security-hub --region ap-netheast-2
prowler --security-hub --send-sh-only-fails #Prowler 출력의 모든 결과를 저장하되 FAIL 결과를 AWS Security Hub로 보내는 데만 사용(비용절감)

6. local 저장 파일(html) s3로 복사
aws s3 cp yourfile.txt [s3버킷URI]
ex)aws s3 cp /root/output/prowler-output-747935822721-20240726062925.html s3://202040710-jaehwan-test/prowler/ --profile jaehwan.myeong
![image](https://github.com/user-attachments/assets/20711b1b-2cda-4e32-bb72-9d3904c241a9)

7. csv 다운로드 후 Excel 데이터 > 텍스트/CSV 불러오기
![image](https://github.com/user-attachments/assets/ae6bf030-3bb1-4c2a-9fe1-da49b90de49a)
