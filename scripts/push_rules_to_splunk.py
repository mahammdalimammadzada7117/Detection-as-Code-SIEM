import requests
import os
import configparser
import urllib3

# SSL xetalarini gormezden gelmek ucun
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_CONF = {
    "host": "144.126.194.146",
    "port": "55555",
    "user": "blueteam",
    "password": "aMehemmedeli.2006.1970.a"
}

def sync_rules():
    rules_path = "../splunk-rules/"
    base_url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/services/saved/searches"
    
    print(f"--- SOC Automation: Syncing 15 Rules to Splunk ---")
    
    if not os.path.exists(rules_path):
        print(f"❌ ERROR: '{rules_path}' qovlugu tapilmadi!")
        return

    for filename in os.listdir(rules_path):
        if filename.endswith(".conf"):
            file_path = os.path.join(rules_path, filename)
            config = configparser.ConfigParser()
            try:
                config.read(file_path)
                rule_name = config.sections()[0]
                search_query = config[rule_name]['search']
                
                payload = {
                    "name": rule_name,
                    "search": search_query,
                    "is_visible": "true",
                    "disabled": "0",
                    "dispatch.earliest_time": "-24h",
                    "dispatch.latest_time": "now",
                    "action.email.sendresults": "0",
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
                    print(f"✅ SUCCESS (Created): {rule_name}")
                elif response.status_code == 409:
                    # Eger qayda artıq varsa, UPDATE et (Müəllimin tələbi)
                    update_url = f"{base_url}/{rule_name}"
                    requests.post(update_url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
                    print(f"🔄 SUCCESS (Updated): {rule_name}")
                else:
                    print(f"❌ FAILED: {rule_name} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"⚠️ ERROR processing {filename}: {e}")

if __name__ == "__main__":
    sync_rules()
