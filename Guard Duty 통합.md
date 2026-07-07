# Guard Duty 이벤트 통합 가이드

Cross Account 구조에서 Event Bridge를 통해 계정 간 Guard Duty 이벤트 통합 방안을 기술하였습니다.

---

## 1. IAM Role 생성(원본 계정에서 수행)

AWS CloudShell에서 아래와 같이 Trust Policy를 생성합니다.

```bash
cat <<EOF > trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
```
IAM Role 생성하고 Trust Policy를 적용합니다.
```bash
aws iam create-role \
  --role-name EventBridgeToSecurityRole \
  --assume-role-policy-document file://trust-policy.json
```
IAM Role에 Permission Policy 생성
```bash
cat <<EOF > permission-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "events:PutEvents",
            "Resource": [
                "arn:aws:events:ap-northeast-2:747935822721:event-bus/ons-central-bus"
            ]
        }
    ]
}
EOF
```
IAM Role에 Permission Policy 연결

```bash
aws iam put-role-policy \
  --role-name EventBridgeToSecurityRole \
  --policy-name AllowPutEvents \
  --policy-document file://permission-policy.json
```

## 2. 이벤트 버스 규칙 생성(원본 계정에서 수행)

AWS CloudShell에서 아래와 같이 이벤트 버스 규칙을 생성합니다.

```bash
aws events put-rule \
  --name guardduty-to-secbus \
  --event-pattern '{
    "source": ["aws.guardduty"],
    "detail-type": ["GuardDuty Finding"]
  }'
```
이벤트 버스 규칙 타겟으로 목적지 계정 지정 
```bash
aws events put-targets \
  --rule guardduty-to-secbus \
  --targets "Id"="ToSecBus", "Arn"="arn:aws:events:ap-northeast-2:747935822721:event-bus/ons-central-bus", "RoleArn"="arn:aws:iam::<SOURCE_ACCOUNT_ID>:role/EventBridgeToSecurityRole"

```

## 3. 사용자 지정 이벤트 버스 생성(목적지 계정에서 수행)

AWS CloudShell에서 아래와 같이 사용자 지정 이벤트 버스를 생성합니다.

```bash
aws events create-event-bus --name ons-central-bus
```
생성한 이벤트 버스에 리소스 기반 정책을 설정합니다. (MSSP 고객이 늘어날때마다 SOURCE ACCOUNT를 추가해야합니다)
```bash
aws events put-permission \
  --event-bus-name ons-central-bus \
  --statement-id AllowSecurityAccount \
  --action events:PutEvents \
  --principal <SOURCE_ACCOUNT_ID>

```
## 4. 이벤트 버스 규칙 생성(목적지 계정에서 수행)

AWS CloudShell에서 아래와 같이 이벤트 버스 규칙을 생성합니다.

```bash
aws events put-rule \
  --name guardduty-from-security \
  --event-bus-name ons-central-bus \
  --event-pattern '{
    "source": ["aws.guardduty"],
    "detail-type": ["GuardDuty Finding"]
  }'
```
이벤트 버스 규칙 타겟으로 람다 지정 
```bash
aws events put-targets \
  --event-bus-name ons-central-bus \
  --rule guardduty-from-security \
  --targets Id="LambdaTarget",Arn="arn:aws:lambda:ap-northeast-2:747935822721:function:CJI-GuardDuty-Alarm"

```
## 5. Guard Dudy Lambda 구성(목적지 계정에서 수행)

python 형식으로 생성해야 합니다. 역할은 자동 생성합니다. 이벤트 트리거는 이벤트 버스 규칙이기 때문에, 리소스 기반 정책으로 권한을 부여해야 합니다.

```bash
aws lambda add-permission \
  --region ap-northeast-2 \
  --function-name CJL-GuardDuty-Alarm \
  --statement-id cjl-guardduty \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:ap-northeast-2:747935822721:rule/ons-central-bus/guardduty-from-security

```
전체 코드입니다. TEAMS_WEBHOOK_URL은 Lambda 환경 변수 형식으로 워크플로 URL이 입력되어 있습니다.
```bash
import json
import os
import urllib.request


def post_to_teams_workflow(workflow_url, payload):

    req = urllib.request.Request(
        workflow_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"Status: {resp.status}")
        print(resp.read().decode())


def build_guardduty_console_url(
    region,
    detector_id,
    finding_id
):

    return (
        f"https://{region}.console.aws.amazon.com/guardduty/home"
        f"?region={region}"
        f"#/findings"
        f"?detectorId={detector_id}"
        f"&search=id%3D{finding_id}"
        f"&fId={finding_id}"
    )


def lambda_handler(event, context):

    print("===== EVENTBRIDGE EVENT =====")
    print(json.dumps(event, indent=2))

    detail = event.get("detail", {})
    service = detail.get("service", {})

    severity = detail.get("severity", 0)

    # High(7.0) 이상만 전송
    if severity < 7:
        print(f"Skip finding. Severity={severity}")
        return {
            "statusCode": 200,
            "body": f"Skipped severity {severity}"
        }

    workflow_url = os.environ["TEAMS_WEBHOOK_URL"]

    account = event.get("account")
    region = event.get("region")

    finding_id = detail.get("id")
    finding_type = detail.get("type")
    title = detail.get("title")
    description = detail.get("description")

    detector_id = service.get("detectorId", "")
    feature_name = service.get("featureName", "")

    console_url = build_guardduty_console_url(
        region=region,
        detector_id=detector_id,
        finding_id=finding_id
    )

    recommended = (
        "https://docs.aws.amazon.com/ko_kr/guardduty/latest/ug/"
        "guardduty_finding-types-active.html"
    )

    payload = {
        "account": account,
        "region": region,
        "finding_id": finding_id,
        "finding_type": finding_type,
        "title": title,
        "description": description,
        "severity": severity,
        "detector_id": detector_id,
        "feature_name": feature_name,
        "console_url": console_url,
        "recommended": recommended
    }

    print("===== PAYLOAD =====")
    print(json.dumps(payload, indent=2))

    post_to_teams_workflow(
        workflow_url,
        payload
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Event forwarded to Teams Workflow"
            }
        )
    }

```

## 6. Teams 워크플로 구성

Teams 웹후크 요청이 수신된 경우로 트리거를 구성합니다. JSON 구문 분석은 아래와 같이 작성합니다.

```bash
{
    "type": "object",
    "properties": {
        "account": {
            "type": "string"
        },
        "region": {
            "type": "string"
        },
        "finding_id": {
            "type": "string"
        },
        "finding_type": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "severity": {
            "type": "number"
        },
        "detector_id": {
            "type": "string"
        },
        "feature_name": {
            "type": "string"
        },
        "recommended": {
            "type": "string"
        },
        "console_url": {
            "type": "string"
        }
    }
}

```

메시지 게시는 적용형 카드로 작성합니다. 이전에 관련 이벤트만 식별되도록 별도 채널을 생성하고 지정합니다.<br>
아래는 적응형 카드 코드입니다.

```bash
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "🚨 GuardDuty Alert",
      "weight": "Bolder",
      "size": "Large",
      "color": "Attention"
    },
    {
      "type": "TextBlock",
      "text": "@{body('JSON_구문_분석')?['title']}",
      "weight": "Bolder",
      "size": "Medium",
      "wrap": true
    },
    {
      "type": "TextBlock",
      "text": "@{body('JSON_구문_분석')?['description']}",
      "wrap": true
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Account",
          "value": "@{body('JSON_구문_분석')?['account']}"
        },
        {
          "title": "Region",
          "value": "@{body('JSON_구문_분석')?['region']}"
        },
        {
          "title": "Severity",
          "value": "@{string(body('JSON_구문_분석')?['severity'])}"
        },
        {
          "title": "Finding Type",
          "value": "@{body('JSON_구문_분석')?['finding_type']}"
        },
        {
          "title": "Finding ID",
          "value": "@{body('JSON_구문_분석')?['finding_id']}"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "📖 Recommended Guide",
      "weight": "Bolder",
      "spacing": "Medium"
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "🔗 Open GuardDuty Finding",
      "url": "@{body('JSON_구문_분석')?['console_url']}"
    },
    {
      "type": "Action.OpenUrl",
      "title": "📖 Recommended Guide",
      "url": "@{body('JSON_구문_분석')?['recommended']}"
    }
  ]
}

```
