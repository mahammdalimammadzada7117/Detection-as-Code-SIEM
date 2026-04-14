import os
import json
import requests
import urllib3

# QRadar sertifikatı "Self-signed" olduğu üçün çıxan xəbərdarlıqları söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# QRadar API və Bağlantı Məlumatları
# image_53782d.png-dəki IP-ni və image_556050.png-də yaratdığımız tokeni yazırıq
QRADAR_IP = "13.61.183.63" 
SEC_TOKEN = "1a136df3-3a18-4bae-9a37-fd165ca9e7d6"

def push_rule_to_qradar(file_path):
    # JSON faylını oxuyuruq
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            rule_data = json.load(f)
            
        url = f"https://{QRADAR_IP}/api/analytics/rules"
        headers = {
            'SEC': SEC_TOKEN,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Qaydanı QRadar-a göndəririk (POST request)
        # verify=False istifadə edirik ki, SSL xətası verməsin
        response = requests.post(url, headers=headers, data=json.dumps(rule_data), verify=False)
        
        if response.status_code == 201 or response.status_code == 200:
            print(f"[+] UĞURLU: '{rule_data.get('rule_name')}' qaydası QRadar-a göndərildi.")
        else:
            print(f"[-] XƏTA: {file_path} göndərilərkən problem oldu. Kod: {response.status_code}")
            print(f"Mesaj: {response.text}")

    except Exception as e:
        print(f"[!] Fayl oxunarkən xəta baş verdi ({file_path}): {e}")

def main():
    # qradar-rules qovluğuna yol (skript scripts/ qovluğunda olduğu üçün bir pillə geri çıxırıq)
    rules_folder
