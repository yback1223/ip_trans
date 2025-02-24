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
        return f"공인 IP 주소: {response.text.strip()}"
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
print("시작 전 IP 확인, 씨발...")
print(get_lte_ip_via_adb())
print(get_public_ip_from_computer())

print("\n비행기 모드 켠다, 존나...")
toggle_airplane_mode("on")
print("10초 기다려, 씨발...")
time.sleep(10)

print("\n비행기 모드 끈다, 씨발...")
toggle_airplane_mode("off")
print("네트워크 연결될 때까지 15초 기다려, 존나...")
time.sleep(15)

print("\n비행기 모드 끈 후 IP 확인, 씨발...")
print(get_lte_ip_via_adb())
print(get_public_ip_from_computer())