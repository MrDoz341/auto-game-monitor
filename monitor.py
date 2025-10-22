import requests
import os
from datetime import datetime

print("=" * 50)
print("🤖 GAME MONITOR STARTED")
print("=" * 50)

# رابط Discord من الإعدادات
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

# المواقع التي نراقبها
SITES = {
    'Tf2Easy': {
        'url': 'https://www.tf2easy.com/',
        'patterns': ['free coins', 'Free Coins', 'Join now to get free coins']
    },
    'RustEasy': {
        'url': 'https://www.rusteasy.com/', 
        'patterns': ['rain event', 'Rain Event', 'RAIN EVENT']
    },
    'RustMagic': {
        'url': 'https://rustmagic.com/',
        'patterns': ['Its Raining!', 'Live Rain']
    }
}

def check_site(site_name, site_config):
    """فحص موقع لاكتشاف الأحداث"""
    try:
        print(f"🔍 Checking {site_name}...")
        
        # إرسال طلب إلى الموقع
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(site_config['url'], headers=headers, timeout=10)
        html_content = response.text
        
        # البحث عن الأنماط
        found_patterns = []
        for pattern in site_config['patterns']:
            if pattern.lower() in html_content.lower():
                found_patterns.append(pattern)
                print(f"   ✅ Found: {pattern}")
        
        if found_patterns:
            return {
                'found': True,
                'site': site_name,
                'url': site_config['url'],
                'patterns': found_patterns,
                'content': f'🎯 Event on {site_name}!\nDetected: {", ".join(found_patterns)}',
                'time': datetime.now().strftime("%H:%M:%S")
            }
        else:
            print(f"   ❌ No events found")
            return {'found': False}
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {'found': False}

def send_discord_alert(event_data):
    """إرسال إشعار إلى Discord"""
    if not DISCORD_WEBHOOK:
        print("❌ No Discord webhook setup")
        return False
    
    # إنشاء رسالة Discord
    discord_message = {
        "content": f"@everyone 🚨 **EVENT DETECTED ON {event_data['site'].upper()}!** 🚨",
        "embeds": [
            {
                "title": f"🎯 {event_data['site']}",
                "description": event_data['content'],
                "color": 65280,  # اللون الأخضر
                "fields": [
                    {
                        "name": "🔍 What was found",
                        "value": "\n".join([f"• {p}" for p in event_data['patterns']]),
                        "inline": False
                    },
                    {
                        "name": "🌐 Website", 
                        "value": f"[Click to visit]({event_data['url']})",
                        "inline": True
                    },
                    {
                        "name": "🕒 Time",
                        "value": event_data['time'],
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Auto Monitor • GitHub Actions"
                }
            }
        ]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=discord_message, timeout=10)
        if response.status_code in [200, 204]:
            print(f"✅ Alert sent to Discord!")
            return True
        else:
            print(f"❌ Failed to send: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Discord error: {str(e)}")
        return False

def main():
    """الدالة الرئيسية"""
    print("Starting monitoring process...")
    
    events_found = 0
    
    # فحص كل موقع
    for site_name, site_info in SITES.items():
        result = check_site(site_name, site_info)
        
        if result['found']:
            print(f"🎉 EVENT CONFIRMED: {site_name}")
            if send_discord_alert(result):
                events_found += 1
    
    # النتائج النهائية
    print("=" * 50)
    print(f"📊 MONITORING COMPLETE")
    print(f"🎯 Events detected: {events_found}")
    print(f"🕒 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

# بدء التشغيل
if __name__ == "__main__":
    main()
