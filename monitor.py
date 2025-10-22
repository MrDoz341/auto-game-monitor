import requests
import os
from datetime import datetime
import re

print("=" * 50)
print("🤖 ADVANCED GAME MONITOR STARTED")
print("=" * 50)

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

# المواقع مع أنماط متقدمة
SITES = {
    'Tf2Easy': {
        'url': 'https://www.tf2easy.com/',
        'patterns': [
            # الأنماط من السكريبت الأصلي
            'Join now to get free coins',
            'free coins', 
            'flex-col flex w-full h-full gap-[12px] mt-[3px]',
            'text-[#FFBF54]',
            # أنماط إضافية
            'rain event', 'Rain Event'
        ]
    },
    'RustEasy': {
        'url': 'https://www.rusteasy.com/', 
        'patterns': [
            # الأنماط من السكريبت الأصلي
            'rain event', 'Rain Event', 'RAIN EVENT',
            'relative.z-[10].bg-[rgba(0,0,0,0.7)].rounded-[11px]',
            'Live Rain',
            # أنماط إضافية
            'Join now', 'claim'
        ]
    },
    'RustMagic': {
        'url': 'https://rustmagic.com/',
        'patterns': [
            # الأنماط من السكريبت الأصلي
            'Its Raining!', 'Live Rain',
            'sc-cHHTbD', 'sc-fHsjty', 'sc-lccgLh',
            # أنماط إضافية
            'rain', 'Rain', 'RAIN'
        ]
    }
}

def check_site(site_name, site_config):
    """فحص موقع متقدم"""
    try:
        print(f"🔍 Checking {site_name}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        response = requests.get(site_config['url'], headers=headers, timeout=15)
        html_content = response.text
        
        detected_patterns = []
        detection_details = []
        
        for pattern in site_config['patterns']:
            # البحث عن الأنماط مع سياق
            if pattern in html_content:
                detected_patterns.append(pattern)
                
                # استخراج سياق النمط
                context = extract_context(html_content, pattern)
                detection_details.append(f"• {pattern}: {context}")
                
                print(f"   ✅ Found: {pattern}")
        
        if detected_patterns:
            # تحسين اكتشاف كمية العملات لـ Tf2Easy
            coins_amount = 'unknown'
            if site_name == 'Tf2Easy' and 'text-[#FFBF54]' in html_content:
                coins_amount = extract_coins_amount(html_content)
            
            return {
                'found': True,
                'site': site_name,
                'url': site_config['url'],
                'patterns': detected_patterns,
                'details': detection_details,
                'coins': coins_amount,
                'content': f'🎯 Advanced detection on {site_name}!\nFound {len(detected_patterns)} patterns',
                'time': datetime.now().strftime("%H:%M:%S")
            }
        else:
            print(f"   ❌ No patterns found")
            return {'found': False}
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {'found': False}

def extract_context(html, pattern, context_size=100):
    """استخراج النص حول النمط المكتشف"""
    try:
        index = html.find(pattern)
        if index == -1:
            return "No context"
        
        start = max(0, index - context_size)
        end = min(len(html), index + len(pattern) + context_size)
        context = html[start:end]
        
        # تنظيف HTML
        context = re.sub(r'<[^>]*>', ' ', context)
        context = re.sub(r'\s+', ' ', context).strip()
        
        return context[:150] + '...' if len(context) > 150 else context
    except:
        return "Context extraction failed"

def extract_coins_amount(html):
    """استخراج كمية العملات لـ Tf2Easy"""
    try:
        # البحث عن النمط المحدد للعملات
        pattern = r'text-\[\#FFBF54\][^>]*>([^<]+)'
        match = re.search(pattern, html)
        if match:
            return match.group(1).strip()
        
        # البحث عن أرقام قريبة من كلمة coins
        coins_pattern = r'(\$?[\d,]+\.?\d*)\s*coins?'
        match = re.search(coins_pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return 'unknown amount'
    except:
        return 'amount extraction failed'

def send_discord_alert(event_data):
    """إرسال إشعار متقدم إلى Discord"""
    if not DISCORD_WEBHOOK:
        print("❌ No Discord webhook setup")
        return False
    
    # تحديد نوع الحدث
    event_type = '💰 FREE COINS' if 'free coins' in ' '.join(event_data['patterns']).lower() else '🌧️ RAIN EVENT'
    
    discord_message = {
        "content": f"@everyone 🚨 **{event_type} ON {event_data['site'].upper()}!** 🚨",
        "embeds": [
            {
                "title": f"🎯 {event_data['site']} - {event_type}",
                "description": event_data['content'],
                "color": 16766720 if 'coins' in event_type else 3447003,
                "fields": [
                    {
                        "name": "🔍 Detected Patterns",
                        "value": "\n".join(event_data['details'][:5]),  # أول 5 أنماط فقط
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Advanced GitHub Monitor • 24/7"
                },
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    # إضافة حقل كمية العملات إذا وجد
    if event_data.get('coins') and event_data['coins'] != 'unknown amount':
        discord_message["embeds"][0]["fields"].append({
            "name": "💰 Coins Amount",
            "value": event_data['coins'],
            "inline": True
        })
    
    # إضافة حقل الرابط
    discord_message["embeds"][0]["fields"].append({
        "name": "🌐 Website",
        "value": f"[Visit {event_data['site']}]({event_data['url']})",
        "inline": True
    })
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=discord_message, timeout=10)
        if response.status_code in [200, 204]:
            print(f"✅ Advanced alert sent to Discord!")
            return True
        else:
            print(f"❌ Failed to send: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Discord error: {str(e)}")
        return False

def main():
    """الدالة الرئيسية المتقدمة"""
    print("🚀 Starting advanced monitoring process...")
    
    events_found = 0
    
    for site_name, site_info in SITES.items():
        result = check_site(site_name, site_info)
        
        if result['found']:
            print(f"🎉 ADVANCED DETECTION: {site_name}")
            print(f"   Patterns found: {len(result['patterns'])}")
            if send_discord_alert(result):
                events_found += 1
            else:
                print(f"❌ Failed to send alert for {site_name}")
    
    # النتائج النهائية
    print("=" * 50)
    print(f"📊 ADVANCED MONITORING COMPLETE")
    print(f"🎯 Events detected: {events_found}")
    print(f"🕒 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

# بدء التشغيل
if __name__ == "__main__":
    main()
