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

## 4. 사용자 지정 이벤트 버스 생성(목적지 계정에서 수행)

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
## 5. 이벤트 버스 규칙 생성(목적지 계정에서 수행)

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
  --rule guardduty-from-security \
  --targets Id="LambdaTarget",Arn="{Lambda ARN}"

```
