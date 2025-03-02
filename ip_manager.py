import subprocess
import requests
import time
import os
from typing import List, Tuple, Optional

class IPManager:
    def __init__(self, adb_path: Optional[str] = None):
        if adb_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.adb_path = os.path.join(current_dir, "platform-tools-latest-windows", "platform-tools", "adb.exe")
        else:
            self.adb_path = adb_path
        
        # print(f"ADB 경로: {self.adb_path}")
        self.sleep_term = 10
        self.max_attempts = 10
    
    def check_usb_connection(self) -> bool:
        try:
            result = subprocess.run(f'"{self.adb_path}" devices', capture_output=True, text=True, shell=True)
            output = result.stdout.strip()
            
            lines = output.splitlines()
            if len(lines) <= 1 or "device" not in output:
                print("USB로 연결된 디바이스가 없습니다. 스마트폰이 연결되어 있는지, USB 디버깅이 켜져 있는지 확인하세요.")
                return False
            
            return True
        except Exception as e:
            print(f"ADB 연결 확인 중 오류 발생: {str(e)}")
            return False

    def get_lte_ip(self) -> Tuple[str, str]:
        try:
            result = subprocess.check_output(f'"{self.adb_path}" shell ip addr', shell=True).decode('utf-8')
            for line in result.splitlines():
                if "inet " in line and "inet6" not in line and "rmnet" in line:
                    ip = line.split()[1].split('/')[0]
                    interface = line.split()[-1]
                    return ip, interface
            return "IP 없음", "인터페이스 없음"
        except subprocess.CalledProcessError:
            return "ADB 명령어 실행 실패", ""

    def get_public_ip(self) -> str:
        try:
            response = requests.get("http://api.ipify.org")
            return response.text.strip()
        except Exception as e:
            return f"공인 IP 확인 실패: {str(e)}"

    def check_usb_tethering(self) -> bool:
        try:
            result = subprocess.check_output(
                f'"{self.adb_path}" shell settings get global tether_dun_required', 
                shell=True
            ).decode('utf-8').strip()
            return result == '0'
        except:
            return False

    def enable_usb_tethering(self) -> bool:
        try:
            subprocess.run(f'"{self.adb_path}" shell svc usb setFunctions rndis', shell=True)
            time.sleep(2)
            subprocess.run(f'"{self.adb_path}" shell svc usb setFunctions rndis,mtp', shell=True)
            return True
        except:
            return False

    def toggle_airplane_mode(self, state: str) -> bool:
        try:
            if state == "on":
                subprocess.run(f'"{self.adb_path}" shell su -c \'settings put global airplane_mode_on 1\'', shell=True)
                subprocess.run(f'"{self.adb_path}" shell su -c \'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true\'', shell=True)
            elif state == "off":
                subprocess.run(f'"{self.adb_path}" shell su -c \'settings put global airplane_mode_on 0\'', shell=True)
                subprocess.run(f'"{self.adb_path}" shell su -c \'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false\'', shell=True)
            return True
        except:
            return False


    def change_ip(self, max_tries: int = 100) -> List[str]:
        if not self.check_usb_connection():
            return ["디바이스 연결 실패"]

        initial_internal_ip, interface = self.get_lte_ip()
        initial_public_ip = self.get_public_ip()

        public_ips = [initial_public_ip]

        for i in range(max_tries):
            attempt = 0
            while attempt < self.max_attempts:
                self.toggle_airplane_mode("on")
                time.sleep(self.sleep_term)
                
                self.toggle_airplane_mode("off")
                time.sleep(self.sleep_term)

                if not self.check_usb_tethering():
                    self.enable_usb_tethering()
                    time.sleep(5)

                internal_ip, interface = self.get_lte_ip()
                time.sleep(3)
                public_ip = self.get_public_ip()
                
                if public_ip != public_ips[-1]:
                    public_ips.append(public_ip)
                    break
                else:
                    attempt += 1
            
            if attempt == self.max_attempts:
                print(f"[{i+1}/{max_tries}] {self.max_attempts}번 시도 후 변경 실패")
                break
        
        return public_ips

if __name__ == "__main__":
    ip_manager = IPManager()
    if ip_manager.check_usb_connection():
        ips: list[str] = ip_manager.change_ip(max_tries=1)
        # print(ips)
