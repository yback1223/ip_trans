import requests

# 컴퓨터에서 공인 IP 확인 (USB 테더링 시 폰 IP와 동일)
def get_public_ip_from_computer():
    try:
        response = requests.get("http://api.ipify.org")
        return f"공인 IP 주소: {response.text.strip()}"
    except Exception as e:
        return f"공인 IP 확인 실패: {str(e)}"

# 실행
print(get_public_ip_from_computer())