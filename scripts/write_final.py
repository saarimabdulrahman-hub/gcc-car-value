html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Car Valuator</title>
<style>
:root{--cream:#FDF6EC;--gold:#C8A951;--gold-dark:#8B6914;--brown:#2D1F0C;--muted:#8B7355;--white:#FFF;--border:#E8DCC8;--sand:#F5EAD5;--green:#2E7D32;--green-bg:#E8F5E9;--red:#C0392B;--red-bg:#FFECEC}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:var(--cream);color:var(--brown);min-height:100vh}
body.has-sidebar{display:flex}
.header{background:var(--brown);border-bottom:3px solid var(--gold);padding:0 32px;height:64px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.header-brand{display:flex;align-items:center;gap:14px}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,#F5E6A3,var(--gold),#A8882E);border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:800;color:var(--brown);box-shadow:0 0 16px rgba(200,169,81,0.4)}
.header-brand h1{font-family:Georgia,serif;font-size:1.4rem;font-weight:700;background:linear-gradient(135deg,#F5E6A3,var(--gold),#D4B55A);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.lang-btn{font-size:0.8rem;color:#8B7B65;cursor:pointer;padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:none;font-family:inherit}
.sidebar{width:200px;background:var(--brown);color:var(--sand);display:none;flex-direction:column;flex-shrink:0}
.has-sidebar .sidebar{display:flex}
.sidebar-nav{padding:12px 0;flex:1}
.sidebar-nav a{display:flex;align-items:center;gap:10px;padding:11px 20px;color:#8B7B65;text-decoration:none;font-size:0.82rem;border-left:2px solid transparent;cursor:pointer}
.sidebar-nav a:hover{color:var(--sand);background:rgba(255,255,255,0.03)}
.sidebar-nav a.active{color:var(--gold);background:rgba(200,169,81,0.08);border-left-color:var(--gold)}
.main-wrap{flex:1;display:flex;flex-direction:column;overflow-y:auto}
.main-content{flex:1;padding:32px;max-width:860px;margin:0 auto;width:100%}
.hidden{display:none!important}
.landing-hero{text-align:center;padding:80px 20px 60px}
.landing-hero h2{font-size:2.2rem}
.landing-hero .sub{font-size:1.05rem;color:var(--muted);margin-bottom:56px}
.choice-cards{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:620px;margin:0 auto}
.choice-card{background:var(--white);border-radius:16px;padding:44px 30px;text-align:center;border:2px solid var(--border);cursor:pointer}
.choice-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(45,31,12,0.08);border-color:var(--gold)}
.choice-card .icon{width:56px;height:56px;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:1.8rem;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.choice-card h3{font-size:1.2rem;margin-bottom:8px}
.choice-card p{font-size:0.9rem;color:var(--muted);line-height:1.5}
.page-title{font-family:Georgia,serif;font-size:1.5rem;font-weight:700;margin-bottom:4px}
.page-sub{font-size:0.95rem;color:var(--muted);margin-bottom:28px}
.card{background:var(--white);border-radius:14px;padding:28px;margin-bottom:20px;border:1px solid var(--border)}
.card h3{font-size:1rem;color:var(--gold-dark);margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid var(--sand)}
.form-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:14px}
.form-group{display:flex;flex-direction:column;gap:5px}
.form-group label{font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:600}
.form-group input,.form-group select{padding:12px 14px;border:1.5px solid var(--border);border-radius:10px;font-size:0.95rem;background:#FEFCF7;color:var(--brown);font-family:inherit}
.btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:1rem;font-weight:600;cursor:pointer;font-family:inherit;margin-top:6px;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.btn:hover{transform:translateY(-1px)}
.price-hero{text-align:center;padding:20px 0}
.price-hero .amount{font-size:3rem;font-weight:700;color:var(--gold-dark)}
.price-hero .range{color:var(--muted);margin-top:6px}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:600}
.badge-high{background:var(--green-bg);color:var(--green)}.badge-medium{background:#FFF8E1;color:#B8860B}
.comp-item{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--sand)}
.comp-item .price{font-weight:700}.comp-item .meta{font-size:0.8rem;color:var(--muted)}.comp-item .source{font-size:0.75rem;color:var(--gold-dark);background:#FEF9EE;padding:3px 10px;border-radius:10px}
</style>
</head>
<body id="body-el">

<aside class="sidebar">
<nav class="sidebar-nav">
<a href="#" id="nav-home" onclick="goPage('home',this)">Home</a>
<a href="#" id="nav-sell" onclick="goPage('sell',this)">Sell</a>
<a href="#" id="nav-buy" onclick="goPage('buy',this)">Buy</a>
</nav>
</aside>

<div class="main-wrap">
<header class="header">
<div class="header-brand"><div class="logo-icon">CV</div><h1>CAR VALUATOR</h1></div>
<button class="lang-btn" onclick="toggleLang()">EN | AR</button>
</header>

<div class="main-content">

<div id="page-home">
<div class="landing-hero">
<h2>What would you like to do?</h2>
<p class="sub">Choose your path and we will guide you through it.</p>
<div class="choice-cards">
<div class="choice-card" onclick="goPage('sell',document.getElementById('nav-sell'))">
<div class="icon">$</div><h3>I am Selling</h3><p>Find out what your car is worth.</p>
</div>
<div class="choice-card" onclick="goPage('buy',document.getElementById('nav-buy'))">
<div class="icon">S</div><h3>I am Buying</h3><p>Check if a deal is fair.</p>
</div>
</div></div></div>

<div id="page-sell" class="hidden">
<h2 class="page-title">I am Selling My Car</h2>
<p class="page-sub">Tell us about your car.</p>
<div class="card"><h3>My Car</h3>
<div class="form-row">
<div class="form-group"><label>Make</label><select id="smake"><option value="Toyota">Toyota</option></select></div>
<div class="form-group"><label>Model</label><select id="smodel"><option value="Land Cruiser">Land Cruiser</option></select></div>
<div class="form-group"><label>Year</label><select id="syear"><option>2018</option><option>2019</option><option>2020</option></select></div>
<div class="form-group"><label>Mileage</label><input id="smileage" type="number" placeholder="80000" value="80000"></div>
</div>
<button class="btn" onclick="doValuation('sell')">Get Market Value</button>
</div>
<div id="sell-result" class="hidden"></div>
</div>

<div id="page-buy" class="hidden">
<h2 class="page-title">I am Buying a Car</h2>
<p class="page-sub">Enter the car and asking price.</p>
<div class="card"><h3>The Car</h3>
<div class="form-row">
<div class="form-group"><label>Make</label><select id="bmake"><option value="Toyota">Toyota</option></select></div>
<div class="form-group"><label>Model</label><select id="bmodel"><option value="Land Cruiser">Land Cruiser</option></select></div>
<div class="form-group"><label>Year</label><select id="byear"><option>2018</option></select></div>
<div class="form-group"><label>Asking Price (AED)</label><input id="bprice" type="number" placeholder="125000" value="125000"></div>
</div>
<button class="btn" onclick="doValuation('buy')">Analyze This Deal</button>
</div>
<div id="buy-result" class="hidden"></div>
</div>

</div></div>

<script>
function goPage(p, el) {
  var links = document.querySelectorAll('.sidebar-nav a');
  for (var i = 0; i < links.length; i++) links[i].classList.remove('active');
  el.classList.add('active');
  var pages = document.querySelectorAll('[id^="page-"]');
  for (var j = 0; j < pages.length; j++) pages[j].classList.add('hidden');
  var pg = document.getElementById('page-' + p);
  if (pg) pg.classList.remove('hidden');
  if (p === 'home') document.body.classList.remove('has-sidebar');
  else document.body.classList.add('has-sidebar');
}

function toggleLang() {
  if (document.body.dir === 'rtl') document.body.dir = 'ltr';
  else document.body.dir = 'rtl';
}

async function doValuation(mode) {
  var prefix = mode === 'buy' ? 'b' : 's';
  var body = {
    make: document.getElementById(prefix + 'make').value,
    model: document.getElementById(prefix + 'model').value,
    year: parseInt(document.getElementById(prefix + 'year').value),
    mileage_km: parseInt(document.getElementById(prefix + 'mileage').value) || 80000,
    spec: 'GCC',
    city: 'Dubai',
    country: 'AE'
  };
  if (mode === 'buy') {
    body.asking_price = parseFloat(document.getElementById('bprice').value);
  }

  try {
    var response = await fetch('http://localhost:8000/v1/valuate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    var data = await response.json();
    var resultEl = document.getElementById(mode + '-result');
    resultEl.classList.remove('hidden');

    var html = '<div class="card"><div class="price-hero"><div class="amount">' + data.estimate.toLocaleString() + ' AED</div><div class="range">Range: ' + data.price_low.toLocaleString() + ' - ' + data.price_high.toLocaleString() + '</div><span class="badge badge-' + data.confidence + '">' + data.confidence.toUpperCase() + '</span></div>';

    if (mode === 'buy' && body.asking_price) {
      var diff = body.asking_price - data.estimate;
      var dpct = ((diff / data.estimate) * 100).toFixed(1);
      var isOver = diff > 0;
      var color = isOver ? 'var(--red)' : 'var(--green)';
      html += '<div class="card" style="border:2px solid ' + color + '"><div style="text-align:center;padding:16px"><div style="font-size:1.5rem;font-weight:700;color:' + color + '">' + (isOver ? 'OVERPRICED' : 'GOOD DEAL') + '</div><div style="font-size:2rem;font-weight:800">' + (isOver ? '+' : '-') + Math.abs(dpct) + '%</div><div>Asking: ' + body.asking_price.toLocaleString() + ' AED vs Market: ' + data.estimate.toLocaleString() + ' AED</div></div></div>';
    }

    var comps = data.comps || [];
    html += '<div class="card"><h3>Similar Cars</h3>';
    for (var k = 0; k < Math.min(comps.length, 5); k++) {
      var c = comps[k];
      html += '<div class="comp-item"><div><div class="price">' + c.price_aed.toLocaleString() + ' AED</div><div class="meta">' + c.year + ' - ' + (c.mileage_km || '?') + ' km - ' + (c.spec || '?') + '</div></div><div class="source">' + c.found_on + '</div></div>';
    }
    html += '</div>';

    resultEl.innerHTML = html;
  } catch (e) {
    alert('Error: ' + e.message);
  }
}
</script>
</body>
</html>'''

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Written: ' + str(len(html)) + ' bytes')
