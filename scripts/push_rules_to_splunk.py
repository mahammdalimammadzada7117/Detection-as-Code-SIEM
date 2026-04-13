import requests, os, configparser, urllib3
urllib3.disable_warnings()

SPLUNK_CONF = {
    "host": "144.126.194.146",
    "port": "8089", # Adətən idarəetmə portu 8089 olur, 55555 deyilsə bunu yoxla
    "user": "blueteam",
    "password": "aMehemmedeli.2006.1970.a"
}

def sync():
    # 'interpolation=None' faiz (%) işarəsi xətasını həll edir
    cfg_parser = configparser.ConfigParser(interpolation=None)
    path = "../splunk-rules/"
    # Professional Splunk API endpoint (saved/searches)
    url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/servicesNS/admin/search/saved/searches"
    
    print("--- SOC Automation: API Sync Starting ---")

    for fn in os.listdir(path):
        if fn.endswith(".conf"):
            try:
                cfg_parser.read(os.path.join(path, fn))
                name = cfg_parser.sections()[0]
                query = cfg_parser[name]['search']
                
                payload = {
                    "name": name,
                    "search": query,
                    "is_visible": "true",
                    "disabled": "0",
                    "dispatch.earliest_time": "-24h",
                    "dispatch.latest_time": "now"
                }
                
                # Yaradırıq
                res = requests.post(url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
                
                if res.status_code == 201:
                    print(f"✅ Created: {name}")
                elif res.status_code == 409 or res.status_code == 400:
                    # Artıq varsa və ya xəta varsa UPDATE yoxlayırıq
                    update_url = f"{url}/{name}"
                    res_up = requests.post(update_url, data=payload, auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), verify=False)
                    if res_up.status_code == 200:
                        print(f"🔄 Updated: {name}")
                    else:
                        print(f"❌ Failed: {name} (Status: {res.status_code})")
            except Exception as e:
                print(f"⚠️ Error in {fn}: {e}")

if __name__ == "__main__":
    sync()
