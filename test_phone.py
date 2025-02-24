import subprocess

def get_lte_ip_via_adb():
    try:
        # 모든 인터페이스 정보 가져오기
        result = subprocess.check_output("adb shell ip addr", shell=True).decode('utf-8')
        print("Raw output:", result)
        
        # IP 주소 파싱 (rmnet으로 시작하는 인터페이스만)
        for line in result.splitlines():
            if "inet " in line and "inet6" not in line and "rmnet" in line:
                ip = line.split()[1].split('/')[0]
                interface = line.split()[-1]
                return f"IPv4: {ip} (인터페이스: {interface})"
        return "LTE IPv4 주소를 찾을 수 없음"
    except subprocess.CalledProcessError:
        return "ADB 명령어 실행 실패"

# 실행
print("LTE IP 주소:", get_lte_ip_via_adb())