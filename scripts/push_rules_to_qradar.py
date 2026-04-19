import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Sənin şəkillərdə təsdiqlənən məlumatlar
QRADAR_IP = "13.61.183.63"
# Şəkildə gördüyümüz Github_Integration tokeni
SEC_TOKEN = "81e8bae3-0090-4f6b-bdd1-2ffce7836519" 

# Github-dan çəkdiyin qovluğun tam yolu (Şəkil 9-dakı struktura əsasən)
RULES_FOLDER = "/home/ec2-user/Detection-as-Code-SIEM/qradar-rules/qradar-rules"

def push_rules():
    print(f"[*] Axtarılan qovluq: {RULES_FOLDER}")
    
    if not os.path.exists(RULES_FOLDER):
        print(f"[!] XƏTA: Qovluq tapılmadı! Zəhmət olmasa 'ls' yazıb yolu yoxla.")
        return

    files = [f for f in os.listdir(RULES_FOLDER) if f.endswith('.json')]
    print(f"[*] Tapılan qayda sayı: {len(files)}")

    for filename in files:
        full_path = os.path.join(RULES_FOLDER, filename)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                rule_data = json.load(f)
                
            url = f"https://{QRADAR_IP}/api/analytics/rules"
            headers = {
                'SEC': SEC_TOKEN, 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            print(f"[*] '{filename}' QRadar-a göndərilir...")
            # Qeyd: Əgər qayda artıq varsa, POST xəta verə bilər (409 Conflict). 
            # Bu halda qaydanı silib yenidən yükləməli və ya PUT istifadə etməli olacağıq.
            response = requests.post(url, headers=headers, data=json.dumps(rule_data), verify=False)
            
            if response.status_code in [200, 201]:
                print(f"[+] UĞURLU: {filename} SIEM-ə əlavə edildi.")
            elif response.status_code == 409:
                print(f"[!] KÖHNƏ: {filename} artıq SIEM-də var (Update lazımdır).")
            else:
                print(f"[-] XƏTA: {filename} (Kod: {response.status_code}, Mesaj: {response.text})")
        except Exception as e:
            print(f"[X] Fayl oxunarkən xəta: {filename} -> {e}")

if __name__ == "__main__":
    push_rules()
