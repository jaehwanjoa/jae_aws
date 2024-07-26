1. 참고 자료: https://github.com/prowler-cloud/prowler
prowler opensource라고 칭하며, CIS, NIST 800, AWS Well-Architected Framework Security Pillar, AWS Foundational Technical Review(FTR)등 보안 모범 사례 평가 및 모니터링 서비스 제공
2. prowler 시작: AWS 환경에 대한 스캐닝 시작
- pip install prowler
- prowler -v
- aws configure --profile [credential name] #자격증명 프로파일 저장
![image](https://github.com/user-attachments/assets/878cfc48-0a98-4279-b038-7869653795d9)
- prowler aws(azure/gcp/kubernetes) --profile jaehwan.myeong
![image](https://github.com/user-attachments/assets/098ff4ce-a370-4ba6-a874-ff770fa2e526)

