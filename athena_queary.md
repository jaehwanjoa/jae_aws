1. AWS WAF 관련:
timestamp를 한국 시간으로 변환하고, 이외 로그 필드를 필터링하여 쿼리함. 필요에 따라 where 절을 통해 추가 검색
- select   date_format(from_unixtime((timestamp / 1000) + 9 * 3600), '%Y-%m-%d %H:%i:%s') AS kst_time, httprequest.httpMethod, webaclid, action, terminatingruleid, httprequest.clientip, httprequest.country, httprequest.uri, labels from waf_logs_jae 
![image](https://github.com/user-attachments/assets/c6b87ded-6541-4f73-a54d-c818db1e8093)
