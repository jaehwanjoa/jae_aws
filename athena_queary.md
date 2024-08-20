1. AWS WAF 관련:
1) timestamp를 한국 시간으로 변환하고, 이외 로그 필드를 필터링하여 쿼리함. 필요에 따라 where 절을 통해 추가 검색
- select   date_format(from_unixtime((timestamp / 1000) + 9 * 3600), '%Y-%m-%d %H:%i:%s') AS kst_time, httprequest.httpMethod, webaclid, action, terminatingruleid, httprequest.clientip, httprequest.country, httprequest.uri, labels from waf_logs_jae 
![image](https://github.com/user-attachments/assets/c6b87ded-6541-4f73-a54d-c818db1e8093)

2) 특정 기간동안 탐지된 IP 기준 Top 10
SELECT httprequest.clientip, count(httprequest.clientip) AS requests FROM waf_logs_jae
where from_unixtime(timestamp / 1000) BETWEEN timestamp '2024-07-01 00:00:00' AND timestamp '2024-07-02 23:59:59' 
--WHERE date >= date_format(current_date - interval '7' day, '%Y/%m/%d')--
GROUP BY httprequest.clientip --동일한 IP 주소를 가진 모든 로그를 그룹화--
ORDER BY requests DESC --requests 요청 수에 따라 내림차순으로 정렬--
LIMIT 10
![image](https://github.com/user-attachments/assets/e3e32c81-48b3-42fb-a1c9-ac260f201744)
3) ㅇ
