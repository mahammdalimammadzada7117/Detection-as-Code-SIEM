import requests, os, configparser, urllib3
urllib3.disable_warnings()

SPLUNK_CONF = {
    "host": "144.126.194.146",
    "port": "8089", 
    "user": "blueteam",
    "password": "aMehemmedeli.2006.1970.a"
}

def sync():
    # Hazırda olduğumuz qovluğu tapırıq
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Bir üst qovluğa çıxıb splunk-rules qovluğuna gedirik
    path = os.path.abspath(os.path.join(current_dir, "..", "splunk-rules"))
    
    url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/servicesNS/admin/search/saved/searches"
    
    print(f"--- SOC Automation: API Sync Starting ---")
    print(f"DEBUG: Qovluq axtarılır: {path}")

    if not os.path.exists(path):
        print(f"❌ ERROR: Qovluq tapılmadı!")
        return

    # Siyahını götürürük
    all_files = os.listdir(path)
    conf_files = [f for f in all_files if f.endswith(".conf")]
    
    print(f"DEBUG: Tapılan cəmi fayl sayı: {len(all_files)}")
    print(f"DEBUG: Tapılan .conf fayl sayı: {len(conf_files)}")

    if len(conf_files) == 0:
        print("⚠️ Xəbərdarlıq: .conf faylı tapılmadı, qovluq boş ola bilər.")
        return

    cfg = configparser.ConfigParser(interpolation=None)

    for fn in conf_files:
        try:
            full_path = os.path.join(path, fn)
            cfg.read(full_path)
            
            if not cfg.sections():
                print(f"⚠️ {fn} faylı boşdur və ya formatı səhvdir.")
                continue
                
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
            
            res = requests.post(url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
            
            if res.status_code == 201:
                print(f"✅ Created: {name}")
            elif res.status_code in [400, 409]:
                # Update ssenarisi
                update_url = f"{url}/{name}"
                requests.post(update_url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
                print(f"🔄 Updated: {name}")
            else:
                print(f"❌ Failed: {name} (Status: {res.status_code})")
                
        except Exception as e:
            print(f"⚠️ Error in {fn}: {e}")

if __name__ == "__main__":
    sync()
