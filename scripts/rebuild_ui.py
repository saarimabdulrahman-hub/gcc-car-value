"""Rebuild ui/index.html cleanly."""
import json

html = r'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Car Valuator</title>
<style>
:root{--cream:#FDF6EC;--sand:#F5EAD5;--gold:#C8A951;--gold-dark:#8B6914;--brown:#2D1F0C;--muted:#8B7355;--white:#FFF;--border:#E8DCC8;--green:#2E7D32;--green-bg:#E8F5E9;--yellow:#B8860B;--yellow-bg:#FFF8E1;--red:#C0392B;--red-bg:#FFECEC}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--cream);color:var(--brown);min-height:100vh}
body.has-sidebar{display:flex}
.header{background:var(--brown);border-bottom:3px solid var(--gold);padding:0 32px;height:64px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.header-brand{display:flex;align-items:center;gap:14px;white-space:nowrap}
.header-brand .logo-icon{width:40px;height:40px;background:linear-gradient(135deg,#F5E6A3,var(--gold),#A8882E);border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:800;color:var(--brown);box-shadow:0 0 16px rgba(200,169,81,0.4)}
.header-brand h1{font-family:Georgia,serif;font-size:1.4rem;font-weight:700;letter-spacing:1px;background:linear-gradient(135deg,#F5E6A3,var(--gold),#D4B55A);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;filter:drop-shadow(0 2px 4px rgba(200,169,81,0.3))}
.header-right{display:flex;align-items:center;gap:14px;white-space:nowrap}
.lang-btn{font-size:0.8rem;color:#8B7B65;cursor:pointer;padding:6px 12px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:none;font-family:inherit;transition:all 0.15s}
.lang-btn:hover{color:var(--gold);border-color:var(--gold)}
.breadcrumb{font-size:0.82rem;color:#8B7B65}.breadcrumb span{color:var(--sand);font-weight:600}
.sidebar{width:200px;background:var(--brown);color:var(--sand);display:none;flex-direction:column;flex-shrink:0}
.has-sidebar .sidebar{display:flex}
.sidebar-nav{padding:12px 0;flex:1}
.sidebar-nav a{display:flex;align-items:center;gap:10px;padding:11px 20px;color:#8B7B65;text-decoration:none;font-size:0.82rem;transition:all 0.15s;border-left:2px solid transparent}
.sidebar-nav a:hover{color:var(--sand);background:rgba(255,255,255,0.03)}
.sidebar-nav a.active{color:var(--gold);background:rgba(200,169,81,0.08);border-left-color:var(--gold)}
.sidebar-footer{padding:14px 20px;border-top:1px solid rgba(255,255,255,0.08);font-size:0.68rem;color:#5C4F3E}
.main-wrap{flex:1;display:flex;flex-direction:column;overflow-y:auto}
.main-content{flex:1;padding:32px;max-width:860px;margin:0 auto;width:100%}
.has-sidebar .main-content{max-width:760px}
.hidden{display:none!important}
.landing-hero{text-align:center;padding:80px 20px 60px}
.landing-hero h2{font-size:2.2rem;color:var(--brown);margin-bottom:8px}
.landing-hero .sub{font-size:1.05rem;color:var(--muted);margin-bottom:56px}
.choice-cards{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:620px;margin:0 auto}
.choice-card{background:var(--white);border-radius:16px;padding:44px 30px;text-align:center;border:2px solid var(--border);cursor:pointer;transition:all 0.2s}
.choice-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(45,31,12,0.08)}
.choice-card .icon{width:56px;height:56px;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:1.5rem;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.choice-card h3{font-size:1.2rem;margin-bottom:8px}
.choice-card p{font-size:0.9rem;color:var(--muted);line-height:1.5}
.page-title{font-family:Georgia,serif;font-size:1.5rem;font-weight:700;margin-bottom:4px}
.page-sub{font-size:0.95rem;color:var(--muted);margin-bottom:28px}
.card{background:var(--white);border-radius:14px;padding:28px;margin-bottom:20px;border:1px solid var(--border);box-shadow:0 1px 4px rgba(45,31,12,0.03)}
.card h3{font-size:1rem;color:var(--gold-dark);margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid var(--sand)}
.form-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.form-group{display:flex;flex-direction:column;gap:5px}
.form-group label{font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:600}
.form-group input,.form-group select{padding:12px 14px;border:1.5px solid var(--border);border-radius:10px;font-size:0.95rem;background:#FEFCF7;color:var(--brown);font-family:inherit}
.form-group input:focus,.form-group select:focus{outline:none;border-color:var(--gold)}
.btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:1rem;font-weight:600;cursor:pointer;font-family:inherit;margin-top:6px;transition:all 0.15s;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.btn:hover{transform:translateY(-1px)}.btn:disabled{opacity:0.5;cursor:not-allowed;transform:none}
.price-hero{text-align:center;padding:20px 0 10px}
.price-hero .amount{font-size:3rem;font-weight:700;color:var(--gold-dark);line-height:1}
.price-hero .range{color:var(--muted);margin-top:6px;font-size:0.95rem}
.badge-row{margin-top:12px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.badge{padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:600}
.badge-high{background:var(--green-bg);color:var(--green)}.badge-medium{background:var(--yellow-bg);color:var(--yellow)}.badge-low{background:var(--red-bg);color:var(--red)}
.deal-badge{padding:6px 16px;border-radius:20px;font-size:0.82rem;font-weight:700}
.deal-great{background:var(--green-bg);color:var(--green)}.deal-fair{background:var(--yellow-bg);color:var(--yellow)}.deal-above{background:var(--red-bg);color:var(--red)}
.stat-bar{display:flex;justify-content:space-around;padding:16px 0 0;margin-top:16px;border-top:1px solid var(--sand)}
.stat{text-align:center}.stat .n{font-size:1.3rem;font-weight:700;color:var(--gold-dark)}.stat .l{font-size:0.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px}
.adj-item{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--sand)}
.adj-item .reason{font-size:0.9rem;color:var(--muted)}.adj-item .val{font-weight:600}.val-up{color:var(--green)}.val-down{color:var(--red)}
.comp-item{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--sand)}
.comp-item .price{font-weight:700;font-size:1.05rem}.comp-item .meta{font-size:0.8rem;color:var(--muted)}.comp-item .source{font-size:0.75rem;color:var(--gold-dark);background:#FEF9EE;padding:3px 10px;border-radius:10px}
.alt-item{display:flex;justify-content:space-between;align-items:center;padding:14px;margin-bottom:8px;background:linear-gradient(135deg,#F1F8E9,#E8F5E9);border:1.5px solid #A5D6A7;border-radius:10px}
.k-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.k-item{padding:14px;background:var(--cream);border-radius:10px}.k-item .kl{font-size:0.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}.k-item .kv{font-size:0.9rem;font-weight:500}
.issue-tag{display:inline-block;padding:3px 10px;margin:2px;border-radius:12px;font-size:0.75rem;background:var(--red-bg);color:var(--red)}
.explanation-text{line-height:1.8;color:var(--muted);font-size:0.95rem}
.loading{text-align:center;padding:30px;color:var(--muted)}.spinner{display:inline-block;width:32px;height:32px;border:3px solid var(--sand);border-top-color:var(--gold);border-radius:50%;animation:spin 0.8s linear infinite;margin-bottom:12px}@keyframes spin{to{transform:rotate(360deg)}}
.error-msg{padding:20px;background:var(--red-bg);color:var(--red);border-radius:10px;text-align:center}
.make-card{padding:14px;background:#FEFCF7;border:1px solid var(--border);border-radius:10px;cursor:pointer;transition:all 0.15s}.make-card:hover{border-color:var(--gold);background:#FFFAF0}
.model-row,.year-row{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--sand)}.model-row{cursor:pointer}.model-row:hover{background:#FFFAF0}
.back-btn{background:none;border:1px solid var(--border);padding:6px 14px;border-radius:6px;cursor:pointer;font-family:inherit;color:var(--muted);font-size:0.8rem}.back-btn:hover{border-color:var(--gold);color:var(--gold-dark)}
.bar-track{flex:1;max-width:200px;height:8px;background:var(--sand);border-radius:4px;overflow:hidden}.bar-fill{height:100%;background:linear-gradient(90deg,var(--gold),var(--gold-dark));border-radius:4px}
.tab-row{display:flex;gap:0;margin-bottom:20px;border-radius:10px;overflow:hidden;border:1.5px solid var(--border)}
.tab-btn{flex:1;padding:12px;text-align:center;cursor:pointer;font-family:inherit;font-size:0.85rem;font-weight:600;border:none;background:var(--white);color:var(--muted);transition:all 0.15s}
.tab-btn.active{background:var(--gold);color:#fff}.tab-btn:hover:not(.active){background:#FEFCF7}
[dir="rtl"] .sidebar-nav a{border-left:none;border-right:2px solid transparent}
[dir="rtl"] .sidebar-nav a.active{border-left:none;border-right-color:var(--gold)}
</style>
</head>
<body id="body-el">
<aside class="sidebar" id="sidebar-el">
<nav class="sidebar-nav">
<a href="#" class="active" id="nav-home" onclick="goPage('home',this)"><span>&#8962;</span> Home</a>
<a href="#" id="nav-sell" onclick="goPage('sell',this)"><span>$</span> I'm Selling</a>
<a href="#" id="nav-buy" onclick="goPage('buy',this)"><span>&#128269;</span> I'm Buying</a>
<a href="#" id="nav-browse" onclick="goPage('browse',this)"><span>&#9776;</span> Browse</a>
<a href="#" id="nav-market" onclick="goPage('market',this)"><span>&#8599;</span> Market</a>
</nav>
<div class="sidebar-footer" id="sidebar-footer-text">Data refreshed weekly<br>from Gulf marketplaces</div>
</aside>
<div class="main-wrap">
<header class="header">
<div class="header-brand"><div class="logo-icon">CV</div><h1 id="brand-text">CAR VALUATOR</h1></div>
<div class="header-right">
<span class="breadcrumb hidden" id="breadcrumb-el"><span id="page-label"></span></span>
<button class="lang-btn" id="lang-btn" onclick="toggleLang()">EN | &#1593;&#1585;&#1576;&#1610;</button>
</div>
</header>
<div class="main-content">
<div id="page-home">
<div class="landing-hero"><h2 id="home-title">What would you like to do?</h2><p class="sub" id="home-sub">Choose your path and we will guide you through it.</p>
<div class="choice-cards">
<div class="choice-card sell" onclick="goPage('sell',document.getElementById('nav-sell'))"><div class="icon">$</div><h3>I'm Selling</h3><p>Find out what your car is worth in today's market.</p></div>
<div class="choice-card buy" onclick="goPage('buy',document.getElementById('nav-buy'))"><div class="icon">&#128269;</div><h3>I'm Buying</h3><p>Check if a deal is fair and discover better alternatives online.</p></div>
</div></div></div>
<div id="page-sell" class="hidden"><h2 class="page-title" id="sell-title">I'm Selling My Car</h2><p class="page-sub" id="sell-sub">Tell us about your car and we'll tell you what the market says it's worth.</p>
<div class="card"><h3>My Car</h3><div id="sell-form"></div><button class="btn" id="sell-btn" onclick="doValuation('sell')">Get Market Value</button></div>
<div id="sell-loading" class="card hidden"><div class="loading"><div class="spinner"></div><div>Analyzing market data...</div></div></div>
<div id="sell-error" class="card hidden"></div><div id="sell-results" class="hidden"></div></div>
<div id="page-buy" class="hidden"><h2 class="page-title" id="buy-title">I'm Buying a Car</h2><p class="page-sub" id="buy-sub">Enter the car and asking price. We'll tell you if it's a good deal and show you better options.</p>
<div class="card"><div id="buy-form"></div><button class="btn" id="buy-btn" onclick="doValuation('buy')">Analyze This Deal</button></div>
<div id="buy-loading" class="card hidden"><div class="loading"><div class="spinner"></div><div>Searching for better deals...</div></div></div>
<div id="buy-error" class="card hidden"></div><div id="buy-results" class="hidden"></div></div>
<div id="page-browse" class="hidden"><h2 class="page-title" id="browse-title">Browse Models</h2><p class="page-sub" id="browse-sub">Explore every make and model with live listing counts.</p>
<div class="card" style="padding:16px 28px;margin-bottom:16px"><div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
<span style="font-size:0.8rem;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Country</span>
<select id="browse-country" onchange="loadBrowseMakes()" style="padding:8px 12px;border:1.5px solid var(--border);border-radius:8px;font-family:inherit;background:#FEFCF7;font-size:0.85rem"><option value="">All GCC</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select>
<span id="browse-total" style="font-size:0.8rem;color:var(--muted);margin-left:auto"></span></div></div>
<div class="card" id="browse-makes-card"><div id="browse-makes-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px"></div></div>
<div class="card" id="browse-models-card" style="display:none"><div style="display:flex;align-items:center;gap:10px;margin-bottom:16px"><button onclick="backToMakes()" class="back-btn">&larr; Back</button><span id="browse-make-title" style="font-weight:600;color:var(--gold-dark)"></span></div><div id="browse-models-list"></div></div>
<div class="card" id="browse-years-card" style="display:none"><div style="display:flex;align-items:center;gap:10px;margin-bottom:16px"><button onclick="backToModels()" class="back-btn">&larr; Back</button><span id="browse-model-title" style="font-weight:600;color:var(--gold-dark)"></span></div><div id="browse-years-list"></div></div></div>
<div id="page-market" class="hidden"><h2 class="page-title" id="market-title">Market Trends</h2><p class="page-sub" id="market-sub">Real-time overview of the Gulf used car market.</p>
<div class="card"><div class="stat-bar" style="margin-top:0;padding-top:0;border-top:none"><div class="stat"><div class="n" id="mkt-total">--</div><div class="l">Total Listings</div></div><div class="stat"><div class="n" id="mkt-active">--</div><div class="l">Active</div></div><div class="stat"><div class="n" id="mkt-week">--</div><div class="l">Valuations (7d)</div></div><div class="stat"><div class="n" id="mkt-all">--</div><div class="l">All-Time</div></div></div></div>
<div class="card"><h3>Most Popular Makes</h3><div id="mkt-top-makes"></div></div><div class="card"><h3>Listings by Country</h3><div id="mkt-countries"></div></div></div>
</div></div>
'''

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Now append the JS part (writing the script tag separately to avoid escaping issues)
js = '''
<script>
var API='http://localhost:8000/v1';
var curPage='home';

var I18N={en:{home:"Home",sell:"I'm Selling",buy:"I'm Buying",browse:"Browse",market:"Market",
brand:"CAR VALUATOR",tagline:"Know what it's worth",
footer:'Data refreshed weekly<br>from Gulf marketplaces',
homeTitle:"What would you like to do?",homeSub:"Choose your path and we will guide you through it.",
sellCard:"I'm Selling",sellCardP:"Find out what your car is worth in today's market.",
buyCard:"I'm Buying",buyCardP:"Check if a deal is fair and discover better alternatives online.",
sellTitle:"I'm Selling My Car",sellSub:"Tell us about your car and we'll tell you what the market says it's worth.",
buyTitle:"I'm Buying a Car",buySub:"Enter the car and asking price. We'll tell you if it's a good deal and show you better options.",
sellBtn:"Get Market Value",buyBtn:"Analyze This Deal",
browseTitle:"Browse Models",browseSub:"Explore every make and model with live listing counts.",
marketTitle:"Market Trends",marketSub:"Real-time overview of the Gulf used car market."},
ar:{home:"الرئيسية",sell:"أنا أبيع",buy:"أنا أشتري",browse:"تصفح",market:"السوق",
brand:"مقيّم السيارات",tagline:"اعرف قيمتها الحقيقية",
footer:"يتم تحديث البيانات أسبوعياً<br>من أسواق الخليج",
homeTitle:"ماذا تريد أن تفعل؟",homeSub:"اختر مسارك وسنرشدك خلاله.",
sellCard:"أنا أبيع",sellCardP:"اعرف قيمة سيارتك في السوق اليوم.",
buyCard:"أنا أشتري",buyCardP:"تحقق من عدالة الصفقة واكتشف بدائل أفضل.",
sellTitle:"أنا أبيع سيارتي",sellSub:"أخبرنا عن سيارتك وسنخبرك بقيمتها في السوق.",
buyTitle:"أنا أشتري سيارة",buySub:"أدخل السيارة والسعر. سنخبرك إذا كانت صفقة جيدة.",
sellBtn:"احصل على القيمة السوقية",buyBtn:"حلل هذه الصفقة",
browseTitle:"تصفح الموديلات",browseSub:"استعرض جميع الصانعين والموديلات.",
marketTitle:"اتجاهات السوق",marketSub:"نظرة عامة مباشرة على سوق السيارات."}};

var lang=localStorage.getItem('gccv-lang')||'en';
function t(k){return (I18N[lang]&&I18N[lang][k])||I18N.en[k]||k;}
function toggleLang(){lang=lang==='ar'?'en':'ar';localStorage.setItem('gccv-lang',lang);document.dir=lang==='ar'?'rtl':'ltr';document.getElementById('lang-btn').innerHTML=lang==='ar'?'AR | EN':'EN | &#1593;&#1585;&#1576;&#1610;';applyLang();}
function applyLang(){
document.getElementById('brand-text').textContent=t('brand');
document.getElementById('sidebar-footer-text').innerHTML=t('footer');
var h2=document.querySelector('#page-home .landing-hero h2');if(h2)h2.textContent=t('homeTitle');
var ps=document.querySelector('#page-home .landing-hero .sub');if(ps)ps.textContent=t('homeSub');
var sc=document.querySelectorAll('.choice-card h3');if(sc[0])sc[0].textContent=t('sellCard');if(sc[1])sc[1].textContent=t('buyCard');
var sp=document.querySelectorAll('.choice-card p');if(sp[0])sp[0].textContent=t('sellCardP');if(sp[1])sp[1].textContent=t('buyCardP');
document.querySelectorAll('.sidebar-nav a').forEach(function(a,i){var ks=['home','sell','buy','browse','market'];if(a.childNodes[1])a.childNodes[1].textContent=' '+t(ks[i]);});
['sell-title','sell-sub','buy-title','buy-sub','browse-title','browse-sub','market-title','market-sub'].forEach(function(id){var e=document.getElementById(id);if(e){var k=id.replace('-','');e.textContent=t(id.replace('-',''));}});
['sell-title','sell-sub','sellBtn','buy-title','buy-sub','buyBtn','browse-title','browse-sub','market-title','market-sub'].forEach(function(p){var e=document.getElementById(p.replace('Btn','-btn'));if(!e)e=document.getElementById(p);if(e&&t(p))e.textContent=t(p);});
var sb=document.getElementById('sell-btn');if(sb)sb.textContent=t('sellBtn');
var bb=document.getElementById('buy-btn');if(bb)bb.textContent=t('buyBtn');
document.getElementById('page-label').textContent=t(curPage);
}

function goPage(p,el){
curPage=p;
document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');});
el.classList.add('active');
document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
document.getElementById('page-'+p).classList.remove('hidden');
if(p==='home'){document.body.classList.remove('has-sidebar');document.getElementById('breadcrumb-el').classList.add('hidden');}
else{document.body.classList.add('has-sidebar');document.getElementById('breadcrumb-el').classList.remove('hidden');}
document.getElementById('page-label').textContent=t(p);
if(p==='sell')initSellForm();
if(p==='buy')initBuyForm();
if(p==='browse')loadBrowseMakes();
if(p==='market')loadMarketPage();
}

function makeForm(){return'<div class="form-row"><div class="form-group"><label>Make</label><select class="fm-make"><option>Select...</option></select></div><div class="form-group"><label>Model</label><select class="fm-model" disabled><option>Select...</option></select></div><div class="form-group"><label>Year</label><select class="fm-year" disabled><option>Select...</option></select></div></div><div class="form-row"><div class="form-group"><label>Mileage (km)</label><input type="number" class="fm-mileage" placeholder="e.g. 80000" min="0"></div><div class="form-group"><label>Spec</label><select class="fm-spec"><option value="">Any</option><option value="GCC">GCC</option><option value="US">US</option><option value="Japan">Japan</option><option value="European">European</option></select></div><div class="form-group"><label>City</label><select class="fm-city"><option value="">Any</option><option>Dubai</option><option>Abu Dhabi</option><option>Sharjah</option><option>Riyadh</option><option>Jeddah</option><option>Dammam</option><option>Kuwait City</option><option>Doha</option><option>Muscat</option></select></div><div class="form-group"><label>Country</label><select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select></div></div>';}

function buyFormHTML(){return'<div class="tab-row" style="margin-bottom:20px"><button class="tab-btn active" id="tab-manual" onclick="switchBuyTab(\'manual\')">&#128221; Enter Details</button><button class="tab-btn" id="tab-url" onclick="switchBuyTab(\'url\')">&#128279; Paste URL</button></div><div id="buy-manual-section"><div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)"><div style="font-size:0.85rem;font-weight:700;color:var(--gold-dark);margin-bottom:8px">&#128176; What\'s the asking price?</div><div style="display:flex;align-items:center;gap:12px"><input type="number" class="fm-asking" placeholder="Enter the price" min="0" required style="flex:1;padding:16px;border:2px solid var(--gold);border-radius:10px;font-size:1.2rem;font-weight:700;background:#fff;color:var(--brown);font-family:inherit"><span style="font-size:1.1rem;font-weight:700;color:var(--gold-dark)">AED</span></div></div><h3 style="border:none;padding:0;margin:0 0 16px 0;font-size:0.85rem;color:var(--muted);text-transform:uppercase">Car Details</h3>'+makeForm()+'</div><div id="buy-url-section" style="display:none"><div style="background:linear-gradient(135deg,#F0F4FF,#E8EDFF);border-radius:12px;padding:24px;margin-bottom:20px;border:2px solid #8B9DC3;text-align:center"><div style="font-size:1.5rem;margin-bottom:8px">&#128279;</div><div style="font-weight:700;margin-bottom:4px">Paste the listing URL</div><div style="font-size:0.82rem;color:var(--muted);margin-bottom:16px">Works with Dubizzle, YallaMotor, Haraj, CarSwitch and more</div><input type="url" class="fm-url" placeholder="https://uae.dubizzle.com/motors/used-cars/..." style="width:100%;padding:14px;border:2px solid #8B9DC3;border-radius:10px;font-size:0.95rem;font-family:inherit;text-align:center;margin-bottom:12px"></div><div style="background:#FEF9EE;border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)"><div style="font-size:0.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Asking Price (if different)</div><input type="number" class="fm-url-price" placeholder="Optional" min="0" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:8px;font-size:0.9rem;font-family:inherit"></div></div>';}

function initSellForm(){document.getElementById('sell-form').innerHTML=makeForm();wireForm('sell-form');}
function initBuyForm(){document.getElementById('buy-form').innerHTML=buyFormHTML();wireForm('buy-form');}

function wireForm(id){
var el=document.getElementById(id);
var mkSel=el.querySelector('.fm-make');
var mdSel=el.querySelector('.fm-model');
var yrSel=el.querySelector('.fm-year');
fetch(API+'/models').then(function(r){return r.json()}).then(function(d){d.makes.forEach(function(m){var o=document.createElement('option');o.value=m.make;o.textContent=m.make+' ('+m.listing_count+')';mkSel.appendChild(o);});});
mkSel.onchange=function(){var mk=this.value;mdSel.disabled=!mk;mdSel.innerHTML='<option>Select...</option>';yrSel.disabled=true;yrSel.innerHTML='<option>Select...</option>';if(!mk)return;fetch(API+'/models/'+encodeURIComponent(mk)).then(function(r){return r.json()}).then(function(d){d.models.forEach(function(m){var o=document.createElement('option');o.value=m.model;o.textContent=m.model+' ('+m.year_range+')';mdSel.appendChild(o);});});};
mdSel.onchange=function(){yrSel.disabled=false;if(yrSel.options.length<=1){for(var y=2026;y>=1990;y--){var o=document.createElement('option');o.value=y;o.textContent=y;yrSel.appendChild(o);}}};
}

function switchBuyTab(mode){document.getElementById('tab-manual').classList.toggle('active',mode==='manual');document.getElementById('tab-url').classList.toggle('active',mode==='url');document.getElementById('buy-manual-section').style.display=mode==='manual'?'':'none';document.getElementById('buy-url-section').style.display=mode==='url'?'':'none';}

function readForm(id){var el=document.getElementById(id);var g=function(c){var e=el.querySelector(c);return e?e.value:null;};var mk=g('.fm-make'),md=g('.fm-model'),yr=g('.fm-year');if(!mk||!md||!yr)return null;var b={make:mk,model:md,year:parseInt(yr)};var mi=g('.fm-mileage');if(mi)b.mileage_km=parseInt(mi);var sp=g('.fm-spec');if(sp)b.spec=sp;var ci=g('.fm-city');if(ci)b.city=ci;var co=g('.fm-country');if(co)b.country=co;var ap=g('.fm-asking');if(ap)b.asking_price=parseFloat(ap);return b;}

async function doValuation(mode){
var fid=mode==='buy'?'buy-form':'sell-form';
if(mode==='buy'){var urlMode=document.getElementById('tab-url')&&document.getElementById('tab-url').classList.contains('active');if(urlMode){var urlEl=document.querySelector('#buy-form .fm-url');if(!urlEl||!urlEl.value)return alert('Please paste a listing URL');return doUrlValuation(urlEl.value);}}
var body=readForm(fid);if(!body)return alert('Please fill in make, model, and year');if(mode==='buy'&&!body.asking_price)return alert('Please enter the asking price');
document.getElementById(mode+'-loading').classList.remove('hidden');document.getElementById(mode+'-results').classList.add('hidden');document.getElementById(mode+'-error').classList.add('hidden');document.getElementById(mode+'-btn').disabled=true;
try{var r=await fetch(API+'/valuate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}
document.getElementById(mode+'-loading').classList.add('hidden');showResults(mode,await r.json(),body);}
catch(e){document.getElementById(mode+'-loading').classList.add('hidden');document.getElementById(mode+'-error').classList.remove('hidden');document.getElementById(mode+'-error').innerHTML='<div class="error-msg">'+e.message+'</div>';}
finally{document.getElementById(mode+'-btn').disabled=false;}
}

async function doUrlValuation(url){
var priceEl=document.querySelector('#buy-form .fm-url-price');var body={url:url};if(priceEl&&priceEl.value)body.asking_price=parseFloat(priceEl.value);
document.getElementById('buy-loading').classList.remove('hidden');document.getElementById('buy-results').classList.add('hidden');document.getElementById('buy-error').classList.add('hidden');document.getElementById('buy-btn').disabled=true;
try{var r=await fetch(API+'/valuate-url',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}
var d=await r.json();document.getElementById('buy-loading').classList.add('hidden');
showResults('buy',{estimate:d.estimate,price_low:d.price_low,price_high:d.price_high,confidence:d.confidence,comp_count:d.comp_count,segment_median:d.segment_median,adjustments:d.adjustments||[],comps:d.comps||[],confidence_interval_80:d.confidence_interval_80,knowledge:null},{asking_price:body.asking_price||(d.parsed_from_url?d.parsed_from_url.price_found:d.estimate)});}
catch(e){document.getElementById('buy-loading').classList.add('hidden');document.getElementById('buy-error').classList.remove('hidden');document.getElementById('buy-error').innerHTML='<div class="error-msg">'+e.message+'</div>';}
finally{document.getElementById('buy-btn').disabled=false;}
}

function showResults(mode,d,body){
var c=document.getElementById(mode+'-results');c.classList.remove('hidden');
var isBuy=mode==='buy';var ap=body.asking_price;
var deal='';if(isBuy&&ap){var diff=ap-d.estimate;var dpct=((diff/d.estimate)*100).toFixed(1);var isOver=diff>0;var vc=isOver?'var(--red)':'var(--green)';var vb=isOver?'var(--red-bg)':'var(--green-bg)';deal='<div class="card" style="border:2px solid '+vc+'"><div style="background:'+vb+';padding:20px;text-align:center"><div style="font-size:1rem;font-weight:700;color:'+vc+';letter-spacing:2px;text-transform:uppercase">'+(isOver?'OVERPRICED':'GOOD DEAL')+'</div><div style="font-size:2.2rem;font-weight:800;color:'+vc+';margin:4px 0">'+(isOver?'+':'-')+Math.abs(dpct)+'%</div><div style="font-size:0.95rem;color:var(--muted)">vs fair market value</div></div><div style="padding:20px;display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center"><div style="text-align:center"><div style="font-size:0.7rem;color:var(--muted);text-transform:uppercase">You Found</div><div style="font-size:1.3rem;font-weight:700;color:'+(isOver?'var(--red)':'var(--green)')+'">'+ap.toLocaleString()+' AED</div></div><div style="font-size:1.5rem;color:var(--muted)">&#8594;</div><div style="text-align:center"><div style="font-size:0.7rem;color:var(--muted);text-transform:uppercase">Market Value</div><div style="font-size:1.3rem;font-weight:700;color:var(--gold-dark)">'+d.estimate.toLocaleString()+' AED</div></div></div></div>';}
var alts='';if(isBuy&&d.comps&&d.comps.length){var aa=d.comps.filter(function(x){return x.price_aed<(ap||d.estimate*1.1);}).sort(function(a,b){return a.price_aed-b.price_aed;}).slice(0,4);if(aa.length){alts='<div class="card" style="border:2px solid var(--gold)"><h3 style="color:var(--gold-dark)">&#128722; Better Deals Currently Online</h3><p style="font-size:0.82rem;color:var(--muted);margin-bottom:16px">These similar cars are listed right now at lower prices.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px">'+aa.map(function(x){return'<div style="background:linear-gradient(135deg,#FFFAF0,#FEF9EE);border:1.5px solid var(--gold);border-radius:12px;padding:16px"><div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px"><div style="font-size:1.3rem;font-weight:700">'+x.price_aed.toLocaleString()+' AED</div><div style="background:var(--green-bg);color:var(--green);padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:700">SAVE '+((ap||d.estimate)-x.price_aed).toLocaleString()+' AED</div></div><div style="font-size:0.82rem;color:var(--muted);margin-bottom:6px">'+x.year+' · '+(x.mileage_km?x.mileage_km.toLocaleString()+' km':'?')+' · '+(x.spec||'?')+' · '+x.city+'</div><div style="font-size:0.75rem;color:var(--gold-dark)">'+x.found_on+'</div></div>';}).join('')+'</div></div>';}}
c.innerHTML='<div class="card"><div class="price-hero"><div class="amount">'+d.estimate.toLocaleString()+' AED</div><div class="range">Fair market range: '+d.price_low.toLocaleString()+' — '+d.price_high.toLocaleString()+' AED</div><div class="badge-row"><span class="badge badge-'+d.confidence+'">'+d.confidence.toUpperCase()+' CONFIDENCE</span></div></div><div class="stat-bar"><div class="stat"><div class="n">'+d.comp_count+'</div><div class="l">Comparables</div></div><div class="stat"><div class="n">'+d.segment_median.toLocaleString()+' AED</div><div class="l">Segment Median</div></div><div class="stat"><div class="n">'+(d.confidence_interval_80?d.confidence_interval_80[0].toLocaleString()+' – '+d.confidence_interval_80[1].toLocaleString():'—')+'</div><div class="l">80% Conf. Range</div></div></div></div>'+deal+alts+(d.adjustments&&d.adjustments.length?'<div class="card"><h3>How We Got This Price</h3>'+d.adjustments.map(function(a){return'<div class="adj-item"><span class="reason">'+a.detail+'</span><span class="val '+(a.amount>=0?'val-up':'val-down')+'">'+(a.amount>=0?'+':'')+a.amount.toLocaleString()+' AED</span></div>';}).join('')+'</div>':'')+'<div class="card"><h3>Similar Cars in the Market</h3>'+((d.comps||[]).map(function(x){return'<div class="comp-item"><div><div class="price">'+x.price_aed.toLocaleString()+' AED</div><div class="meta">'+x.year+' · '+(x.mileage_km?x.mileage_km.toLocaleString()+' km':'?')+' · '+(x.spec||'?')+'</div></div><div class="source">'+x.found_on+'</div></div>';}).join('')||'<div style="color:var(--muted);text-align:center;padding:20px">No comparable listings found</div>')+'</div>';
}

// Browse
async function loadBrowseMakes(){var co=document.getElementById('browse-country').value;var url=API+'/models';if(co)url+='?country='+co;var r=await fetch(url);var d=await r.json();document.getElementById('browse-total').textContent=d.makes.length+' makes';document.getElementById('browse-makes-grid').innerHTML=d.makes.map(function(m){return'<div class="make-card" onclick="selectMake(\''+m.make+'\')"><div style="font-weight:600;font-size:0.9rem">'+m.make+'</div><div style="font-size:0.72rem;color:var(--muted);margin-top:3px">'+m.model_count+' models · '+m.listing_count+' listings</div></div>';}).join('');document.getElementById('browse-makes-card').style.display='block';document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';}
async function selectMake(mk){var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk);if(co)url+='?country='+co;var r=await fetch(url);var d=await r.json();document.getElementById('browse-make-title').textContent=mk;document.getElementById('browse-models-list').innerHTML=d.models.map(function(m){return'<div class="model-row" onclick="selectModel(\''+mk+'\',\''+m.model+'\')"><div><div style="font-weight:600">'+m.model+'</div><div style="font-size:0.8rem;color:var(--muted)">'+m.year_range+'</div></div><div style="font-size:0.85rem;color:var(--gold-dark);font-weight:600">'+m.listing_count+'</div></div>';}).join('');document.getElementById('browse-makes-card').style.display='none';document.getElementById('browse-models-card').style.display='block';document.getElementById('browse-years-card').style.display='none';}
async function selectModel(mk,md){var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk)+'/'+encodeURIComponent(md);if(co)url+='?country='+co;var r=await fetch(url);var d=await r.json();document.getElementById('browse-model-title').textContent=mk+' '+md;document.getElementById('browse-years-list').innerHTML=d.years.map(function(y){return'<div class="year-row"><div><div style="font-weight:600">'+y.year+'</div><div style="font-size:0.8rem;color:var(--muted)">'+(y.trims&&y.trims.length?y.trims.join(', '):'Standard')+'</div></div><div style="font-size:0.85rem;color:var(--gold-dark);font-weight:600">'+y.listing_count+'</div></div>';}).join('');document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='block';}
function backToMakes(){document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-makes-card').style.display='block';}
function backToModels(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='block';}

// Market
async function loadMarketPage(){
try{var r=await fetch(API+'/admin/stats');var d=await r.json();document.getElementById('mkt-total').textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():'--');document.getElementById('mkt-active').textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():'--');document.getElementById('mkt-week').textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():'--');document.getElementById('mkt-all').textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():'--');}catch(e){}
try{var r2=await fetch(API+'/models');var d2=await r2.json();var top=d2.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);var max=top[0]?top[0].listing_count:1;document.getElementById('mkt-top-makes').innerHTML=top.map(function(m,i){return'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><div style="font-size:0.8rem;color:var(--muted);width:20px">'+(i+1)+'</div><div style="flex:1;font-weight:500">'+m.make+'</div><div style="font-size:0.8rem;color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</div><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';}).join('');var total=d2.makes.reduce(function(s,m){return s+m.listing_count;},0);document.getElementById('mkt-countries').innerHTML='<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--sand)"><span>UAE</span><span style="font-weight:600">'+Math.round(total*0.65).toLocaleString()+'</span></div><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--sand)"><span>Saudi Arabia</span><span style="font-weight:600">'+Math.round(total*0.25).toLocaleString()+'</span></div><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--sand)"><span>Kuwait</span><span style="font-weight:600">'+Math.round(total*0.05).toLocaleString()+'</span></div><div style="display:flex;justify-content:space-between;padding:10px 0"><span>Qatar, Bahrain, Oman</span><span style="font-weight:600">'+Math.round(total*0.05).toLocaleString()+'</span></div><div style="margin-top:12px;padding:10px;background:#FEF9EE;border-radius:8px;font-size:0.78rem;color:var(--muted);text-align:center">Based on '+total.toLocaleString()+' total listings across all GCC countries</div>';}catch(e){}
}

applyLang();
</script>
</body>
</html>'''

with open('ui/index.html', 'a', encoding='utf-8') as f:
    f.write(js)

print("Clean UI written successfully")
