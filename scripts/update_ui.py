"""Update UI with URL paste toggle on buying page."""
with open('ui/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Add toggle tab CSS
css_insert = '''/* ── Toggle tabs ── */
.tab-row{display:flex;gap:0;margin-bottom:20px;border-radius:10px;overflow:hidden;border:1.5px solid var(--border)}
.tab-btn{flex:1;padding:12px;text-align:center;cursor:pointer;font-family:inherit;font-size:0.85rem;font-weight:600;border:none;background:var(--white);color:var(--muted);transition:all 0.15s}
.tab-btn.active{background:var(--gold);color:#fff}
.tab-btn:hover:not(.active){background:#FEFCF7}
'''

c = c.replace('/* ── Form ── */', css_insert + '\n/* ── Form ── */')

# Wrap existing BUY_FORM content with manual section and add URL section
old = 'const BUY_FORM = `\n<div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)">'
new = '''const BUY_FORM = `
<div class="tab-row" style="margin-bottom:20px">
  <button class="tab-btn active" id="tab-manual" onclick="switchBuyTab('manual')">&#x1F4DD; Enter Details Manually</button>
  <button class="tab-btn" id="tab-url" onclick="switchBuyTab('url')">&#x1F517; Paste Listing URL</button>
</div>
<div id="buy-manual-section">
<div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)">'''

c = c.replace(old, new)

# Close manual section and add URL section before the closing backtick
# Find end of BUY_FORM
needle = '</div></div>`;'
idx = c.find('const BUY_FORM')
end_idx = c.find(needle, idx + 100)
if end_idx < 0:
    print("ERROR: couldn't find BUY_FORM end")
else:
    url_section = '''</div></div></div>
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
    c = c[:end_idx] + url_section + c[end_idx + len(needle):]
    print("BUY_FORM updated with tabs")

# Update getValuation to support URL mode
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

# Add new functions before init
old_init = '// ── Init ──\ninitForms();'
new_funcs = '''// ── URL Valuation ──
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

// ── Init ──
initForms();'''
c = c.replace(old_init, new_funcs)
print("Functions added")

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("All done!")
