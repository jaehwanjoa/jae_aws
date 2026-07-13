# AI 분석 에이전트 개발 가이드(Cortex)

Notebook, Lambda, Amazon Bedrock을 활용하였습니다. 사용자 입력데이터를 AI가 추론하는 일반적인 AI 챗봇이 아닙니다.<br>
수집된 보안 이벤트를 기반으로 RAG(Retrieval-Augmented Generation)를 적용하여, 사용자 환경에 특화된 분석 결과를 제공합니다.<br>
즉, Cortex Cloud 전용 AI 분석 에이전트라고 이해할 수 있습니다. 

---
## 아키텍처 구조
1. 보안 이벤트 S3 적재: Cortex Cloud -> S3(rag-bucket-jaehwan/CSPM/raw)<br>
2. RAG 프로세싱: Cortex 보안 로그를 AI 검색 가능한 벡터 DB 형태로 변환하는 단계(rag-lambda-jaehwan)<br>
- Preprocessing 수행: serverity/asset_name/asset_account 등 주요 필드를 추출<br>
- Chunk 생성: AI 검색 효율을 위해 이벤트를 검색 단위로 분리<br>
- Embedding/Vector 생성: SageMaker Processing Job 수행(Titan Embedding과 Vector 동작)<br>
- Vector Store 생성:  rag-lambda-jaehwan -> S3(rag-bucket-jaehwan/CSPM/vector)<br>
4. 사용자 인터페이스(UI)<br>
- S3 정적 웹호스팅: index.html 정적 웹사이트 기반 UI 제공. 사용자는 자연어로 질문을 입력합니다. ex)어제 탐지된 이슈 알려줘<br>
- 질의 요청: 사용자 -> API Gateway -> rag-chat-api(lambda)<br>
- 질의 검색: rag-query lambda(질의 내용을 검색하고, 질문을 Tiran Embedding으로 변환)<br>
- Context 생성: 검색된 Finding과 Metadata를 기반으로 Context 생성<br>
- AI 분석: EventBridge -> rag-answer(이벤트 자동 트리거, 사전정의 입력 프롬프트 반영 ex)Serverity 운선 순위, 권고 사항 생성 등<br>
- 결과 저장: S3 -> rag-bucket-jaehwan/CSPM/answer<br>
- 결과 조회: UI는 API Gateway를 통해 결과를 조회하고 사용자 질의 결과를 출력합니다.
```bash
┌────────────────────────────┐
│   Cortex Cloud Findings    │
└─────────────┬──────────────┘
              │ Raw Event
              ▼
s3://rag-bucket-jaehwan/CSPM/raw/
│
├── raw/
│   └── finding.json
│
├── chunk/
│   └── chunk.json
│
├── vector/
│   ├── cspm.index
│   └── metadata.json
│
├── context/
│   └── context.json
│
└── answer/
    └── cspm-rag-query-xxxx.json
              ▲
              │ Vector Store 저장
┌─────────────┴──────────────┐
│ Lambda(Preprocessing)      │
├────────────────────────────┤
│ - Raw Event Parsing        │
│ - 주요 필드 추출            │
│ - Chunk 생성               │
└─────────────▲──────────────┘
              │ S3 Event
┌─────────────┴──────────────┐
│      S3 Raw Event          │
└────────────────────────────┘
────────────────────────────────────────────
┌────────────────────────────┐
│ SageMaker Processing Job   │
├────────────────────────────┤
│ - Titan Embedding          │
│ - Vector 생성             │
│ - FAISS Index 생성        │
│ - Metadata 생성           │
└─────────────┬──────────────┘
              │
              ▼
s3://rag-bucket-jaehwan/CSPM/vector/
│
├── cspm.index
└── metadata.json
────────────────────────────────────────────
사용자 질의 프로세스
┌────────────────────────────┐
│ S3 Static Website Hosting  │
│ (index.html)               │
└─────────────┬──────────────┘
              │ 사용자 질문
              ▼
┌────────────────────────────┐
│ API Gateway                │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ rag-chat-api Lambda        │
├────────────────────────────┤
│ - 질문 수신                │
│ - Query 등록              │
│ - Processing Job 생성      │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ rag-query Lambda           │
├────────────────────────────┤
│ - Query Embedding          │
│ - FAISS Similarity Search  │
│ - Metadata 매핑           │
│ - Context 생성            │
└─────────────┬──────────────┘
              │
              ▼

s3://rag-bucket-jaehwan/CSPM/context/
│
└── context.json
              │
              ▼
┌────────────────────────────┐
│ EventBridge                │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ rag-answer Lambda          │
├────────────────────────────┤
│ - Context 조회            │
│ - Claude Prompt 생성      │
│ - Claude 분석             │
│ - Answer 생성             │
└─────────────┬──────────────┘
              ▼
s3://rag-bucket-jaehwan/CSPM/answer/
│
└── cspm-rag-query-xxxx.json
              ▲
              │ Polling
              │
┌─────────────┴──────────────┐
│ rag-answer-api Lambda      │
├────────────────────────────┤
│ - Answer 조회             │
│ - Processing 상태 확인     │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ API Gateway                │
└─────────────┬──────────────┘
              ▼
┌────────────────────────────┐
│ S3 정적 웹사이트           │
│ Cortex Copilot UI          │
└────────────────────────────┘
```

## 1. 보안 이벤트 알림 설정 및 RAG 프로세싱 적용
보안 이벤트 적재는 솔루션별로 상이하므로, 되었다는 가정하에 해당 내용은 생략합니다.<br>
S3 버킷 > 속성 선택 > 이벤트 알림 추가 (해당 작업 시 대상 Lambda에 리소스 기반 정책이 자동 추가됨)

```bash
접두사: CSPM_RAG/raw/
접미사: .json
이벤트 유형: 모든 객체 생성 이벤트
대상: Lambda 함수 선택 ex)rag-lambda-jaehwan
```
람다 역할은 자동으로 생성합니다. 다만 필요 권한은 아래와 같습니다.<br>

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::rag-bucket-jaehwan/CSPM_RAG/raw/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::rag-bucket-jaehwan/CSPM_RAG/chunk/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:CreateProcessingJob"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "<자동 생성 Lambda Role ARN 입력>"
            ]
        }
    ]
}
```
전체 람다 코드입니다.<br>
s3

```bash
import json
import uuid
import boto3

s3 = boto3.client("s3")
sm = boto3.client("sagemaker")

RAG_BUCKET = "rag-bucket-jaehwan"

ROLE_ARN = (
    "arn:aws:iam::747935822721:role/service-role/AmazonSageMakerServiceCatalogProductsUseRole"
)


def build_embedding_text(chunk):

    if chunk.get("event_type") == "CVE":

        return f"""
Event Type:
CVE

CVE:
{chunk.get('cve_id', '')}

Title:
{chunk.get('alert_name', '')}

Description:
{chunk.get('description', '')}

Severity:
{chunk.get('severity', '')}

CVSS:
{chunk.get('cvss_score', '')}

Package:
{chunk.get('package_purl', '')}

Package Version:
{chunk.get('package_version', '')}

File Path:
{chunk.get('file_path', '')}

Has Fix:
{chunk.get('has_fix', '')}

Fix Versions:
{chunk.get('fix_versions', '')}

Asset:
{chunk.get('asset_name', '')}

Region:
{chunk.get('asset_region', '')}

Account:
{chunk.get('asset_account', '')}

Status:
{chunk.get('status', '')}
""".strip()

    return f"""
Event Type:
{chunk.get('event_type', 'UNKNOWN')}

Owner:
{chunk.get('issue_owner', '')}

Control:
{chunk.get('alert_name', '')}

Description:
{chunk.get('description', '')}

Severity:
{chunk.get('severity', '')}

Asset:
{chunk.get('asset_name', '')}

Region:
{chunk.get('asset_region', '')}

Account:
{chunk.get('asset_account', '')}

Status:
{chunk.get('status', '')}
""".strip()

def validate_chunk(chunk):

    required_fields = [

        "event_type",
        "alert_name",
        "description",
        "severity",
        "asset_name"

    ]

    for field in required_fields:

        value = chunk.get(field)

        if value is None:
            return False

        if isinstance(value, str):

            if not value.strip():
                return False

    return True

def lambda_handler(event, context):

    bucket = (
        event["Records"][0]
        ["s3"]["bucket"]["name"]
    )

    key = (
        event["Records"][0]
        ["s3"]["object"]["key"]
    )

    print(f"Bucket : {bucket}")
    print(f"Key : {key}")

    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    content = (
        response["Body"]
        .read()
        .decode("utf-8")
    )

    source_data = json.loads(content)

    if isinstance(source_data, dict):
        source_data = [source_data]

    chunk_list = []

    for item in source_data:

        body = item.get("body", item)

        try:

            original_alert = body.get(
                "original_alert_json",
                {}
            )

            nested_alert = original_alert.get(
                "original_alert_json",
                {}
            )

            issues = nested_alert.get(
                "issues",
                []
            )

            if not issues:

                print(
                    f"NO ISSUES : "
                    f"{body.get('alert_name')}"
                )

                continue

            issue = issues[0]

            normalized = issue.get(
                "xdm.issue.normalized_fields",
                {}
            )

            asset = {}

            assets = body.get(
                "assets",
                []
            )

            if assets:
                asset = assets[0]

            cve_id = normalized.get(
                "xdm.vulnerability.cve_id"
            )

            issue_owner = issue.get(
                "xdm.issue.owner"
            )

            if cve_id:

                event_type = "CVE"

            elif issue_owner == "CSPM":

                event_type = "COMPLIANCE"

            else:

                event_type = "UNKNOWN"

            chunk = {

                "chunk_id":
                    str(uuid.uuid4()),

                "event_type":
                    event_type,

                "issue_owner":
                    issue_owner,

                "cve_id":
                    cve_id,

                "alert_name":
                    body.get(
                        "alert_name"
                    ),

                "description":
                    issue.get(
                        "xdm.issue.description"
                    ),

                "severity":
                    issue.get(
                        "xdm.issue.platform_severity"
                    ),

                "cvss_score":
                    normalized.get(
                        "xdm.vulnerability.cvss_score"
                    ),

                "package_purl":
                    normalized.get(
                        "xdm.software_package.purl"
                    ),

                "package_version":
                    normalized.get(
                        "xdm.software_package.version"
                    ),

                "file_path":
                    normalized.get(
                        "xdm.file.path"
                    ),

                "has_fix":
                    normalized.get(
                        "xdm.vulnerability.has_a_fix"
                    ),

                "fix_versions":
                    normalized.get(
                        "xdm.vulnerability.fix_versions"
                    ),

                "remediation":
                    issue.get(
                        "xdm.issue.remediation"
                    ),

                "observation_time":
                    nested_alert.get(
                        "xdm.issue.observation_time"
                    ),

                "status":
                    (
                        body.get(
                            "extra_issue_data",
                            {}
                        )
                        .get(
                            "platform_status.progress"
                        )
                    ),

                "asset_name":
                    asset.get(
                        "asset_name"
                    ),

                "asset_region":
                    asset.get(
                        "asset_region"
                    ),

                "asset_account":
                    asset.get(
                        "asset_account"
                    ),

                "asset_tags":
                    asset.get(
                        "asset_tags"
                    )
            }

            if not validate_chunk(chunk):

                print(
                    f"INVALID CHUNK : "
                    f"{chunk.get('alert_name')}"
                )

                continue

            chunk["embedding_text"] = (
                build_embedding_text(
                    chunk
                )
            )

            chunk_list.append(
                chunk
            )

            print(
                f"CHUNK CREATED : "
                f"{chunk['event_type']} | "
                f"{chunk['severity']} | "
                f"{chunk['asset_name']}"
            ) 

        except Exception as e:

            print(
                f"Parse Error : {str(e)}"
            )

    output_key = (
        "CSPM_RAG/chunk/"
        f"{uuid.uuid4()}.json"
    )

    s3.put_object(
        Bucket=RAG_BUCKET,
        Key=output_key,
        Body=json.dumps(
            chunk_list,
            ensure_ascii=False,
            indent=2
        ),
        ContentType="application/json"
    )

    cve_count = len([
        c for c in chunk_list
        if c.get("event_type") == "CVE"
    ])

    compliance_count = len([
        c for c in chunk_list
        if c.get("event_type") == "COMPLIANCE"
    ])

    unknown_count = len([
        c for c in chunk_list
        if c.get("event_type") == "UNKNOWN"
    ])

    print(
        f"""
    ===================
    Chunk Summary
    ===================
    TOTAL      : {len(chunk_list)}
    CVE        : {cve_count}
    COMPLIANCE : {compliance_count}
    UNKNOWN    : {unknown_count}
    ===================
    """
    )

    print(
        f"Chunk Created : "
        f"s3://{RAG_BUCKET}/{output_key}"
    )

    job_name = (
        "cspm-rag-vector-"
        f"{uuid.uuid4().hex[:8]}"
    )

    try:

        response = sm.create_processing_job(

            ProcessingJobName=job_name,

            RoleArn=ROLE_ARN,

            AppSpecification={

                "ImageUri": (
                    "366743142698.dkr.ecr.ap-northeast-2.amazonaws.com/"
                    "sagemaker-scikit-learn:1.4-2-cpu-py3"
                ),

                "ContainerEntrypoint": [

                    "python3",

                    "/opt/ml/processing/code/build_vector.py"
                ]
            },

            ProcessingResources={

                "ClusterConfig": {

                    "InstanceCount": 1,

                    "InstanceType":
                    "ml.t3.medium",

                    "VolumeSizeInGB": 30
                }
            },

            ProcessingInputs=[

                {
                    "InputName": "chunk",

                    "S3Input": {

                        "S3Uri":
                        f"s3://{RAG_BUCKET}/{output_key}",

                        "LocalPath":
                        "/opt/ml/processing/input",

                        "S3DataType":
                        "S3Prefix",

                        "S3InputMode":
                        "File"
                    }
                },

                {
                    "InputName": "code",

                    "S3Input": {

                        "S3Uri":
                        f"s3://{RAG_BUCKET}/CSPM_RAG/code/",

                        "LocalPath":
                        "/opt/ml/processing/code",

                        "S3DataType":
                        "S3Prefix",

                        "S3InputMode":
                        "File"
                    }
                }
            ],

            ProcessingOutputConfig={

                "Outputs": [

                    {

                        "OutputName":
                        "vector",

                        "S3Output": {

                            "S3Uri":
                            f"s3://{RAG_BUCKET}/CSPM_RAG/vector/",

                            "LocalPath":
                            "/opt/ml/processing/output",

                            "S3UploadMode":
                            "EndOfJob"
                        }
                    }
                ]
            }
        )

        print(
            f"Processing Job Started : "
            f"{job_name}"
        )

        print(
            response["ProcessingJobArn"]
        )

    except Exception as e:

        print(
            f"Processing Job Error : {str(e)}"
        )

        raise

    return {
        "statusCode": 200,
        "chunkCount": len(chunk_list),
        "processingJob": job_name
    }

```

## 2. 분석파일 업로드

<S3 버킷>/WAF_Report/upload/ 폴더에 WAF쿼리결과.xlsx 파일을 업로드 합니다. 파일은 영문으로 작성합니다.

## 3. 출력파일 다운로드

<S3 버킷>/WAF_Report/results/ 폴더에 WAF_분석_결과_YYYYMMDD_HHMMSS.xlsx 파일을 다운로드 합니다.


## 참고. 디버깅용

SageMaker Processing Job에 대한 모니터링은 아래 경로에서 확인 가능합니다.<br>
SageMaker AI > Data preparation: Processing Jobs > 처리작업에서 작업 이름을 선택합니다.<br> 
모니터링 > 로그 보기 > CloudWatch 로그 스트림을 선택합니다. 완료 예시는 아래와 같습니다.
```bash
2026-07-08T18:02:23.098+09:00
Downloading openpyxl-3.1.5-py2.py3-none-any.whl (250 kB)
2026-07-08T18:02:23.099+09:00
Downloading et_xmlfile-2.0.0-py3-none-any.whl (18 kB)
2026-07-08T18:02:23.099+09:00
Installing collected packages: et-xmlfile, openpyxl
2026-07-08T18:02:23.099+09:00
Successfully installed et-xmlfile-2.0.0 openpyxl-3.1.5
2026-07-08T18:02:23.099+09:00
Input File : /opt/ml/processing/input/07_waf_alb.xlsx
2026-07-08T18:02:23.099+09:00
Rule File : /opt/ml/processing/resource/waf_rule.xlsx
2026-07-08T18:02:23.099+09:00
Output File: /opt/ml/processing/output/WAF_분석_결과_20260708_090221.xlsx
2026-07-08T18:02:52.108+09:00
[AI START] CommonRuleSet
2026-07-08T18:02:52.108+09:00
[AI START] AdminProtectionRuleSet
2026-07-08T18:02:52.108+09:00
[AI START] SQLiRuleSet
2026-07-08T18:02:52.108+09:00
[AI START] AmazonIpReputationList
2026-07-08T18:02:52.108+09:00
[AI START] AnonymousIpList
2026-07-08T18:03:07.115+09:00
[AI COMPLETE] AdminProtectionRuleSet
2026-07-08T18:03:11.115+09:00
[AI COMPLETE] SQLiRuleSet
2026-07-08T18:03:11.116+09:00
[AI COMPLETE] AmazonIpReputationList
2026-07-08T18:03:18.117+09:00
[AI COMPLETE] CommonRuleSet
2026-07-08T18:03:25.118+09:00
[AI COMPLETE] AnonymousIpList
2026-07-08T18:03:45.122+09:00
완성
```


## 참고. 구성 설정

Notebook Role에는 다음 권한을 필수적으로 필요로합니다.

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel",
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:Converse",
                "bedrock:ConverseStream"
            ],
            "Resource": "*"
        },
        {
            "Sid": "MarketplaceSubscription",
            "Effect": "Allow",
            "Action": [
                "aws-marketplace:ViewSubscriptions",
                "aws-marketplace:Subscribe"
            ],
            "Resource": "*"
        }
    ]
}
```
Lambda 코드는 다음과 같습니다.

```bash
import boto3
import uuid

sm = boto3.client("sagemaker")

ROLE_ARN = "<SageMaker AI Role ARN>"

def lambda_handler(event, context):

    for record in event["Records"]:

        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        input_path = f"s3://{bucket}/{key}"

        print(f"Input File : {input_path}")

        job_name = f"waf-analysis-{uuid.uuid4().hex[:8]}"

        response = sm.create_processing_job(

            ProcessingJobName=job_name,

            RoleArn=ROLE_ARN,

            AppSpecification={
                "ImageUri": (
                    "366743142698.dkr.ecr.ap-northeast-2.amazonaws.com/"
                    "sagemaker-scikit-learn:1.4-2-cpu-py3"
                ),
                "ContainerEntrypoint": [
                    "python3",
                    "/opt/ml/processing/code/process_waf.py"
                ]
            },

            ProcessingResources={
                "ClusterConfig": {
                    "InstanceCount": 1,
                    "InstanceType": "ml.t3.medium",
                    "VolumeSizeInGB": 30
                }
            },

            ProcessingInputs=[

                # 업로드된 WAF 보고서
                {
                    "InputName": "input",
                    "S3Input": {
                        "S3Uri": input_path,
                        "LocalPath": "/opt/ml/processing/input",
                        "S3DataType": "S3Prefix",
                        "S3InputMode": "File"
                    }
                },

                # 분석 코드
                {
                    "InputName": "code",
                    "S3Input": {
                        "S3Uri": (
                            "<S3 버킷 경로>/"
                            "WAF_Report/code/"
                        ),
                        "LocalPath": "/opt/ml/processing/code",
                        "S3DataType": "S3Prefix",
                        "S3InputMode": "File"
                    }
                },

                # 정책 파일
                {
                    "InputName": "resource",
                    "S3Input": {
                        "S3Uri": (
                            "<S3 버킷 경로>/"
                            "WAF_Report/resource/"
                        ),
                        "LocalPath": "/opt/ml/processing/resource",
                        "S3DataType": "S3Prefix",
                        "S3InputMode": "File"
                    }
                }
            ],

            ProcessingOutputConfig={
                "Outputs": [
                    {
                        "OutputName": "result",
                        "S3Output": {
                            "S3Uri": (
                                "<S3 버킷 경로>/"
                                "WAF_Report/results/"
                            ),
                            "LocalPath": "/opt/ml/processing/output",
                            "S3UploadMode": "EndOfJob"
                        }
                    }
                ]
            }
        )

        print(f"Processing Job Started : {job_name}")
        print(response["ProcessingJobArn"])

    return {
        "statusCode": 200
    }
```
Lambda Role에는 다음 권한을 필수적으로 필요로합니다.

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:CreateProcessingJob"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "<Sage Maker AI Role ARN>"
            ]
        }
    ]
}
```
Lambda 에는 다음과 같은 리소스 권한도 필적입니다. 참고로 해당 과정은 S3 버킷 이벤트 알림 설정에서도 작업 가능합니다.

```bash
{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {
      "Sid": "event_permissions_from_bucket_WAF-S3-Trigger",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "<Lambda ARN>",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "747935822721"
        },
        "ArnLike": {
          "AWS:SourceArn": "<S3 버킷 ARN>"
        }
      }
    }
  ]
}
```

## 참고. process_waf.py

해당 파일을 /WAF_Report/code 폴더에 업로드하면 Lambda가 해당 파일을 실행합니다.

```bash
import boto3
import json
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

# ===============================
# ✅ 경로
# ===============================
result = "WAF Report/6월waf_alb.xlsx"
rule   = "WAF Report/waf 로그 분석1.xlsx"
output = "WAF Report/WAF_분석_결과.xlsx"

# ===============================
# ✅ Boderline 설정
# ===============================
THIN = Side(style="thin")

BOX_BORDER = Border(
    left=THIN,
    right=THIN,
    top=THIN,
    bottom=THIN
)

# ===============================
# ✅ Bedrock Client
# ===============================

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="ap-northeast-2"
)

MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# ===============================
# ✅ Bedrock Function
# ===============================

def get_bedrock_analysis(ruleset, top5_df, actual_count):

    top_text = top5_df[
        [
            "matched_ruleid",
            "location",
            "httpMethod",
            "host_header",
            "uri",
            "args",
            "matcheddata",
            "clientip",
            "TotalCount",
            "EventCount"
        ]
    ].to_json(
        orient="records",
        force_ascii=False,
        indent=2
    )

    prompt = f"""
당신은 AWS WAF 보안 분석 전문가이다.

아래는 AWS WAF RuleSet [{ruleset}]의 matched_ruleid별 총 탐지 건수 기준 상위 5개 탐지 항목이다.

{top_text}

다음 기준을 반드시 준수하여 분석하라.

1. RuleSet 이름에 BODY가 포함된 경우에는 HTTP Body Payload를 확인할 수 없으므로 공격으로 단정하지 말고 오탐 가능성을 중심으로 분석한다.

2. RuleSet 이름에 QUERYARGUMENTS, HEADER 또는 URIPATH가 포함된 경우에는 host_header, uri, args, matcheddata, clientip를 근거로 공격 가능성을 분석한다.

3. 입력 데이터에 없는 내용은 절대 추측하지 않는다.
- 국가
- 클라우드 사업자(CSP)
- 공격 그룹
- 공격자의 의도
- 서버 취약 여부

4. 분석 대상 선정 기준
 - Count 기준 TOP5 이벤트를 분석하지 않는다.
 - matched_ruleid별 총 탐지 건수를 집계한다.
 - 총 탐지 건수 기준 상위 5개의 matched_ruleid를 분석한다.
 - 동일 matched_ruleid는 1회만 분석한다.

5. 각 이벤트마다 아래 형식으로 작성한다.

[분석 기준]

반드시 의견의 가장 첫 부분에 작성한다.

형식:

본 분석은 이벤트 유형 내 탐지정책별 총 탐지 건수를 집계한 후, 총 탐지 건수 기준 상위 {actual_count}개 Rule을 대상으로 분석을 수행하였습니다.
각 탐지 정책은 해당 정책에서 가장 많이 탐지된 대표 이벤트를 기준으로 분석하였습니다.

■ RULE: matched_ruleid 값
- 분석 대상
  ;출발지IP: clientip / 도메인: host_header / URI: uri / 시도 횟수: EventCount / 총 탐지 건수: TotalCount
  
- 분석 결과
  ;BODY 정책은 실제 Payload 확인이 불가능하므로 오탐 가능성을 고려하여 분석
  ;QUERYARGUMENTS, HEADER, URIPATH 정책은 host_header, uri, args, matcheddata, httpMethod, location 정보를 종합하여 공격 가능성을 중심으로 분석한다.
  
- 권고 사항
  ;1문장으로 간결하게 표현

6. ■ RULE 상세 분석 작성 규칙

- 시도 횟수는 EventCount를 사용한다.
- 총 탐지 건수는 TotalCount를 사용한다.
- TotalCount와 EventCount를 혼용하지 않는다.

7. 입력으로 제공된 데이터는 정확히 {actual_count}건이다. 반드시 {actual_count}개의 ■ RULE: 블록을 출력한다.

8. 분석 결과가 어떤 탐지 이벤트에 대한 것인지 명확히 식별할 수 있도록 반드시 분석 대상 정보를 기재한다.

9. 입력 데이터에 존재하지 않는 정보는 절대 생성하거나 추측하지 않는다.

10. 출력 예시는 아래와 같다.

■ CROSSSITESCRIPTING_BODY
 - 분석 대상
    ;출발지IP: 58.97.120.185 / 도메인: loiswmsappglobal.cjlogistics.com / URI: /minkSvc / 시도 횟수: 1245 / 총 탐지 건수: 10254
    
 - 분석 결과
    ;AWS WAF 로그 특성상 실제 Body Payload 확인이 불가능하여 정상 서비스 요청에 의한 오탐 가능성을 배제할 수 없다.

 - 권고 사항
    ;서비스 담당자를 통한 정상 요청 여부 확인 후 예외 적용 검토가 필요하다.

11. 분석 내용을 출력 시  ■ RULE: 블록 앞단에는 아무런 서도도 입력하지 않는다. ex)이해했습니다. 분석을 시작하겠습니다.

12. 출력 검증 규칙
 - 출려된 ■ RULE 블록 개수는 반드시 {actual_count}개여야 한다. 
 - {actual_count}개보다 적게 출력한 경우 응답을 종료하지 말고 나머지 RULE을 계속 작성한다.
 - 입력 데이터에 없는 RULE을 새로 생성하지 않는다.

13. 첫 번째 이벤트로부터 반드시 아래 형식으로 시작한다.
    ■ RULE: RULE명
    첫 번째 RULE에서도 ■ 기호를 생략하지 않는다.

14. 각 이벤트는 독립적으로 분석한다.
- "첫 번째 이벤트와 유사", "두 번째 이벤트와 동일", "앞선 이벤트", "이전 이벤트" 등의 표현을 사용하지 않는다.
- 현재 이벤트에 제공된
  host_header,
  uri,
  args,
  matcheddata,
  clientip,
  httpMethod,
  EventCount,
  TotalCount
  정보만 근거로 분석한다.
- 동일한 Source IP 또는 URI가 다른 이벤트에 존재하더라도 이를 언급하지 않는다.
- 다른 이벤트와의 연관성 또는 공격 시나리오를 추론하지 않는다.
- 각 ■ RULE 블록은 독립적인 분석 보고서로 작성한다.

"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    return result["content"][0]["text"]

# ===============================
# ✅ Claud 병렬 처리
# ===============================
def run_ai_analysis(ruleset, sub):

    top5_rules = (
        sub.groupby("matched_ruleid")
           .agg(
               TotalCount=("Count", "sum")
           )
           .reset_index()
           .sort_values(
               "TotalCount",
               ascending=False
           )
           .head(5)
    )

    ai_rows = []

    for _, rule_row in top5_rules.iterrows():
    
        rule_name = rule_row["matched_ruleid"]
    
        sample = (
            sub[
                sub["matched_ruleid"] == rule_name
            ]
            .sort_values(
                "Count",
                ascending=False
            )
            .iloc[0]
        )
    
        ai_rows.append(
            {
                "matched_ruleid": sample["matched_ruleid"],
                "location": sample["location"],
                "host_header": sample["host_header"],
                "httpMethod": sample["httpMethod"],
                "uri": sample["uri"],
                "args": sample["args"],
                "matcheddata": sample["matcheddata"],
                "clientip": sample["clientip"],
        
                # Rule 전체 탐지 수
                "TotalCount": int(
                    rule_row["TotalCount"]
                ),
        
                # 대표 이벤트 탐지 수
                "EventCount": int(
                    sample["Count"]
                )
            }
        )
    ai_df = pd.DataFrame(ai_rows)

    try:
        
        actual_count = len(ai_df)

        opinion = get_bedrock_analysis(
            ruleset,
            ai_df,
            actual_count
        )

    except Exception as e:

        opinion = (
            f"Bedrock 분석 실패\n\n"
            f"{str(e)}"
        )

    return ruleset, opinion
    
# ===============================
# ✅ 스타일
# ===============================
HEADER_FILL = PatternFill("solid", fgColor="D9D9D9")
DESC_FILL   = PatternFill("solid", fgColor="FFF2CC")

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left", vertical="top", wrap_text=True)

# ✅ ✅ 폰트 (🔥 전체 8.5로 통일)
BASE_FONT = Font(name="맑은 고딕", size=8.5)
BOLD_FONT = Font(name="맑은 고딕", size=8.5, bold=True)

# ===============================
# ✅ 테두리
# ===============================
def border_box(ws, r1, c1, r2, c2):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(r, c).border = BOX_BORDER
            
# ===============================
# ✅ merge helper
# ===============================
def merge(ws, r1, c1, r2, c2):
    ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)

# ===============================
# ✅ 로그 로드
# ===============================
df = pd.read_excel(result).fillna("")

for c in df.columns:
    if df[c].dtype == "object":
        df[c] = df[c].astype(str).str.strip()

df["matched_ruleid"] = df["matched_ruleid"].str.upper()

# ===============================
# ✅ 정책 파싱
# ===============================
rule_df = pd.read_excel(rule, sheet_name="정책 설명", header=None).fillna("")

ruleset_rules = {}
rule_to_ruleset = {}
current_ruleset = None

rule_desc_map = {}

for ruleset, rules in ruleset_rules.items():

    for rule_name, desc in rules:

        rule_desc_map[
            rule_name.upper()
        ] = desc

for i in range(len(rule_df)):

    col_a = str(rule_df.iloc[i, 0]).strip()
    col_b = str(rule_df.iloc[i, 1]).strip()

    desc = " ".join(
        str(rule_df.iloc[i, j]).strip()
        for j in range(2, len(rule_df.columns))
        if str(rule_df.iloc[i, j]).strip()
    )

    if col_a and "_" not in col_a:
        current_ruleset = col_a
        ruleset_rules.setdefault(current_ruleset, [])

    if current_ruleset is None:
        continue

    if col_b:
        rule_name = col_b.upper()
        ruleset_rules[current_ruleset].append((rule_name, desc))
        rule_to_ruleset[rule_name] = current_ruleset

# ===============================
# ✅ 집계
# ===============================
group_cols = [
    "matched_ruleid","clientip","uri",
    "httpMethod","host_header","country"
]
group_cols = [c for c in group_cols if c in df.columns]
agg_df = (
    df.groupby(group_cols)
    .agg(
        Count=("matched_ruleid","size"),
        location=("location","first"),
        args=("args","first"),
        matcheddata=("matcheddata","first"),
        user_agent=("user_agent","first"),
        webaclid=("webaclid","first")
    )
    .reset_index()
)
agg_df["RuleSet"] = agg_df["matched_ruleid"].map(rule_to_ruleset)

ruleset_data = {
    ruleset: grp.copy()
    for ruleset, grp in agg_df.groupby("RuleSet")
}

# ===============================
# ✅ AI 분석 병렬 처리
# ===============================
ai_results = {}

with ThreadPoolExecutor(max_workers=5) as executor:

    futures = []

    for ruleset, rules in ruleset_rules.items():

        sub = ruleset_data.get(ruleset)

        if sub is None or sub.empty:
            continue

        future = executor.submit(
            run_ai_analysis,
            ruleset,
            sub
        )

        print(f"[AI START] {ruleset}")

        futures.append(future)

    for future in as_completed(futures):

        try:

            ruleset, opinion = future.result()

            ai_results[ruleset] = opinion

            print(f"[AI COMPLETE] {ruleset}")

        except Exception as e:

            print(f"[AI ERROR] {str(e)}")

# ===============================
# ✅ 엑셀 생성
# ===============================
wb = openpyxl.Workbook()
wb.remove(wb.active)

for ruleset, rules in ruleset_rules.items():

    sub = agg_df[agg_df["RuleSet"] == ruleset]
    if sub.empty:
        continue

    ws = wb.create_sheet(ruleset[:30])

    # =========================
    # ✅ AI 분석 (TOP 5)
    # =========================
    ai_opinion = ai_results.get(
        ruleset,
        "분석 결과 없음"
    )

    # -------------------------
    # ✅ 헤더
    # -------------------------
    headers = [
        "Count","탐지 장비","탐지 정책","탐지 위치",
        "출발지IP","국가코드","HTTP Method","host header",
        "User Agent","URI","파라미터","탐지 문자열"
    ]

    for i, h in enumerate(headers, 1):
        cell = ws.cell(1, i, h)
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
        cell.font = BOLD_FONT

    border_box(ws, 1, 1, 1, len(headers))

    # -------------------------
    # ✅ 이벤트 데이터
    # -------------------------
    row_idx = 2
    
    for r in sub.itertuples(index=False):
    
        arn = r.webaclid

        # ✅ UUID 제거 (최종 안정)
        arn = r.webaclid
        webacl_value = arn.rsplit("/", 1)[0] if "/" in arn else arn

        vals = [
            int(r.Count),
            webacl_value,
            r.matched_ruleid,
            r.location,
            r.clientip,
            r.country,
            r.httpMethod,
            r.host_header,
            r.user_agent,
            r.uri,
            r.args,
            r.matcheddata
        ]
 
        for c_idx, v in enumerate(vals, 1):
            cell = ws.cell(row_idx, c_idx, v)
            cell.alignment = CENTER
            cell.font = BASE_FONT
     
        row_idx += 1

    border_box(ws, 2, 1, row_idx - 1, len(headers))

    # =========================
    # ✅ 패턴 상세
    # =========================
    start_col = 15

    merge(ws, 1, start_col, 1, start_col+1)

    t = ws.cell(1, start_col, "패턴 상세 정보")
    t.fill = DESC_FILL
    t.alignment = CENTER
    t.font = BOLD_FONT

    ws.cell(2, start_col, "Rule").fill = DESC_FILL
    ws.cell(2, start_col+1, "설명").fill = DESC_FILL

    ws.cell(2, start_col).alignment = CENTER
    ws.cell(2, start_col+1).alignment = CENTER

    ws.cell(2, start_col).font = BOLD_FONT
    ws.cell(2, start_col+1).font = BOLD_FONT

    border_box(ws, 2, start_col, 2, start_col+1)

    row = 3

    for rule_name, desc in rules:

        c1 = ws.cell(row, start_col, rule_name)
        c2 = ws.cell(row, start_col+1, desc)

        c1.fill = DESC_FILL
        c2.fill = DESC_FILL

        c1.alignment = CENTER
        c2.alignment = LEFT

        c1.font = BASE_FONT
        c2.font = BASE_FONT

        border_box(ws, row, start_col, row, start_col+1)

        row += 1

    # =========================
    # ✅ 의견
    # =========================
    opinion_start = row + 1
    
    # AI 결과 줄 수 기준 영역 자동 계산
    line_count = len(str(ai_opinion).split("\n"))
    opinion_rows = min(
        max(line_count + 3, 15),
        40
    )
    
    merge(
        ws,
        opinion_start + 1,
        start_col,
        opinion_start + opinion_rows,
        start_col + 1
    )
    
    t = ws.cell(opinion_start, start_col, "의견")
    t.fill = DESC_FILL
    t.alignment = CENTER
    t.font = BOLD_FONT
    
    c = ws.cell(opinion_start + 1, start_col)
    c.value = ai_opinion
    c.fill = DESC_FILL
    c.font = BASE_FONT
    
    c.alignment = Alignment(
        horizontal="left",
        vertical="center",
        wrap_text=True
    )
    
    for r in range(
        opinion_start + 1,
        opinion_start + opinion_rows + 1
    ):
        ws.row_dimensions[r].height = 20
    
    border_box(
        ws,
        opinion_start,
        start_col,
        opinion_start + opinion_rows,
        start_col + 1
    )
    
    # -------------------------
    # ✅ 열 너비
    # -------------------------
    widths = [10, 60, 30, 15, 18, 12, 15, 35, 50, 50, 30, 35]

    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64+i)].width = w

    ws.column_dimensions['O'].width = 40
    ws.column_dimensions['P'].width = 80

# ===============================
# ✅ 저장
# ===============================
wb.save(output)

print("완성")
```
