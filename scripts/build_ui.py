"""Single script: apply URL tabs + i18n to index.html."""
with open('ui/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# === 1. Add CSS for tabs and RTL ===
css_add = '''
/* ── Toggle tabs ── */
.tab-row{display:flex;gap:0;margin-bottom:20px;border-radius:10px;overflow:hidden;border:1.5px solid var(--border)}
.tab-btn{flex:1;padding:12px;text-align:center;cursor:pointer;font-family:inherit;font-size:0.85rem;font-weight:600;border:none;background:var(--white);color:var(--muted);transition:all 0.15s}
.tab-btn.active{background:var(--gold);color:#fff}
.tab-btn:hover:not(.active){background:#FEFCF7}
/* ── RTL Support ── */
[dir="rtl"] .sidebar{border-left:none;border-right:none}
[dir="rtl"] .sidebar-nav a{border-left:none;border-right:2px solid transparent}
[dir="rtl"] .sidebar-nav a.active{border-left:none;border-right-color:var(--gold)}
[dir="rtl"] .header-brand{flex-direction:row-reverse}
[dir="rtl"] .sidebar-brand .logo{flex-direction:row-reverse}
'''
c = c.replace('/* ── Form ── */', css_add + '\n/* ── Form ── */')

# === 2. Update BUY_FORM with tabs + URL section ===
old_buy = 'const BUY_FORM = `\n<div class="form-row"><div class="form-group"><label>Make</label><select class="fm-make"><option>Select...</option></select></div>'
new_buy = '''const BUY_FORM = `
<div class="tab-row" style="margin-bottom:20px">
  <button class="tab-btn active" id="tab-manual" onclick="switchBuyTab('manual')">&#x1F4DD; Enter Details Manually</button>
  <button class="tab-btn" id="tab-url" onclick="switchBuyTab('url')">&#x1F517; Paste Listing URL</button>
</div>
<div id="buy-manual-section">
<div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)">
  <div style="font-size:0.85rem;font-weight:700;color:var(--gold-dark);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px">&#x1F4B0; What's the asking price?</div>
  <div style="display:flex;align-items:center;gap:12px">
    <input type="number" class="fm-asking" placeholder="Enter the price you saw" min="0" required style="flex:1;padding:16px;border:2px solid var(--gold);border-radius:10px;font-size:1.2rem;font-weight:700;background:#fff;color:var(--brown);font-family:inherit">
    <span style="font-size:1.1rem;font-weight:700;color:var(--gold-dark);white-space:nowrap">AED</span>
  </div>
  <div style="font-size:0.75rem;color:var(--muted);margin-top:6px">Enter the price the seller is asking — we'll tell you if it's fair and show you better alternatives</div>
</div>
<h3 style="border:none;padding:0;margin:0 0 16px 0;font-size:0.85rem;color:var(--muted);text-transform:uppercase;letter-spacing:1px">Car Details</h3>
<div class="form-row"><div class="form-group"><label>Make</label><select class="fm-make"><option>Select...</option></select></div>'''
c = c.replace(old_buy, new_buy)

# Close the buy-manual-section and add buy-url-section
old_close = '<div class="form-row"><div class="form-group"><label>Country</label><select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select></div></div>`;'
new_close = '''<div class="form-row"><div class="form-group"><label>Country</label><select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select></div></div></div>
<div id="buy-url-section" style="display:none">
  <div style="background:linear-gradient(135deg,#F0F4FF,#E8EDFF);border-radius:12px;padding:24px;margin-bottom:20px;border:2px solid #8B9DC3;text-align:center">
    <div style="font-size:1.5rem;margin-bottom:8px">&#x1F517;</div>
    <div style="font-weight:700;color:var(--brown);margin-bottom:4px">Paste the listing URL</div>
    <div style="font-size:0.82rem;color:var(--muted);margin-bottom:16px">Works with Dubizzle, YallaMotor, Haraj, CarSwitch, OpenSooq, and more</div>
    <input type="url" class="fm-url" placeholder="https://uae.dubizzle.com/motors/used-cars/..." style="width:100%;padding:14px;border:2px solid #8B9DC3;border-radius:10px;font-size:0.95rem;font-family:inherit;text-align:center;margin-bottom:12px">
    <div style="font-size:0.75rem;color:var(--muted)">We'll fetch the page, extract car details, and tell you if it's a good deal</div>
  </div>
  <div style="background:#FEF9EE;border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)">
    <div style="font-size:0.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Asking Price (if different from listing)</div>
    <input type="number" class="fm-url-price" placeholder="Optional - leave empty to use price from listing" min="0" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:8px;font-size:0.9rem;font-family:inherit">
  </div>
</div>`;'''
c = c.replace(old_close, new_close)

# === 3. Update getValuation to support URL mode ===
old_val = "if (mode === 'buy' && !body.asking_price) return alert('Please enter the asking price to analyze the deal');"
new_val = '''if (mode === 'buy') {
    const tabMode = document.getElementById('tab-url')?.classList.contains('active') ? 'url' : 'manual';
    if (tabMode === 'url') {
      const url = document.querySelector('#buy-form .fm-url')?.value;
      if (!url) return alert('Please paste a listing URL');
      return getUrlValuation(url);
    }
    if (!body.asking_price) return alert('Please enter the asking price to analyze the deal');
  }'''
c = c.replace(old_val, new_val)

# === 4. Add switchBuyTab + getUrlValuation + i18n before initForms ===
old_init = '// ── Init ──\ninitForms();'

new_all = '''// ── URL Valuation ──
function switchBuyTab(mode) {
  document.getElementById('tab-manual').classList.toggle('active', mode === 'manual');
  document.getElementById('tab-url').classList.toggle('active', mode === 'url');
  document.getElementById('buy-manual-section').style.display = mode === 'manual' ? '' : 'none';
  document.getElementById('buy-url-section').style.display = mode === 'url' ? '' : 'none';
}

async function getUrlValuation(url) {
  const priceEl = document.querySelector('#buy-form .fm-url-price');
  const body = { url: url };
  if (priceEl?.value) body.asking_price = parseFloat(priceEl.value);
  document.getElementById('buy-loading').classList.remove('hidden');
  document.getElementById('buy-results').classList.add('hidden');
  document.getElementById('buy-error').classList.add('hidden');
  document.getElementById('buy-btn').disabled = true;
  try {
    const r = await fetch(API + '/valuate-url', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    if (!r.ok) { const e = await r.json(); throw new Error(e.detail || 'Failed'); }
    const d = await r.json();
    document.getElementById('buy-loading').classList.add('hidden');
    const fakeBody = { asking_price: body.asking_price || d.parsed_from_url?.price_found || d.estimate };
    renderResults('buy', {
      estimate: d.estimate, price_low: d.price_low, price_high: d.price_high,
      confidence: d.confidence, comp_count: d.comp_count,
      segment_median: d.segment_median,
      adjustments: d.adjustments || [],
      comps: d.comps || [],
      confidence_interval_80: d.confidence_interval_80,
      knowledge: null, deal_indicator: null, deal_description: null,
    }, fakeBody);
  } catch(e) {
    document.getElementById('buy-loading').classList.add('hidden');
    document.getElementById('buy-error').classList.remove('hidden');
    document.getElementById('buy-error').innerHTML = '<div class="error-msg">' + e.message + '</div>';
  } finally { document.getElementById('buy-btn').disabled = false; }
}

// ── i18n ──
const I18N = {
  en: {
    home: "Home", selling: "I'm Selling", buying: "I'm Buying",
    browse: "Browse", market: "Market",
    carValuator: "CAR VALUATOR", tagline: "Know what it's worth",
    whatDo: "What would you like to do?",
    choosePath: "Choose your path and we'll guide you through it.",
    sellTitle: "I'm Selling My Car",
    sellSub: "Tell us about your car and we'll tell you what the market says it's worth.",
    getValue: "Get Market Value",
    buyTitle: "I'm Buying a Car",
    buySub: "Enter the car you're looking at and the asking price. We'll tell you if it's a good deal.",
    analyzeDeal: "Analyze This Deal",
    dataRefreshed: "Data refreshed weekly\\nfrom Gulf marketplaces",
    browseTitle: "Browse Models",
    browseSub: "Explore every make and model with real-time listing counts.",
    marketTitle: "Market Trends",
    marketSub: "Real-time overview of the Gulf used car market.",
  },
  ar: {
    home: "الرئيسية", selling: "أنا أبيع", buying: "أنا أشتري",
    browse: "تصفح", market: "السوق",
    carValuator: "مقيّم السيارات", tagline: "اعرف قيمتها الحقيقية",
    whatDo: "ماذا تريد أن تفعل؟",
    choosePath: "اختر مسارك وسنرشدك خلاله.",
    sellTitle: "أنا أبيع سيارتي",
    sellSub: "أخبرنا عن سيارتك وسنخبرك بقيمتها في السوق.",
    getValue: "احصل على القيمة السوقية",
    buyTitle: "أنا أشتري سيارة",
    buySub: "أدخل تفاصيل السيارة والسعر المطلوب. سنخبرك إذا كانت صفقة جيدة.",
    analyzeDeal: "حلل هذه الصفقة",
    dataRefreshed: "يتم تحديث البيانات أسبوعياً\\nمن أسواق الخليج",
    browseTitle: "تصفح الموديلات",
    browseSub: "استعرض جميع الصانعين والموديلات مع عدد الإعلانات المباشرة.",
    marketTitle: "اتجاهات السوق",
    marketSub: "نظرة عامة مباشرة على سوق السيارات المستعملة في الخليج.",
  }
};

let currentLang = localStorage.getItem('gccv-lang') || 'en';
function t(key) { return I18N[currentLang]?.[key] || I18N.en[key] || key; }

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('gccv-lang', lang);
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.lang = lang;
  document.getElementById('lang-el').textContent = lang === 'ar' ? 'AR | EN' : 'EN | عربي';
  document.querySelector('.header-brand h1').textContent = t('carValuator');
  document.querySelector('.sidebar-brand .tagline').textContent = t('tagline');
  document.querySelector('.sidebar-footer').innerHTML = t('dataRefreshed').replace('\\\\n', '<br>');
  document.querySelectorAll('.sidebar-nav a').forEach((a, i) => {
    const keys = ['home', 'selling', 'buying', 'browse', 'market'];
    if (keys[i]) a.childNodes[a.childNodes.length-1].textContent = ' ' + t(keys[i]);
  });
  // Home page
  const h2 = document.querySelector('#page-home .landing-hero h2');
  if (h2) h2.textContent = t('whatDo');
  const ps = document.querySelector('#page-home .landing-hero .sub');
  if (ps) ps.textContent = t('choosePath');
  // Section titles
  const st = document.querySelector('#page-sell .page-title');
  if (st) st.textContent = t('sellTitle');
  const ss = document.querySelector('#page-sell .page-sub');
  if (ss) ss.textContent = t('sellSub');
  const bt = document.querySelector('#page-buy .page-title');
  if (bt) bt.textContent = t('buyTitle');
  const bs = document.querySelector('#page-buy .page-sub');
  if (bs) bs.textContent = t('buySub');
  const brt = document.querySelector('#page-browse .page-title');
  if (brt) brt.textContent = t('browseTitle');
  const brs = document.querySelector('#page-browse .page-sub');
  if (brs) brs.textContent = t('browseSub');
  const mt = document.querySelector('#page-market .page-title');
  if (mt) mt.textContent = t('marketTitle');
  const ms = document.querySelector('#page-market .page-sub');
  if (ms) ms.textContent = t('marketSub');
  document.getElementById('page-label').textContent = t(currentPage || 'home');
}

document.addEventListener('DOMContentLoaded', () => { setLanguage(currentLang); });

// ── Init ──
initForms();'''

c = c.replace(old_init, new_all)

# === 5. Update language toggle to be clickable ===
c = c.replace(
    '<span class="lang">EN | عربي</span>',
    '<span class="lang" id="lang-el" onclick="setLanguage(currentLang===\'ar\'?\'en\':\'ar\')" style="cursor:pointer">EN | عربي</span>'
)

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Build complete: tabs + i18n + URL valuation all in one file")
