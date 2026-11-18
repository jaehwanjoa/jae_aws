# AWS Athena 테이블 관련 가이드 

Athena 파티션 프로젝션 기능을 사용하여 쿼리 런타임을 줄이고 파티션 관리를 자동화할 수 있습니다. 새 데이터가 추가되면 파티션 프로젝션은 자동으로 새 파티션을 추가합니다. 
따라서 ALTER TABLE ADD PARTITION을 사용해 파티션을 수동으로 추가할 필요가 없습니다.

https://docs.aws.amazon.com/ko_kr/athena/latest/ug/create-waf-table-partition-projection.html
---

## 1. 단일WebACL 전용 테이블 생성

CREATE EXTERNAL TABLE `waf_logs_partition_projection`(
  `timestamp` bigint, 
  `formatversion` int, 
  `webaclid` string, 
  `terminatingruleid` string, 
  `terminatingruletype` string, 
  `action` string, 
  `terminatingrulematchdetails` array<struct<conditiontype:string,sensitivitylevel:string,location:string,matcheddata:array<string>>>, 
  `httpsourcename` string, 
  `httpsourceid` string, 
  `rulegrouplist` array<struct<rulegroupid:string,terminatingrule:struct<ruleid:string,action:string,rulematchdetails:array<struct<conditiontype:string,sensitivitylevel:string,location:string,matcheddata:array<string>>>>,nonterminatingmatchingrules:array<struct<ruleid:string,action:string,overriddenaction:string,rulematchdetails:array<struct<conditiontype:string,sensitivitylevel:string,location:string,matcheddata:array<string>>>,challengeresponse:struct<responsecode:string,solvetimestamp:string>,captcharesponse:struct<responsecode:string,solvetimestamp:string>>>,excludedrules:string>>, 
  `ratebasedrulelist` array<struct<ratebasedruleid:string,limitkey:string,maxrateallowed:int>>, 
  `nonterminatingmatchingrules` array<struct<ruleid:string,action:string,rulematchdetails:array<struct<conditiontype:string,sensitivitylevel:string,location:string,matcheddata:array<string>>>,challengeresponse:struct<responsecode:string,solvetimestamp:string>,captcharesponse:struct<responsecode:string,solvetimestamp:string>>>, 
  `requestheadersinserted` array<struct<name:string,value:string>>, 
  `responsecodesent` string, 
  `httprequest` struct<clientip:string,country:string,headers:array<struct<name:string,value:string>>,uri:string,args:string,httpversion:string,httpmethod:string,requestid:string,fragment:string,scheme:string,host:string>,
  `labels` array<struct<name:string>>, 
  `captcharesponse` struct<responsecode:string,solvetimestamp:string,failurereason:string>, 
  `challengeresponse` struct<responsecode:string,solvetimestamp:string,failurereason:string>, 
  `ja3fingerprint` string, 
  `ja4fingerprint` string, 
  `oversizefields` string, 
  `requestbodysize` int, 
  `requestbodysizeinspectedbywaf` int)
  PARTITIONED BY ( 
   `log_time` string)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://amzn-s3-demo-bucket/AWSLogs/AWS_ACCOUNT_NUMBER/WAFLogs/cloudfront/testui/'
TBLPROPERTIES (
 'projection.enabled'='true',
  'projection.log_time.format'='yyyy/MM/dd/HH/mm',
  'projection.log_time.interval'='1',
  'projection.log_time.interval.unit'='minutes',
  'projection.log_time.range'='2025/01/01/00/00,NOW',
  'projection.log_time.type'='date',
  'storage.location.template'='s3://amzn-s3-demo-bucket/AWSLogs/AWS_ACCOUNT_NUMBER/WAFLogs/cloudfront/testui/${log_time}')
  
```bash


```
