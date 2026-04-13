import requests
import urllib3

# SSL (sertifikat) xəbərdarlıqlarını lab mühiti üçün söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFİQURASİYA ---
SPLUNK_CONF = {
    "host": "144.126.194.146",
    "port": "55555",  # Sənin mühitində kənara açılan port
    "user": "admin",
    "password": ""
}

def push_to_splunk(rule_name, spl_query, description):
    # Splunk REST API endpointi
    # Qeyd: Əgər 55555 birbaşa Management portuna yönləndirilmirsə, URL-də portu yoxla
    url = f"https://{SPLUNK_CONF['host']}:{SPLUNK_CONF['port']}/services/saved/searches"
    
    # Qaydanın parametrləri
    data = {
        "name": rule_name,
        "search": spl_query,
        "description": description,
        "is_visible": "true",
        "disabled": "0",  # Qaydanı dərhal aktiv et
        "dispatch.earliest_time": "-24h",
        "dispatch.latest_time": "now",
        "action.short_leadin": "Alert Tətikləndi!",
        "alert_type": "number of events",
        "alert_comparator": "greater than",
        "alert_threshold": "0"
    }
    
    try:
        # POST sorğusu ilə qaydanı Splunk-a inject edirik
        response = requests.post(
            url, 
            data=data, 
            auth=(SPLUNK_CONF['user'], SPLUNK_CONF['password']), 
            verify=False,
            timeout=15
        )
        
        if response.status_code == 201:
            print(f"✅ UĞURLU: '{rule_name}' qaydası Splunk-da yaradıldı.")
        elif response.status_code == 409:
            print(f"ℹ️ MƏLUMAT: '{rule_name}' artıq mövcuddur. GitHub-dan update etmək üçün mövcud olanı silmək və ya update metodundan istifadə lazımdır.")
        else:
            print(f"❌ XƏTA: Status {response.status_code} - Mesaj: {response.text}")
            
    except Exception as e:
        print(f"🚨 BAĞLANTI XƏTASI: Splunk serverinə qoşulmaq mümkün olmadı. Xəta: {e}")

if __name__ == "__main__":
    print("🚀 Detection-as-Code: Qaydaların sinxronizasiyası başlayır...\n")
    
    # 1-ci Professional Qayda: Brute Force Detection
    name = "Mammadzade_SOC_Brute_Force"
    query = 'index=win_logs EventCode=4625 | stats count as failed_attempts by src_ip, user | where failed_attempts > 10'
    desc = "Uğursuz giriş cəhdlərini aşkar edən professional qayda (API vasitəsilə yüklənib)."
    
    push_to_splunk(name, query, desc)
    
    # Digər 14 qaydanı da aşağıda eyni qayda ilə əlavə edəcəyik...
