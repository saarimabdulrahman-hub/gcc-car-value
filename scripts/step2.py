page = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Car Valuator</title>
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
.lang-btn:hover{color:var(--gold)}
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
.form-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.form-group{display:flex;flex-direction:column;gap:5px}
.form-group label{font-size:0.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;font-weight:600}
.form-group input,.form-group select{padding:12px 14px;border:1.5px solid var(--border);border-radius:10px;font-size:0.95rem;background:#FEFCF7;color:var(--brown);font-family:inherit}
.form-group input:focus,.form-group select:focus{outline:none;border-color:var(--gold)}
.btn{width:100%;padding:14px;border:none;border-radius:10px;font-size:1rem;font-weight:600;cursor:pointer;font-family:inherit;margin-top:6px;background:linear-gradient(135deg,#C8A951,#A8882E);color:#fff}
.btn:hover{transform:translateY(-1px)}.btn:disabled{opacity:0.5}
.price-hero{text-align:center;padding:20px 0}.price-hero .amount{font-size:3rem;font-weight:700;color:var(--gold-dark)}.price-hero .range{color:var(--muted);margin-top:6px}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:600}
.badge-high{background:var(--green-bg);color:var(--green)}.badge-medium{background:#FFF8E1;color:#B8860B}
.stat-bar{display:flex;justify-content:space-around;padding:16px 0 0;margin-top:16px;border-top:1px solid var(--sand)}
.stat{text-align:center}.stat .n{font-size:1.3rem;font-weight:700;color:var(--gold-dark)}.stat .l{font-size:0.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-top:2px}
.comp-item{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--sand)}
.comp-item .price{font-weight:700}.comp-item .meta{font-size:0.8rem;color:var(--muted)}.comp-item .source{font-size:0.75rem;color:var(--gold-dark);background:#FEF9EE;padding:3px 10px;border-radius:10px}
.alt-card{background:linear-gradient(135deg,#FFFAF0,#FEF9EE);border:1.5px solid var(--gold);border-radius:12px;padding:16px;margin-bottom:8px}
.loading{text-align:center;padding:30px;color:var(--muted)}.spinner{display:inline-block;width:32px;height:32px;border:3px solid var(--sand);border-top-color:var(--gold);border-radius:50%;animation:spin 0.8s linear infinite;margin-bottom:12px}@keyframes spin{to{transform:rotate(360deg)}}
.error-msg{padding:20px;background:var(--red-bg);color:var(--red);border-radius:10px}
.make-card{padding:14px;background:#FEFCF7;border:1px solid var(--border);border-radius:10px;cursor:pointer}.make-card:hover{border-color:var(--gold);background:#FFFAF0}
.row-link{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--sand);cursor:pointer}.row-link:hover{background:#FFFAF0}
.back-btn{background:none;border:1px solid var(--border);padding:6px 14px;border-radius:6px;cursor:pointer;color:var(--muted);font-size:0.8rem;font-family:inherit}.back-btn:hover{border-color:var(--gold)}
.bar-track{flex:1;max-width:200px;height:8px;background:var(--sand);border-radius:4px;overflow:hidden}.bar-fill{height:100%;background:linear-gradient(90deg,var(--gold),var(--gold-dark));border-radius:4px}
.tab-row{display:flex;margin-bottom:20px;border-radius:10px;overflow:hidden;border:1.5px solid var(--border)}
.tab-btn{flex:1;padding:12px;text-align:center;cursor:pointer;font-size:0.85rem;font-weight:600;border:none;background:var(--white);color:var(--muted);font-family:inherit}
.tab-btn.active{background:var(--gold);color:#fff}
</style></head>
<body id="body-el">
<aside class="sidebar">
<nav class="sidebar-nav">
<a href="#" id="nav-home" onclick="goPage('home',this)">Home</a>
<a href="#" id="nav-sell" onclick="goPage('sell',this)">Sell</a>
<a href="#" id="nav-buy" onclick="goPage('buy',this)">Buy</a>
<a href="#" id="nav-browse" onclick="goPage('browse',this)">Browse</a>
<a href="#" id="nav-market" onclick="goPage('market',this)">Market</a>
</nav>
</aside>
<div class="main-wrap">
<header class="header"><div class="header-brand"><div class="logo-icon">CV</div><h1>CAR VALUATOR</h1></div><button class="lang-btn" onclick="toggleLang()">EN | AR</button></header>
<div class="main-content">
<div id="page-home"><div class="landing-hero"><h2>What would you like to do?</h2><p class="sub">Choose your path and we'll guide you through it.</p>
<div class="choice-cards">
<div class="choice-card" onclick="goPage('sell',document.getElementById('nav-sell'))"><div class="icon">$</div><h3>I'm Selling</h3><p>Find out what your car is worth.</p></div>
<div class="choice-card" onclick="goPage('buy',document.getElementById('nav-buy'))"><div class="icon">S</div><h3>I'm Buying</h3><p>Check if a deal is fair. Find better alternatives.</p></div>
</div></div></div>

<div id="page-sell" class="hidden"><h2 style="font-family:Georgia,serif;font-size:1.5rem">I'm Selling My Car</h2><p style="color:var(--muted);margin-bottom:28px">Tell us about your car and we'll tell you what the market says it's worth.</p>
<div class="card" id="sell-form-card"><h3>My Car</h3><div id="sell-form"></div><button class="btn" onclick="doValuation('sell')">Get Market Value</button></div>
<div id="sell-loading" class="card hidden"><div class="loading"><div class="spinner"></div><div>Analyzing market data...</div></div></div>
<div id="sell-error" class="card hidden"></div><div id="sell-results" class="hidden"></div></div>

<div id="page-buy" class="hidden"><h2 style="font-family:Georgia,serif;font-size:1.5rem">I'm Buying a Car</h2><p style="color:var(--muted);margin-bottom:28px">Enter the car and the asking price. We'll tell you if it's a good deal.</p>
<div class="card" id="buy-form-card"><div id="buy-form"></div><button class="btn" onclick="doValuation('buy')">Analyze This Deal</button></div>
<div id="buy-loading" class="card hidden"><div class="loading"><div class="spinner"></div><div>Searching for better deals...</div></div></div>
<div id="buy-error" class="card hidden"></div><div id="buy-results" class="hidden"></div></div>

<div id="page-browse" class="hidden"><h2 style="font-family:Georgia,serif;font-size:1.5rem">Browse Models</h2><p style="color:var(--muted);margin-bottom:28px">Explore every make and model.</p>
<div class="card" style="padding:16px 28px;margin-bottom:16px"><select id="browse-country" onchange="loadBrowseMakes()" style="padding:8px 12px;border:1.5px solid var(--border);border-radius:8px;font-family:inherit;background:#FEFCF7"><option value="">All GCC</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select><span id="browse-total" style="font-size:0.8rem;color:var(--muted);margin-left:12px"></span></div>
<div class="card" id="browse-makes-card"><div id="browse-makes-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px"></div></div>
<div class="card" id="browse-models-card" style="display:none"><button onclick="backToMakes()" class="back-btn">Back</button><span id="browse-make-title" style="font-weight:600;color:var(--gold-dark);margin-left:8px"></span><div id="browse-models-list" style="margin-top:12px"></div></div>
<div class="card" id="browse-years-card" style="display:none"><button onclick="backToModels()" class="back-btn">Back</button><span id="browse-model-title" style="font-weight:600;color:var(--gold-dark);margin-left:8px"></span><div id="browse-years-list" style="margin-top:12px"></div></div></div>

<div id="page-market" class="hidden"><h2 style="font-family:Georgia,serif;font-size:1.5rem">Market Trends</h2><p style="color:var(--muted);margin-bottom:28px">Gulf used car market overview.</p>
<div class="card"><div class="stat-bar" style="margin-top:0;padding-top:0;border-top:none"><div class="stat"><div class="n" id="mkt-total">--</div><div class="l">Total Listings</div></div><div class="stat"><div class="n" id="mkt-active">--</div><div class="l">Active</div></div><div class="stat"><div class="n" id="mkt-week">--</div><div class="l">Valuations (7d)</div></div><div class="stat"><div class="n" id="mkt-all">--</div><div class="l">All-Time</div></div></div></div>
<div class="card"><h3>Most Popular Makes</h3><div id="mkt-top-makes"></div></div></div>
</div></div>
<script>
var API='http://localhost:8000/v1';

function goPage(p,el){
document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');});
el.classList.add('active');
document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
var pg=document.getElementById('page-'+p);if(pg)pg.classList.remove('hidden');
document.body.classList.toggle('has-sidebar',p!=='home');
if(p==='sell')buildForm('sell-form',false);
if(p==='buy')buildForm('buy-form',true);
if(p==='browse')loadBrowseMakes();
if(p==='market')loadMarketPage();
}

function toggleLang(){document.body.dir=document.body.dir==='rtl'?'ltr':'rtl';}

// ---- Forms ----
function buildForm(id,isBuy){
var el=document.getElementById(id);
el.innerHTML='<div class="form-row"><div class="form-group"><label>Make</label><select class="fm-make"><option>Loading...</option></select></div><div class="form-group"><label>Model</label><select class="fm-model" disabled><option>Select model</option></select></div><div class="form-group"><label>Year</label><select class="fm-year" disabled><option>Select year</option></select></div><div class="form-group"><label>Mileage (km)</label><input type="number" class="fm-mileage" placeholder="e.g. 80000"></div></div><div class="form-row"><div class="form-group"><label>Spec</label><select class="fm-spec"><option value="">Any</option><option value="GCC">GCC</option><option value="US">US</option><option value="Japan">Japan</option></select></div><div class="form-group"><label>City</label><select class="fm-city"><option value="">Any</option><option>Dubai</option><option>Abu Dhabi</option><option>Riyadh</option><option>Jeddah</option></select></div><div class="form-group"><label>Country</label><select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option></select></div>'+
(isBuy?'<div class="form-group"><label style="color:var(--gold-dark)">Asking Price (AED)</label><input type="number" class="fm-asking" placeholder="e.g. 125000"></div>':'')+
'</div>';
wireDropdowns(el);
}

function wireDropdowns(el){
var mk=el.querySelector('.fm-make'), md=el.querySelector('.fm-model'), yr=el.querySelector('.fm-year');
fetch(API+'/models').then(function(r){return r.json()}).then(function(d){
mk.innerHTML='<option value="">Select make...</option>';
d.makes.forEach(function(m){var o=document.createElement('option');o.value=m.make;o.textContent=m.make+' ('+m.listing_count+')';mk.appendChild(o);});
});
mk.onchange=function(){
md.disabled=!this.value;md.innerHTML='<option>Select model</option>';yr.disabled=true;yr.innerHTML='<option>Select year</option>';
if(!this.value)return;
fetch(API+'/models/'+encodeURIComponent(this.value)).then(function(r){return r.json()}).then(function(d){
d.models.forEach(function(m){var o=document.createElement('option');o.value=m.model;o.textContent=m.model+' ('+m.year_range+')';md.appendChild(o);});
});
};
md.onchange=function(){
yr.disabled=false;
if(yr.options.length<=1)for(var y=2026;y>=1990;y--){var o=document.createElement('option');o.value=y;o.textContent=y;yr.appendChild(o);}
};
}

function readForm(el){
var g=function(c){var e=el.querySelector(c);return e?e.value:null;};
var mk=g('.fm-make'),md=g('.fm-model'),yr=g('.fm-year');
if(!mk||!md||!yr)return null;
var b={make:mk,model:md,year:parseInt(yr)};
var mi=g('.fm-mileage');if(mi)b.mileage_km=parseInt(mi);
var sp=g('.fm-spec');if(sp)b.spec=sp;
var ci=g('.fm-city');if(ci)b.city=ci;
var co=g('.fm-country');if(co)b.country=co;
var ap=g('.fm-asking');if(ap)b.asking_price=parseFloat(ap);
return b;
}

// ---- Valuation ----
async function doValuation(mode){
var el=document.getElementById(mode+'-form');
var body=readForm(el);if(!body)return alert('Please fill in make, model, and year');
if(mode==='buy'&&!body.asking_price)return alert('Please enter the asking price');

var ld=document.getElementById(mode+'-loading');ld.classList.remove('hidden');
var rs=document.getElementById(mode+'-results');rs.classList.add('hidden');
var er=document.getElementById(mode+'-error');er.classList.add('hidden');

try{
var r=await fetch(API+'/valuate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}
ld.classList.add('hidden');
showResults(mode,await r.json(),body);
}catch(e){ld.classList.add('hidden');er.classList.remove('hidden');er.innerHTML='<div class="error-msg">'+e.message+'</div>';}
}

function showResults(mode,d,body){
var c=document.getElementById(mode+'-results');c.classList.remove('hidden');
var ap=body.asking_price;
var h='<div class="card"><div class="price-hero"><div class="amount">'+d.estimate.toLocaleString()+' AED</div><div class="range">Range: '+d.price_low.toLocaleString()+' - '+d.price_high.toLocaleString()+' AED</div><span class="badge badge-'+d.confidence+'">'+d.confidence.toUpperCase()+'</span></div><div class="stat-bar"><div class="stat"><div class="n">'+d.comp_count+'</div><div class="l">Comparables</div></div><div class="stat"><div class="n">'+d.segment_median.toLocaleString()+' AED</div><div class="l">Median</div></div></div></div>';

// Deal analysis for buyers
if(mode==='buy'&&ap&&d.estimate){
var diff=ap-d.estimate;var dpct=((diff/d.estimate)*100).toFixed(1);var isOver=diff>0;
var vc=isOver?'var(--red)':'var(--green)';var vb=isOver?'var(--red-bg)':'var(--green-bg)';
h+='<div class="card" style="border:2px solid '+vc+'"><div style="text-align:center;padding:16px"><div style="font-size:1.5rem;font-weight:700;color:'+vc+'">'+(isOver?'OVERPRICED':'GOOD DEAL')+'</div><div style="font-size:2rem;font-weight:800;color:'+vc+'">'+(isOver?'+':'-')+Math.abs(dpct)+'%</div><div>You found: '+ap.toLocaleString()+' AED vs Market: '+d.estimate.toLocaleString()+' AED</div></div></div>';
// Alternatives
var alts=d.comps.filter(function(x){return x.price_aed<ap;}).sort(function(a,b){return a.price_aed-b.price_aed;}).slice(0,4);
if(alts.length){h+='<div class="card" style="border:2px solid var(--gold)"><h3>Better Deals Online</h3>'+alts.map(function(x){return'<div class="alt-card"><div style="display:flex;justify-content:space-between"><div style="font-size:1.2rem;font-weight:700">'+x.price_aed.toLocaleString()+' AED</div><div style="background:var(--green-bg);color:var(--green);padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:700">SAVE '+(ap-x.price_aed).toLocaleString()+' AED</div></div><div style="font-size:0.82rem;color:var(--muted);margin-top:4px">'+x.year+' &middot; '+x.mileage_km+' km &middot; '+x.spec+' &middot; '+x.city+'</div><div style="font-size:0.75rem;color:var(--gold-dark);margin-top:4px">'+x.found_on+'</div></div>';}).join('')+'</div>';}
}

// Similar cars
h+='<div class="card"><h3>Similar Cars in the Market</h3>'+(d.comps||[]).map(function(x){return'<div class="comp-item"><div><div class="price">'+x.price_aed.toLocaleString()+' AED</div><div class="meta">'+x.year+' &middot; '+(x.mileage_km?x.mileage_km.toLocaleString()+' km':'?')+' &middot; '+(x.spec||'?')+'</div></div><div class="source">'+x.found_on+'</div></div>';}).join('')+'</div>';
c.innerHTML=h;
}

// ---- Browse ----
var bmake='';
async function loadBrowseMakes(){
var co=document.getElementById('browse-country').value;var url=API+'/models';if(co)url+='?country='+co;
var r=await fetch(url);var d=await r.json();
document.getElementById('browse-total').textContent=d.makes.length+' makes';
document.getElementById('browse-makes-grid').innerHTML=d.makes.map(function(m){return'<div class="make-card" onclick="selectMake(\''+m.make+'\')"><div style="font-weight:600">'+m.make+'</div><div style="font-size:0.72rem;color:var(--muted)">'+m.model_count+' models, '+m.listing_count+' listings</div></div>';}).join('');
document.getElementById('browse-makes-card').style.display='block';document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';
}
async function selectMake(mk){bmake=mk;
var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk);if(co)url+='?country='+co;
var r=await fetch(url);var d=await r.json();
document.getElementById('browse-make-title').textContent=mk;
document.getElementById('browse-models-list').innerHTML=d.models.map(function(m){return'<div class="row-link" onclick="selectModel(\''+mk+'\',\''+m.model+'\')"><div><div style="font-weight:600">'+m.model+'</div><div style="font-size:0.8rem;color:var(--muted)">'+m.year_range+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+m.listing_count+'</div></div>';}).join('');
document.getElementById('browse-makes-card').style.display='none';document.getElementById('browse-models-card').style.display='block';
}
async function selectModel(mk,md){
var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk)+'/'+encodeURIComponent(md);if(co)url+='?country='+co;
var r=await fetch(url);var d=await r.json();
document.getElementById('browse-model-title').textContent=mk+' '+md;
document.getElementById('browse-years-list').innerHTML=d.years.map(function(y){return'<div class="row-link"><div><div style="font-weight:600">'+y.year+'</div><div style="font-size:0.8rem;color:var(--muted)">'+(y.trims&&y.trims.length?y.trims.join(', '):'Standard')+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+y.listing_count+'</div></div>';}).join('');
document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='block';
}
function backToMakes(){document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-makes-card').style.display='block';}
function backToModels(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='block';}

// ---- Market ----
async function loadMarketPage(){
try{var r=await fetch(API+'/admin/stats');var d=await r.json();document.getElementById('mkt-total').textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():'--');document.getElementById('mkt-active').textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():'--');document.getElementById('mkt-week').textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():'--');document.getElementById('mkt-all').textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():'--');}catch(e){}
try{var r2=await fetch(API+'/models');var d2=await r2.json();var top=d2.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);var max=top[0]?top[0].listing_count:1;document.getElementById('mkt-top-makes').innerHTML=top.map(function(m,i){return'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><span style="width:20px;color:var(--muted)">'+(i+1)+'</span><span style="flex:1">'+m.make+'</span><span style="color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</span><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';}).join('');}catch(e){}
}
</script>
</body></html>"""

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(page)
print('Step 2 written - ' + str(len(page)) + ' chars')
