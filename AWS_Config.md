1. Conformance Pack 배포
![image](https://github.com/user-attachments/assets/4a9a155e-7b98-4421-8865-84e44864972e)
2. COnformance Pack 출력
![image](https://github.com/user-attachments/assets/3e05aff7-3f56-42ad-9dde-ac76148689d6)
만약 json으로 저장하고자 한다면 다음 명령어로 실행
aws configservice get-conformance-pack-compliance-details --conformance-pack-name AwsWAF-SecurityPillar --output json --next-token  --profile jaehwan.myeong > compliance3.json
3. S3 저장
aws s3 cp /root/compliance3.json s3://202040710-jaehwan-test/prowler/ --profile jaehwan.myeong
4. csv 변환
엑셀로 실행 시 레코드가 깨져서 식별이 어려운 경우가 있다. 다음 파이썬 코드 실행
![image](https://github.com/user-attachments/assets/41e81175-cab8-4efc-ab9f-4a8adf4a2582)
import json
import pandas as pd

# JSON 파일 경로
input_file = 'C:/Users/User/Downloads/compliance_240731.json'
output_file = 'C:/Users/User/Downloads/compliance_240731.csv'

# JSON 파일 읽기
with open(input_file, 'r') as file:
    data = json.load(file)

# Conformance Pack의 규정 준수 세부 사항 추출
compliance_details = data.get('ConformancePackRuleEvaluationResults', [])
records = []
for pack in compliance_details:
        record = {
            'ConfigRuleName': pack.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {}).get('ConfigRuleName'),
            'ComplianceResults': pack.get('ComplianceType', ''),
            'ResourceType': pack.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {}).get('ResourceType'),
            'ResourceId': pack.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {}).get('ResourceId')
        }
        records.append(record)

# 데이터프레임 생성
df = pd.DataFrame(records)

# CSV 파일로 저장
df.to_csv(output_file, index=False)
print(f'CSV file saved as {output_file}')
5. 결과 출력
![image](https://github.com/user-attachments/assets/58e09661-1188-49cd-99b0-00077d65e179)
6. 주의 사항
출력 결과가 많으면 AWS는 Next Token을 요구함. 이게 싫으면 Cloudtrail을 활용하거나 다른 방법을 강구해야함
![image](https://github.com/user-attachments/assets/2fbd00f7-fc21-4254-b3e3-6e9c397000ff)
![image](https://github.com/user-attachments/assets/bed9dcea-7739-4dda-82e8-afec3c0085b3)
다음과 같이 실행하면 다음 페이지 정보를 출력할 수 있다(만약 10개 페이지면 노가다..)
aws configservice get-conformance-pack-compliance-details --conformance-pack-name AwsWAF-SecurityPillar --output json --next-token []  --profile jaehwan.myeong > compliance3.json
![image](https://github.com/user-attachments/assets/9520137c-e483-4a67-be9e-7c22c1e5d28b)



