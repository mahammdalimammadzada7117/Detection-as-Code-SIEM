import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Məlumatlarını bura bir dəfəlik tam yazaq
QRADAR_IP = "13.61.183.63"
SEC_TOKEN = "1a136df3-3a18-4bae-9a37-fd165ca9e7d6"
# Faylların olduğu tam yol
RULES_FOLDER = "/home/ec2-user/Detection-as-Code-SIEM/qradar-rules"

def push_rules():
    print(f"[*] Axtarılan qovluq: {RULES_FOLDER}")
    
    if not os.path.exists(RULES_FOLDER):
        print(f"[!] XƏTA: Qovluq tapılmadı: {RULES_FOLDER}")
        return

    files = [f for f in os.listdir(RULES_FOLDER) if f.endswith('.json')]
    print(f"[*] Tapılan JSON fayl sayı: {len(files)}")

    for filename in files:
        full_path = os.path.join(RULES_FOLDER, filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            rule_data = json.load(f)
            
        url = f"https://{QRADAR_IP}/api/analytics/rules"
        headers = {'SEC': SEC_TOKEN, 'Content-Type': 'application/json'}
        
        print(f"[*] '{filename}' göndərilir...")
        response = requests.post(url, headers=headers, data=json.dumps(rule_data), verify=False)
        
        if response.status_code in [200, 201]:
            print(f"[+] UĞURLU: {filename}")
        else:
            print(f"[-] XƏTA: {filename} (Kod: {response.status_code})")

if __name__ == "__main__":
    push_rules()
