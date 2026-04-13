import requests, os, configparser, urllib3
urllib3.disable_warnings()

SPLUNK_CONF = {
    "host": "144.126.194.146",
    "port": "8089", 
    "user": "blueteam",
    "password": "aMehemmedeli.2006.1970.a"
}

def sync():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(current_dir, "..", "splunk-rules"))
    
    # ƏN SADƏ VƏ QLOBAL ÜNVAN
    url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/services/saved/searches?output_mode=json"
    
    print(f"--- SOC Automation: API Sync Starting ---")
    
    cfg = configparser.ConfigParser(interpolation=None)
    conf_files = [f for f in os.listdir(path) if f.endswith(".conf")]

    for fn in conf_files:
        try:
            cfg.read(os.path.join(path, fn))
            name = cfg.sections()[0]
            query = cfg[name]['search']
            
            payload = {
                "name": name,
                "search": query,
                "is_visible": "true",
                "disabled": "0",
                "dispatch.earliest_time": "-24h",
                "dispatch.latest_time": "now"
            }
            
            # Həm Create, həm Update üçün tək sorğu (Splunk bəzən 409 verəndə update tələb edir)
            res = requests.post(url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
            
            if res.status_code in [201, 200]:
                print(f"✅ SUCCESS: {name}")
            elif res.status_code == 409:
                # Əgər artıq varsa, UPDATE etmək üçün sonuna adını əlavə edirik
                update_url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/services/saved/searches/{name}?output_mode=json"
                res_up = requests.post(update_url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
                if res_up.status_code == 200:
                    print(f"🔄 UPDATED: {name}")
                else:
                    print(f"❌ UPDATE FAILED: {name}")
            else:
                print(f"❌ FAILED: {name} (Status: {res.status_code})")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    sync()
