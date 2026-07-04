page = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Car Valuator</title>
<style>
:root{--cream:#FDF6EC;--gold:#C8A951;--gold-dark:#8B6914;--brown:#2D1F0C;--muted:#8B7355;--white:#FFF;--border:#E8DCC8;--sand:#F5EAD5}
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
.landing-hero h2{font-size:2.2rem;margin-bottom:8px}
.landing-hero .sub{font-size:1.05rem;color:var(--muted);margin-bottom:56px}
.choice-cards{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:620px;margin:0 auto}
.choice-card{background:var(--white);border-radius:16px;padding:44px 30px;text-align:center;border:2px solid var(--border);cursor:pointer;transition:all 0.2s}
.choice-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(45,31,12,0.08);border-color:var(--gold)}
.choice-card .icon{width:56px;height:56px;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:1.8rem;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.choice-card h3{font-size:1.2rem;margin-bottom:8px}
.choice-card p{font-size:0.9rem;color:var(--muted);line-height:1.5}
.card{background:var(--white);border-radius:14px;padding:28px;margin-bottom:20px;border:1px solid var(--border)}
.card h3{font-size:1rem;color:var(--gold-dark);margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid var(--sand)}
.form-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:14px}
.form-group{display:flex;flex-direction:column;gap:5px}
.form-group label{font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:600}
.form-group input,.form-group select{padding:12px 14px;border:1.5px solid var(--border);border-radius:10px;font-size:0.95rem;background:#FEFCF7;color:var(--brown);font-family:inherit}
.btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:1rem;font-weight:600;cursor:pointer;font-family:inherit;margin-top:6px;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.btn:hover{transform:translateY(-1px)}.btn:disabled{opacity:0.5}
.price-hero{text-align:center;padding:20px 0}.price-hero .amount{font-size:3rem;font-weight:700;color:var(--gold-dark)}.price-hero .range{color:var(--muted);margin-top:6px}
</style></head>
<body id="body-el">
<aside class="sidebar">
<nav class="sidebar-nav">
<a href="#" id="nav-home" onclick="goPage('home',this)">Home</a>
<a href="#" id="nav-sell" onclick="goPage('sell',this)">Sell</a>
<a href="#" id="nav-buy" onclick="goPage('buy',this)">Buy</a>
</nav>
</aside>
<div class="main-wrap">
<header class="header"><div class="header-brand"><div class="logo-icon">CV</div><h1>CAR VALUATOR</h1></div><button class="lang-btn" onclick="toggleLang()">EN</button></header>
<div class="main-content">
<div id="page-home"><div class="landing-hero"><h2>What would you like to do?</h2><p class="sub">Choose your path.</p>
<div class="choice-cards">
<div class="choice-card" onclick="goPage('sell',document.getElementById('nav-sell'))"><div class="icon">$</div><h3>Sell</h3><p>Value your car.</p></div>
<div class="choice-card" onclick="goPage('buy',document.getElementById('nav-buy'))"><div class="icon">S</div><h3>Buy</h3><p>Check a deal.</p></div>
</div></div></div>
<div id="page-sell" class="hidden"><h2>Sell Your Car</h2>
<div class="card"><h3>Car Details</h3>
<div id="sell-form">
<div class="form-row">
<div class="form-group"><label>Make</label><select id="smake"><option value="Toyota">Toyota</option></select></div>
<div class="form-group"><label>Model</label><select id="smodel"><option value="Land Cruiser">Land Cruiser</option></select></div>
<div class="form-group"><label>Year</label><select id="syear"><option>2018</option><option>2019</option><option>2020</option></select></div>
<div class="form-group"><label>Mileage</label><input id="smileage" type="number" placeholder="80000" value="80000"></div>
</div>
</div>
<button class="btn" onclick="doValuation('sell')">Get Value</button>
</div>
<div id="sell-result" class="hidden"></div>
</div>
<div id="page-buy" class="hidden"><h2>Buy a Car</h2>
<div class="card"><h3>Car Details</h3>
<div id="buy-form">
<div class="form-row">
<div class="form-group"><label>Make</label><select id="bmake"><option value="Toyota">Toyota</option></select></div>
<div class="form-group"><label>Model</label><select id="bmodel"><option value="Land Cruiser">Land Cruiser</option></select></div>
<div class="form-group"><label>Year</label><select id="byear"><option>2018</option></select></div>
<div class="form-group"><label>Price</label><input id="bprice" type="number" placeholder="125000" value="125000"></div>
</div>
</div>
<button class="btn" onclick="doValuation('buy')">Check Deal</button>
</div>
<div id="buy-result" class="hidden"></div>
</div>
</div></div>
<script>
function goPage(p, el) {
  document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');});
  el.classList.add('active');
  document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
  var pg = document.getElementById('page-'+p);
  if(pg) pg.classList.remove('hidden');
  document.body.classList.toggle('has-sidebar', p!=='home');
}
function toggleLang(){document.body.dir=document.body.dir==='rtl'?'ltr':'rtl';}
async function doValuation(mode) {
  var prefix = mode === 'buy' ? 'b' : 's';
  var body = {
    make: document.getElementById(prefix+'make').value,
    model: document.getElementById(prefix+'model').value,
    year: parseInt(document.getElementById(prefix+'year').value),
    mileage_km: parseInt(document.getElementById(prefix+'mileage').value) || 80000,
    spec: 'GCC', city: 'Dubai', country: 'AE'
  };
  if (mode === 'buy') body.asking_price = parseFloat(document.getElementById('bprice').value);
  try {
    var r = await fetch('http://localhost:8000/v1/valuate', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    var d = await r.json();
    var el = document.getElementById(mode+'-result');
    el.classList.remove('hidden');
    el.innerHTML = '<div class="card"><div class="price-hero"><div class="amount">'+d.estimate.toLocaleString()+' AED</div><div class="range">Range: '+d.price_low.toLocaleString()+' - '+d.price_high.toLocaleString()+'</div></div></div>';
  } catch(e) { alert('Error: '+e.message); }
}
</script>
</body></html>"""

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(page)
print('Step 1 written - ' + str(len(page)) + ' chars')
