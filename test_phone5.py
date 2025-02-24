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

# 비행기 모드 토글 (루팅 필요)
def toggle_airplane_mode(state):
    if state == "on":
        subprocess.run("adb shell su -c 'settings put global airplane_mode_on 1'", shell=True)
        subprocess.run("adb shell su -c 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'", shell=True)
    elif state == "off":
        subprocess.run("adb shell su -c 'settings put global airplane_mode_on 0'", shell=True)
        subprocess.run("adb shell su -c 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'", shell=True)

# 라디오 리셋 (루팅 필요)
def reset_radio():
    # 모뎀 끄기
    subprocess.run("adb shell su -c 'service call phone 7'", shell=True)  # 모뎀 리셋 (기기마다 다를 수 있음)
    time.sleep(5)
    # 모뎀 켜기
    subprocess.run("adb shell su -c 'svc data enable'", shell=True)

# 메인 실행
print("시작 전 IP 확인")
initial_internal = get_lte_ip_via_adb()
initial_public = get_public_ip_from_computer()
print(initial_internal)
print(f"공인 IP 주소: {initial_public}")

public_ips = [initial_public]
internal_ips = [initial_internal.split()[1]]  # 내부 IP만 추출
max_attempts = 10

for i in range(5):
    attempt = 0
    while attempt < max_attempts:
        print(f"\n[{i+1}/5] 시도 {attempt+1}: 비행기 모드 켜기 및 라디오 리셋")
        toggle_airplane_mode("on")
        reset_radio()
        time.sleep(60)  # 1분 대기
        
        print(f"[{i+1}/5] 비행기 모드 끄기")
        toggle_airplane_mode("off")
        time.sleep(30)  # 네트워크 연결 대기

        internal_ip = get_lte_ip_via_adb()
        public_ip = get_public_ip_from_computer()
        internal_ip_value = internal_ip.split()[1]  # "내부 IPv4: xxx"에서 xxx만
        
        # 내부 IP와 공인 IP 둘 다 체크
        if internal_ip_value != internal_ips[-1] or public_ip != public_ips[-1]:
            internal_ips.append(internal_ip_value)
            public_ips.append(public_ip)
            print(f"시도 {i+1} 후 IP 확인:")
            print(internal_ip)
            print(f"공인 IP 주소: {public_ip}")
            break
        else:
            print(f"[{i+1}/5] IP 변경 실패 - 내부: {internal_ip_value}, 공인: {public_ip}, 재시도 중...")
            attempt += 1
    
    if attempt == max_attempts:
        print(f"[{i+1}/5] {max_attempts}번 시도 후 변경 실패, 다음으로 진행")
        internal_ips.append(internal_ip_value)
        public_ips.append(public_ip)
        break

# 결과 분석
print("\n내부 IP 변화 확인")
for idx, ip in enumerate(internal_ips):
    print(f"시도 {idx}: 내부 IP: {ip}")

print("\n공인 IP 변화 확인")
for idx, ip in enumerate(public_ips):
    print(f"시도 {idx}: 공인 IP 주소: {ip}")

unique_internal = len(set(internal_ips))
unique_public = len(set(public_ips))
print(f"\n내부 IP: {unique_internal}번 변경")
print(f"공인 IP: {unique_public}번 변경")
if unique_internal == 6 and unique_public == 6:
    print("내부와 공인 IP 모두 5번 변경 성공!")
else:
    print("목표 달성 실패...")