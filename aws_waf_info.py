import boto3
import pandas as pd

# AWS 세션 생성(프로파일 및 지역 변경 필요)
session = boto3.session.Session(profile_name='jaehwan_API') 
client = session.client('wafv2', region_name='ap-northeast-2')

# Web ACL 목록 가져오기
def get_web_acl(name, scope, acl_id):
    try:
        response = client.get_web_acl(
            Name=name,
            Scope=scope,
            Id=acl_id
        )
        return response.get('WebACL', {})
    except client.exceptions.WAFNonexistentItemException:
        print("Web ACL does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while getting Web ACL: {e}")
        return None

# 로깅 정보 가져오기
def get_logging_configuration(arn):
    try:
        response = client.get_logging_configuration(
            ResourceArn=arn
        )
        return response.get('LoggingConfiguration', {})
    except client.exceptions.WAFNonexistentItemException:
        print("Logging configuration does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while getting logging configuration: {e}")
        return None

# IP Set 리스트 출력
def list_ip_sets(scope):
    response = client.list_ip_sets(Scope=scope)
    return response.get('IPSets', [])

# IP Set 정보 가져오기
def get_ip_set(name, scope, ip_set_id):
    try:
        response = client.get_ip_set(
            Name=name,
            Scope=scope,
            Id=ip_set_id
        )
        return response['IPSet']
    except client.exceptions.WAFNonexistentItemException:
        print(f"IP Set with ID '{ip_set_id}' and name '{name}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Regex Pattern Set 목록 가져오기
def list_regex_pattern_sets(scope):
    try:
        response = client.list_regex_pattern_sets(Scope=scope)
        return response.get('RegexPatternSets', [])
    except Exception as e:
        print(f"An error occurred while listing Regex Pattern Sets: {e}")
        return []

# Regex Pattern Set 정보 가져오기
def get_regex_pattern_set(name, scope, regex_pattern_set_id):
    try:
        response = client.get_regex_pattern_set(
            Name=name,
            Scope=scope,
            Id=regex_pattern_set_id
        )
        return response['RegexPatternSet']
    except client.exceptions.WAFNonexistentItemException:
        print(f"Regex Pattern Set with ID '{regex_pattern_set_id}' and name '{name}' does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while getting Regex Pattern Set: {e}")
        return None

# 설정할 값들(!!반드시입력필요!!)
web_acl_name = 'Juice-Shop-WAF' 
web_acl_scope = 'REGIONAL'
web_acl_id = 'ca289688-261c-4808-be2a-29ee93707514'

# API 호출
web_acl = get_web_acl(web_acl_name, web_acl_scope, web_acl_id)

if web_acl:
    logging_config = get_logging_configuration(web_acl['ARN'])
    ip_sets = list_ip_sets(web_acl_scope)
    ip_set_infos = [get_ip_set(ip_set['Name'], web_acl_scope, ip_set['Id']) for ip_set in ip_sets]

    regex_pattern_sets = list_regex_pattern_sets(web_acl_scope)
    regex_pattern_infos = [get_regex_pattern_set(regex_pattern['Name'], web_acl_scope, regex_pattern['Id']) for regex_pattern in regex_pattern_sets]

# 선택적으로 CSV로 저장
def save_to_csv(logging_config, web_acl, ip_set_infos):
    # 로깅 정보 데이터프레임으로 변환
    logging_df = pd.DataFrame([logging_config]) if logging_config else pd.DataFrame()
    
    # Web ACL 정보 데이터프레임으로 변환
    rules_data = [
        {
            'RuleName': rule.get('Name'),
            'Priority': rule.get('Priority'),
            'Action': rule.get('Action')
        }
        for rule in web_acl.get('Rules', [])
    ]
    web_acl_data = {
        'Name': web_acl.get('Name'),
        'ARN': web_acl.get('ARN'),
        'Capacity': web_acl.get('Capacity'),
        'Rules': [rules_data],
        'DefaultAction': web_acl.get('DefaultAction')
    }
    web_acl_df = pd.DataFrame([web_acl_data])
    
    # IPSet 정보 데이터프레임으로 변환
    ip_info_df = pd.DataFrame(ip_set_infos)

    # regex_pattern Set 정보 데이터프레임으로 변환
    regex_pattern_infos_df = pd.DataFrame(regex_pattern_infos)

    # xlsx 파일로 저장(파일 저장 위치 수정 필요)
    with pd.ExcelWriter('C:/Users/User/Downloads/aws_waf_info.xlsx') as writer:
        if not logging_df.empty:
            logging_df.to_excel(writer, sheet_name='LoggingConfiguration', index=False)
        if not web_acl_df.empty:
            web_acl_df.to_excel(writer, sheet_name='WebACL', index=False)
        if not ip_info_df.empty:
            ip_info_df.to_excel(writer, sheet_name='IPSet', index=False)
        if not regex_pattern_infos_df.empty:
            regex_pattern_infos_df.to_excel(writer, sheet_name='regex_pattern Sets', index=False)    

    print('Excel file saved with WAF information.')

# CSV 저장 호출
save_to_csv(logging_config, web_acl, ip_set_infos)
