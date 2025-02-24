import subprocess

# USB로 연결된 디바이스 확인
def check_usb_connection():
    try:
        # ADB 명령어로 연결된 디바이스 확인
        result = subprocess.run("adb devices", capture_output=True, text=True, shell=True)
        output = result.stdout.strip()
        
        # 출력에서 디바이스 목록 확인
        lines = output.splitlines()
        if len(lines) <= 1 or "device" not in output:
            print("USB로 연결된 디바이스가 없습니다. 스마트폰이 연결되어 있는지, USB 디버깅이 켜져 있는지 확인하세요.")
            return False
        else:
            print("USB로 연결된 디바이스 발견:")
            for line in lines[1:]:  # 첫 줄은 "List of devices attached"이므로 제외
                if line.strip():
                    print(f"- {line}")
            return True
    except FileNotFoundError:
        print("ADB가 설치되어 있지 않거나 PATH에 추가되지 않았습니다. ADB를 설치하고 환경 변수를 설정하세요.")
        return False

# 메인 실행
if __name__ == "__main__":
    check_usb_connection()