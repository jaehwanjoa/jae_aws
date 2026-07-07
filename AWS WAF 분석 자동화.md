# AWS WAF 분석 자동화 가이드

Notebook, Amazon Bedrock을 활용하였습니다. Athena 쿼리 결과(Excel) 파일을 필요로하며, Bedrock 내 Claud AI가 TOP5 형식으로 분석을 수행합니다.

---

## 1. Athena에 WAF 로그 추출
아테나 쿼리는 아래 형식을 유지합니다.

```bash
WITH base AS (
    SELECT
        t.*,
        date_format(
            from_unixtime(t.timestamp / 1000, 'Asia/Seoul'),
            '%Y-%m-%d %H:%i:%s'
        ) AS kst_time,

        element_at(
            multimap_from_entries(
                transform(
                    t.httprequest.headers,
                    x -> (lower(x.name), x.value)
                )
            ),
            'host'
        )[1] AS host_header,

        element_at(
            multimap_from_entries(
                transform(
                    t.httprequest.headers,
                    x -> (lower(x.name), x.value)
                )
            ),
            'user-agent'
        )[1] AS user_agent

    FROM ons_cjl_ue1 t    #테이블 이름 변경해야 합니다.
    WHERE from_unixtime(t.timestamp / 1000)
          BETWEEN TIMESTAMP '2026-06-01 00:00:00' #시작 날짜 및 시간을 지정합니다.
              AND TIMESTAMP '2026-06-30 00:00:00' #종료 날짜 및 시간을 지정합니다.
      AND t.action IN ('ALLOW', 'COUNT')
)

SELECT
    b.kst_time,
    b.webaclid,
    nmr_item.ruleid AS matched_ruleid,
    md.location,
    b.httprequest.clientip,
    b.httprequest.country,
    b.httprequest.httpMethod,
    b.host_header,
    b.user_agent,
    b.httprequest.uri,
    b.httprequest.args,
    md.matcheddata

FROM base b

LEFT JOIN UNNEST(b.rulegrouplist) AS rg(rg_item) ON TRUE
LEFT JOIN UNNEST(rg_item.nonterminatingmatchingrules) AS nmr(nmr_item) ON TRUE
LEFT JOIN UNNEST(nmr_item.rulematchdetails) AS rd(md) ON TRUE
LEFT JOIN UNNEST(b.labels) AS lbl(label_item) ON TRUE

WHERE nmr_item.ruleid IS NOT NULL

ORDER BY b.kst_time ASC;
```
쿼리 결과를 CSV로 다운로드 하고, 파일은 통합 EXCEL로 저장되어야만 합니다(민감도 제외 필수)

## 2. Notebook 실행 및 파일 업로드

Amazon SageMaker AI > Notebooks > Jupyter 열기 > WAF Report 폴더에 파일을 업로드 합니다.<br>
루트(/) 디렉터리 이동 > WAF_Report.ipynb 실행 > 파일 경로 수정 후 실행(Cell 선택 후 Shift + Enter)

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
result = "WAF Report/6월waf_alb.xlsx" #업로드한 파일 경로로 수정합니다.
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

```

## 4. 출력 파일 다운로드

루트(/) 디렉토리 > WAF Report 폴더에 'WAF_분석 결과'라는 이름으로 생성됩니다. 

## 5. 구성 설정

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

## 참고용. 전체 코드

코드는 Notebook 형식으로 작성되었습니다. 기준이 되는 룰 자료가 필요합니다(waf_로그 분석1.xlsx)

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
