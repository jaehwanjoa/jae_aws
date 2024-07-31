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
