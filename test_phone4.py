import subprocess
import requests
import time

# 내부 LTE IP 확인
def get_lte_ip_via_adb():
    try:
        result = subprocess.check_output("adb shell ip addr", shell=True).decode('utf-8')
        for line in result.splitlines():
            if "inet " in line and "inet6" not in line and "rmnet" in line:
                ip = line.split()[1].split('/')[0]
                interface = line.split()[-1]
                return f"내부 IPv4: {ip} (인터페이스: {interface})"
        return "LTE IPv4 주소를 찾을 수 없음"
    except subprocess.CalledProcessError:
        return "ADB 명령어 실행 실패"

# 공인 IP 확인 (USB 테더링)
def get_public_ip_from_computer():
    try:
        response = requests.get("http://api.ipify.org")
        return response.text.strip()
    except Exception as e:
        return f"공인 IP 확인 실패: {str(e)}"

# 비행기 모드 토글 (루팅된 상태)
def toggle_airplane_mode(state):
    if state == "on":
        subprocess.run("adb shell su -c 'settings put global airplane_mode_on 1'", shell=True)
        subprocess.run("adb shell su -c 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'", shell=True)
    elif state == "off":
        subprocess.run("adb shell su -c 'settings put global airplane_mode_on 0'", shell=True)
        subprocess.run("adb shell su -c 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'", shell=True)

# 메인 실행
print("시작 전 IP 확인")
initial_internal = get_lte_ip_via_adb()
initial_public = get_public_ip_from_computer()
print(initial_internal)
print(f"공인 IP 주소: {initial_public}")

public_ips = [initial_public]  # 공인 IP 리스트 (초기값 포함)
max_attempts = 10  # 최대 재시도 횟수
max_tries = 100
sleep_term = 5

for i in range(max_tries):
    attempt = 0
    while attempt < max_attempts:
        print(f"\n[{i+1}/{max_tries}] 시도 {attempt+1}: 비행기 모드 켜기")
        toggle_airplane_mode("on")
        time.sleep(sleep_term)  # 10초 대기
        
        print(f"[{i+1}/{max_tries}] 비행기 모드 끄기")
        toggle_airplane_mode("off")
        time.sleep(sleep_term)  # 네트워크 연결 대기

        internal_ip = get_lte_ip_via_adb()
        public_ip = get_public_ip_from_computer()
        
        # 직전 IP와 다르면 추가하고 다음으로
        if public_ip != public_ips[-1]:
            public_ips.append(public_ip)
            print(f"시도 {i+1} 후 IP 확인:")
            print(internal_ip)
            print(f"공인 IP 주소: {public_ip}")
            break
        else:
            print(f"[{i+1}/{max_tries}] 공인 IP 변경 실패 ({public_ip}), ({internal_ip})재시도 중...")
            attempt += 1
    
    if attempt == max_attempts:
        print(f"[{i+1}/{max_tries}] {max_attempts}번 시도 후 변경 실패, 다음으로 진행")
        public_ips.append(public_ip)
        break

# 결과 분석
print("\n공인 IP 변화 확인")
for idx, ip in enumerate(public_ips):
    print(f"시도 {idx}: 공인 IP 주소: {ip}")
unique_ips = len(set(public_ips))
if unique_ips == max_tries + 1:  # 초기 + 5번 모두 다르면 6
    print(f"{max_tries}번 모두 공인 IP가 변경되었습니다!")
else:
    print(f"{unique_ips}번만 변경되었습니다.")
