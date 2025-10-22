import requests
import os
import re
import json
from datetime import datetime
from urllib.parse import unquote

print("=" * 60)
print("🤖 ULTIMATE GAME MONITOR - ADVANCED DETECTION")
print("=" * 60)

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

# إعدادات متقدمة للمواقع
SITES = {
    'Tf2Easy': {
        'url': 'https://www.tf2easy.com/',
        'selectors': {
            'main_container': [
                r'flex-col flex w-full h-full gap-\[12px\] mt-\[3px\]',
                r'flex-col\.flex\.w-full\.h-full\.gap-\[12px\]\.mt-\[3px\]',
                r'join-now-free-coins',
                r'event-container'
            ],
            'coins_amount': [
                r'text-\[\#FFBF54\]',
                r'text-\\\[\#FFBF54\\\]',
                r'coin-amount',
                r'amount-text'
            ],
            'button_text': [
                r'Join now to get free coins',
                r'Claim Free Coins',
                r'Get Free Coins'
            ]
        },
        'patterns': [
            'Join now to get free coins',
            'free coins',
            'text-[#FFBF54]',
            'flex-col flex w-full h-full gap-[12px] mt-[3px]'
        ]
    },
    'RustEasy': {
        'url': 'https://www.rusteasy.com/',
        'selectors': {
            'rain_container': [
                r'relative z-\[10\] bg-\[rgba\(0\,0\,0\,0\.7\)\] rounded-\[11px\]',
                r'relative\.z-\[10\]\.bg-\[rgba\(0\,0\,0\,0\.7\)\]\.rounded-\[11px\]',
                r'rain-event',
                r'live-rain'
            ],
            'rain_text': [
                r'Rain Event',
                r'RAIN EVENT',
                r'Live Rain',
                r'rain is active'
            ],
            'join_button': [
                r'Join now',
                r'Claim Rain',
                r'Participate'
            ]
        },
        'patterns': [
            'rain event',
            'Rain Event',
            'RAIN EVENT',
            'relative.z-[10].bg-[rgba(0,0,0,0.7)].rounded-[11px]',
            'Live Rain'
        ]
    }
}

class AdvancedMonitor:
    def __init__(self):
        self.last_events = self.load_last_events()
        
    def load_last_events(self):
        """تحميل آخر الأحداث المسجلة"""
        try:
            return {}
        except:
            return {}
    
    def save_last_events(self, events):
        """حفظ الأحداث الحالية"""
        try:
            self.last_events = events
        except:
            pass

    def advanced_site_check(self, site_name, site_config):
        """فحص موقع متقدم باستخدام تقنيات متعددة"""
        try:
            print(f"\n🔍 Advanced scanning {site_name}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(site_config['url'], headers=headers, timeout=15)
            html_content = response.text
            
            # نتائج الاكتشاف
            detection_results = {
                'found': False,
                'site': site_name,
                'url': site_config['url'],
                'type': 'unknown',
                'details': {},
                'confidence': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            # الاكتشاف المتقدم باستخدام تقنيات متعددة
            if site_name == 'Tf2Easy':
                result = self.detect_tf2easy_events(html_content, site_config)
            elif site_name == 'RustEasy':
                result = self.detect_rusteasy_events(html_content, site_config)
            
            if result['found']:
                detection_results.update(result)
                detection_results['found'] = True
                print(f"   🎯 ADVANCED DETECTION: {len(result['details'])} patterns found")
                
            return detection_results
            
        except Exception as e:
            print(f"   ❌ Advanced scan error: {str(e)}")
            return {'found': False, 'error': str(e)}

    def detect_tf2easy_events(self, html, site_config):
        """اكتشاف متقدم لأحداث Tf2Easy"""
        results = {
            'found': False,
            'type': 'free_coins',
            'details': {},
            'confidence': 0
        }
        
        detected_patterns = []
        
        # 1. البحث عن الهيكل الرئيسي
        main_container_found = False
        for selector in site_config['selectors']['main_container']:
            if self.fuzzy_search(html, selector):
                main_container_found = True
                detected_patterns.append(f"Main Container: {selector}")
                break
        
        # 2. البحث عن كمية العملات
        coins_amount = 'unknown'
        for amount_selector in site_config['selectors']['coins_amount']:
            amount = self.extract_coins_amount(html, amount_selector)
            if amount != 'unknown':
                coins_amount = amount
                detected_patterns.append(f"Coins Amount: {amount}")
                break
        
        # 3. البحث عن نص الزر
        button_found = False
        for button_text in site_config['selectors']['button_text']:
            if button_text.lower() in html.lower():
                button_found = True
                detected_patterns.append(f"Button Text: {button_text}")
                break
        
        # 4. البحث عن الأنماط الإضافية
        for pattern in site_config['patterns']:
            if pattern.lower() in html.lower():
                detected_patterns.append(f"Pattern: {pattern}")
        
        # حساب ثقة الاكتشاف
        confidence = 0
        if main_container_found:
            confidence += 40
        if coins_amount != 'unknown':
            confidence += 30
        if button_found:
            confidence += 30
        
        if confidence >= 50:  # حد أدنى للثقة
            results['found'] = True
            results['details'] = {
                'patterns': detected_patterns,
                'coins_amount': coins_amount,
                'main_container_found': main_container_found,
                'button_found': button_found,
                'confidence_score': confidence
            }
            results['confidence'] = confidence
        
        return results

    def detect_rusteasy_events(self, html, site_config):
        """اكتشاف متقدم لأحداث RustEasy"""
        results = {
            'found': False,
            'type': 'rain_event',
            'details': {},
            'confidence': 0
        }
        
        detected_patterns = []
        
        # 1. البحث عن حاوية المطر الرئيسية
        rain_container_found = False
        for selector in site_config['selectors']['rain_container']:
            if self.fuzzy_search(html, selector):
                rain_container_found = True
                detected_patterns.append(f"Rain Container: {selector}")
                break
        
        # 2. البحث عن نص المطر
        rain_text_found = False
        for rain_text in site_config['selectors']['rain_text']:
            if rain_text.lower() in html.lower():
                rain_text_found = True
                detected_patterns.append(f"Rain Text: {rain_text}")
                break
        
        # 3. البحث عن أزرار المشاركة
        join_button_found = False
        for button_text in site_config['selectors']['join_button']:
            if button_text.lower() in html.lower():
                join_button_found = True
                detected_patterns.append(f"Join Button: {button_text}")
                break
        
        # 4. البحث عن الأنماط الإضافية
        for pattern in site_config['patterns']:
            if pattern.lower() in html.lower():
                detected_patterns.append(f"Pattern: {pattern}")
        
        # حساب ثقة الاكتشاف
        confidence = 0
        if rain_container_found:
            confidence += 40
        if rain_text_found:
            confidence += 30
        if join_button_found:
            confidence += 30
        
        if confidence >= 50:  # حد أدنى للثقة
            results['found'] = True
            results['details'] = {
                'patterns': detected_patterns,
                'rain_container_found': rain_container_found,
                'rain_text_found': rain_text_found,
                'join_button_found': join_button_found,
                'confidence_score': confidence
            }
            results['confidence'] = confidence
        
        return results

    def fuzzy_search(self, html, pattern):
        """بحث مرن مع تحمل الأخطاء"""
        try:
            # تحويل النمط للبحث المرن
            flexible_pattern = pattern.replace('\\', '').replace(' ', '\\s*')
            matches = re.findall(flexible_pattern, html, re.IGNORECASE | re.DOTALL)
            return len(matches) > 0
        except:
            return pattern.lower() in html.lower()

    def extract_coins_amount(self, html, pattern):
        """استخراج كمية العملات بدقة"""
        try:
            # طريقة 1: البحث باستخدام regex دقيق
            coins_regex = r'(\$?[\d,]+\.?\d*)\s*coins?'
            matches = re.findall(coins_regex, html, re.IGNORECASE)
            if matches:
                return matches[0] + ' coins'
            
            # طريقة 2: البحث بالقرب من النمط المحدد
            if pattern in html:
                index = html.find(pattern)
                context = html[max(0, index-100):min(len(html), index+200)]
                amount_match = re.search(r'(\$?[\d,]+\.?\d*)', context)
                if amount_match:
                    return amount_match.group(1) + ' coins'
            
            return 'unknown'
        except:
            return 'unknown'

    def send_advanced_discord_alert(self, event_data):
        """إرسال إشعار متقدم إلى Discord"""
        if not DISCORD_WEBHOOK:
            print("❌ No Discord webhook configured")
            return False
        
        # تخصيص الرسالة حسب نوع الحدث
        if event_data['type'] == 'free_coins':
            color = 16766720  # ذهبي
            emoji = "💰"
            event_type = "FREE COINS"
        else:
            color = 3447003   # أزرق
            emoji = "🌧️"
            event_type = "RAIN EVENT"
        
        # بناء رسالة متقدمة
        discord_message = {
            "content": f"@everyone 🚨 **{emoji} {event_type} DETECTED ON {event_data['site'].upper()}!** 🚨",
            "embeds": [
                {
                    "title": f"{emoji} Advanced Detection - {event_data['site']}",
                    "description": f"**🎯 CONFIDENCE SCORE: {event_data['confidence']}%**\nAdvanced monitoring system detected a new event!",
                    "color": color,
                    "fields": [],
                    "footer": {
                        "text": "GitHub Ultimate Monitor • Advanced AI Detection"
                    },
                    "timestamp": event_data['timestamp'],
                    "thumbnail": {
                        "url": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/53/rocket_1f680.png"
                    }
                }
            ]
        }
        
        # إضافة تفاصيل الاكتشاف
        details = event_data['details']
        
        # أنماط مكتشفة
        if 'patterns' in details and details['patterns']:
            patterns_text = "\n".join([f"• {p}" for p in details['patterns'][:8]])  # أول 8 أنماط فقط
            discord_message["embeds"][0]["fields"].append({
                "name": "🔍 Detected Patterns",
                "value": patterns_text,
                "inline": False
            })
        
        # إحصائيات الاكتشاف
        stats_fields = []
        if 'coins_amount' in details and details['coins_amount'] != 'unknown':
            stats_fields.append({"name": "💰 Coins Amount", "value": details['coins_amount'], "inline": True})
        
        if 'confidence_score' in details:
            stats_fields.append({"name": "🎯 Confidence", "value": f"{details['confidence_score']}%", "inline": True})
        
        if 'main_container_found' in details:
            stats_fields.append({"name": "📦 Main Container", "value": "✅ Found" if details['main_container_found'] else "❌ Not found", "inline": True})
        
        if 'rain_container_found' in details:
            stats_fields.append({"name": "🌧️ Rain Container", "value": "✅ Found" if details['rain_container_found'] else "❌ Not found", "inline": True})
        
        # إضافة الحقول الإحصائية
        for field in stats_fields:
            discord_message["embeds"][0]["fields"].append(field)
        
        # إضافة رابط الموقع
        discord_message["embeds"][0]["fields"].append({
            "name": "🌐 Quick Action",
            "value": f"[🚀 Visit {event_data['site']}]({event_data['url']})",
            "inline": False
        })
        
        try:
            response = requests.post(DISCORD_WEBHOOK, json=discord_message, timeout=10)
            if response.status_code in [200, 204]:
                print(f"✅ Advanced alert sent successfully! (Confidence: {event_data['confidence']}%)")
                return True
            else:
                print(f"❌ Discord API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error sending advanced alert: {str(e)}")
            return False

def main():
    """الدالة الرئيسية المتقدمة"""
    print("🚀 Starting ULTIMATE monitoring system...")
    monitor = AdvancedMonitor()
    
    total_events = 0
    high_confidence_events = 0
    
    for site_name, site_config in SITES.items():
        print(f"\n{'='*50}")
        print(f"🎯 SCANNING: {site_name}")
        print(f"{'='*50}")
        
        result = monitor.advanced_site_check(site_name, site_config)
        
        if result['found']:
            print(f"🎉 ADVANCED DETECTION CONFIRMED!")
            print(f"   📊 Confidence: {result['confidence']}%")
            print(f"   🔍 Type: {result['type']}")
            print(f"   📝 Patterns: {len(result['details'].get('patterns', []))}")
            
            if result['confidence'] >= 70:  # أحداث عالية الثقة فقط
                high_confidence_events += 1
                if monitor.send_advanced_discord_alert(result):
                    total_events += 1
                else:
                    print(f"❌ Failed to send high-confidence alert for {site_name}")
            else:
                print(f"⚠️  Event detected but confidence too low ({result['confidence']}%)")
        else:
            print(f"❌ No high-confidence events detected")
    
    # النتائج النهائية
    print("\n" + "="*60)
    print("📊 ULTIMATE MONITORING REPORT")
    print("="*60)
    print(f"🎯 High-Confidence Events: {high_confidence_events}")
    print(f"📨 Notifications Sent: {total_events}")
    print(f"🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # حفظ الإحصائيات
    monitor.save_last_events({})

if __name__ == "__main__":
    main()
