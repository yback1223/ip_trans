import subprocess
import time
import requests
import ctypes
import sys
import os

# 관리자 권한 확인 및 요청
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        # 현재 스크립트를 관리자 권한으로 재실행
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# ADB 디바이스 연결 확인
def connect_device():
    try:
        subprocess.run(['adb', 'kill-server'], capture_output=True, text=True)
        subprocess.run(['adb', 'start-server'], capture_output=True, text=True)
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        output = result.stdout.strip()
        if 'device' not in output or len(output.splitlines()) <= 1:
            print("디바이스가 연결되어 있지 않습니다. USB 연결과 디버깅 설정을 확인하세요.")
            return None
        print("디바이스 연결 성공:", output)
        return True
    except Exception as e:
        print(f"디바이스 연결 실패: {e}")
        return None

# ADB 명령어 실행 래퍼
def run_adb_shell(command):
    try:
        result = subprocess.run(['adb', 'shell', command], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"ADB 명령 실패: {e}")
        return None

# 컴퓨터 Wi-Fi 끄기 (Windows 기준)
def disable_computer_wifi():
    try:
        subprocess.run('netsh interface set interface "Wi-Fi" admin=enable', shell=True, check=True)
        print("컴퓨터 Wi-Fi 비활성화됨")
        time.sleep(2)
    except Exception as e:
        print(f"Wi-Fi 끄기 실패: {e}")

# 컴퓨터 Wi-Fi 켜기 (테스트 후 복구용)
def enable_computer_wifi():
    try:
        subprocess.run('netsh interface set interface "Wi-Fi" admin=enable', shell=True, check=True)
        print("컴퓨터 Wi-Fi 활성화됨")
    except Exception as e:
        print(f"Wi-Fi 켜기 실패: {e}")

# 네트워크 설정 (Wi-Fi 끄기, 모바일 데이터 켜기)
def setup_network():
    run_adb_shell("svc wifi disable")
    run_adb_shell("svc data enable")
    print("스마트폰 Wi-Fi 꺼짐, 모바일 데이터 켜짐")

# USB 테더링 활성화
def enable_usb_tethering():
    run_adb_shell("service call connectivity 33 i32 1")
    time.sleep(2)
    print("USB 테더링 켜짐")

# 비행기 모드 설정
def toggle_airplane_mode(enable=True):
    state = "1" if enable else "0"
    run_adb_shell(f"settings put global airplane_mode_on {state}")
    run_adb_shell("am broadcast -a android.intent.action.AIRPLANE_MODE")
    time.sleep(1)
    print(f"비행기 모드 {'켜짐' if enable else '꺼짐'}")

# 컴퓨터에서 공인 IP 확인 (테더링 IP로 간주)
def check_computer_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except requests.RequestException:
        return "컴퓨터 공인 IP 확인 불가 (인터넷 연결 확인)"

# 테스트 루프
def test_ip_change():
    print("IP 변경 테스트 시작...")
    try:
        while True:
            toggle_airplane_mode(enable=True)
            time.sleep(5)
            
            toggle_airplane_mode(enable=False)
            time.sleep(5)
            
            computer_ip = check_computer_public_ip()
            print(f"테더링 공인 IP: {computer_ip}")
            print("---------------------")
            
            time.sleep(5)
    finally:
        enable_computer_wifi()

# 메인 실행
def main():
    run_as_admin()  # 관리자 권한 요청
    if not connect_device():
        return
    
    disable_computer_wifi()
    setup_network()
    enable_usb_tethering()
    toggle_airplane_mode(enable=False)
    test_ip_change()

if __name__ == "__main__":
    main()