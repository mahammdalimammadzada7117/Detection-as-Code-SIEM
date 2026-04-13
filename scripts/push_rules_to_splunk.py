import requests
import os
import configparser
import urllib3

# SSL xəbərdarlıqlarını (InsecureRequest) söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFİQURASİYA ---
SPLUNK_CONF = {
    "host": "144.126.194.146",
    "port": "55555",
    "user": "blueteam", # User "admin" dən "blueteam"ə dəyişdirildi
    "password": "aMehemmedeli.2006.1970.a"
}

def sync_detection_rules():
    # Faylın yerləşdiyi qovluqdan asılı olaraq yolu tənzimləyirik
    rules_path = "../splunk-rules/" 
    base_url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/services/saved/searches"
    
    print(f"--- SOC Automation: Syncing Rules to Splunk ---")
    
    # Qovluq yoxdursa xəta verməməsi üçün yoxlama
    if not os.path.exists(rules_path):
        print(f"❌ ERROR: '{rules_path}' qovluğu tapılmadı!")
        return

    for filename in os.listdir(rules_path):
        if filename.endswith(".conf"):
            file_path = os.path.join(rules_path, filename)
            
            # .conf faylını SOC standartlarına uyğun oxuyuruq
            config = configparser.ConfigParser()
            try:
                config.read(file_path)
                
                # Faylın daxilindəki qayda adını (section) götürürük
                rule_section = config.sections()[0]
                search_query = config[rule_section]['search']
                description = config[rule_section].get('description', 'Professional SOC Rule')

                payload = {
                    "name": rule_section,
                    "search": search_query,
                    "description": description,
                    "is_visible": "true",
                    "disabled": "0",
                    "dispatch.earliest_time": "-24h",
                    "dispatch.latest_time": "now",
                    "output_mode": "json"
                }

                # API Sorğusu
                response = requests.post(
                    base_url, 
                    data=payload, 
                    auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), 
                    verify=False
                )
                
                if response.status_code == 201:
                    print(f"✅ SUCCESS: '{rule_section}' yaradıldı.")
                elif response.status_code == 409:
                    print(f"ℹ️ INFO: '{rule_section}' artıq mövcuddur. Yenilənir (Update)...")
                    update_url = f"{base_url}/{rule_section}"
                    requests.post(
                        update_url, 
                        data=payload, 
                        auth
