
var API='http://localhost:8000/v1';
var curPage='home';
var lang='en';

var TXT={en:{sellTitle:"I'm Selling My Car",sellSub:"Tell us about your car and we'll tell you what the market says it's worth.",sellBtn:"Get Market Value",buyTitle:"I'm Buying a Car",buySub:"Enter the car and asking price. We'll tell you if it's a good deal.",buyBtn:"Analyze This Deal"},ar:{sellTitle:"أنا أبيع سيارتي",sellSub:"أخبرنا عن سيارتك وسنخبرك بقيمتها في السوق.",sellBtn:"احصل على القيمة السوقية",buyTitle:"أنا أشتري سيارة",buySub:"أدخل السيارة والسعر. سنخبرك إذا كانت صفقة جيدة.",buyBtn:"حلل هذه الصفقة"}};
function t(k){return (TXT[lang]&&TXT[lang][k])||TXT.en[k]||k;}

function goPage(p,el){
curPage=p;
document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');});
el.classList.add('active');
document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
document.getElementById('page-'+p).classList.remove('hidden');
if(p==='home'){document.body.classList.remove('has-sidebar');}
else{document.body.classList.add('has-sidebar');}
if(p==='sell')initForm('sell');
if(p==='buy')initForm('buy');
if(p==='browse')loadBrowseMakes();
if(p==='market')loadMarketPage();
applyLabels();
}

function toggleLang(){lang=lang==='ar'?'en':'ar';document.body.dir=lang==='ar'?'rtl':'ltr';document.querySelector('.lang-btn').textContent=lang==='ar'?'AR | EN':'EN | عربي';applyLabels();}

function applyLabels(){
var el=function(id,k){var e=document.getElementById(id);if(e&&t(k))e.textContent=t(k);};
el('sell-title','sellTitle');el('sell-sub','sellSub');el('sell-btn','sellBtn');
el('buy-title','buyTitle');el('buy-sub','buySub');el('buy-btn','buyBtn');
}

function makeForm(showAsking){
var h='<div class="form-row"><div class="form-group"><label>Make</label><select class="fm-make"><option>Loading...</option></select></div><div class="form-group"><label>Model</label><select class="fm-model" disabled><option>Select model...</option></select></div><div class="form-group"><label>Year</label><select class="fm-year" disabled><option>Select year...</option></select></div></div><div class="form-row"><div class="form-group"><label>Mileage (km)</label><input type="number" class="fm-mileage" placeholder="e.g. 80000" min="0"></div><div class="form-group"><label>Spec</label><select class="fm-spec"><option value="">Any</option><option value="GCC">GCC</option><option value="US">US</option><option value="Japan">Japan</option><option value="European">European</option></select></div><div class="form-group"><label>City</label><select class="fm-city"><option value="">Any</option><option>Dubai</option><option>Abu Dhabi</option><option>Sharjah</option><option>Riyadh</option><option>Jeddah</option><option>Dammam</option><option>Kuwait City</option><option>Doha</option><option>Muscat</option></select></div><div class="form-group"><label>Country</label><select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select></div></div>';
if(showAsking)h='<div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)"><div style="font-size:0.85rem;font-weight:700;color:var(--gold-dark);margin-bottom:8px">What\'s the asking price?</div><div style="display:flex;align-items:center;gap:12px"><input type="number" class="fm-asking" placeholder="Enter the price" min="0" style="flex:1;padding:16px;border:2px solid var(--gold);border-radius:10px;font-size:1.2rem;font-weight:700;background:#fff;color:var(--brown);font-family:inherit"><span style="font-size:1.1rem;font-weight:700;color:var(--gold-dark)">AED</span></div></div><h3 style="border:none;padding:0;margin:0 0 16px 0;font-size:0.85rem;color:var(--muted);text-transform:uppercase">Car Details</h3>'+h;
return h;
}

var buyTabMode='manual';
function buyFormHTML(){
return '<div class="tab-row" style="margin-bottom:20px"><button class="tab-btn active" id="tab-manual" onclick="switchBuyTab('manual')">Enter Details</button><button class="tab-btn" id="tab-url" onclick="switchBuyTab('url')">Paste URL</button></div><div id="buy-manual-section">'+makeForm(true)+'</div><div id="buy-url-section" style="display:none"><div style="background:linear-gradient(135deg,#F0F4FF,#E8EDFF);border-radius:12px;padding:24px;margin-bottom:20px;border:2px solid #8B9DC3;text-align:center"><div style="font-size:1.5rem;margin-bottom:8px">&#128279;</div><div style="font-weight:700;margin-bottom:4px">Paste the listing URL</div><div style="font-size:0.82rem;color:var(--muted);margin-bottom:16px">Works with Dubizzle, YallaMotor, Haraj, and more</div><input type="url" class="fm-url" placeholder="https://uae.dubizzle.com/motors/used-cars/..." style="width:100%;padding:14px;border:2px solid #8B9DC3;border-radius:10px;font-size:0.95rem;font-family:inherit;text-align:center;margin-bottom:12px"></div><div style="background:#FEF9EE;border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)"><div style="font-size:0.8rem;color:var(--muted);margin-bottom:8px">Asking Price (if different)</div><input type="number" class="fm-url-price" placeholder="Optional" min="0" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:8px;font-size:0.9rem;font-family:inherit"></div></div>';
}

function switchBuyTab(mode){buyTabMode=mode;document.getElementById('tab-manual').classList.toggle('active',mode==='manual');document.getElementById('tab-url').classList.toggle('active',mode==='url');document.getElementById('buy-manual-section').style.display=mode==='manual'?'':'none';document.getElementById('buy-url-section').style.display=mode==='url'?'':'none';}

function initForm(mode){
var id=mode==='buy'?'buy-form':'sell-form';
var el=document.getElementById(id);
el.innerHTML=mode==='buy'?buyFormHTML():makeForm(false);
// Wire make dropdown
var mkSel=el.querySelector('.fm-make');
fetch(API+'/models').then(function(r){return r.json()}).then(function(d){
mkSel.innerHTML='<option value="">Select make...</option>';
d.makes.forEach(function(m){var o=document.createElement('option');o.value=m.make;o.textContent=m.make+' ('+m.listing_count+')';mkSel.appendChild(o);});
});
mkSel.onchange=function(){
var mk=this.value;var mdSel=el.querySelector('.fm-model');var yrSel=el.querySelector('.fm-year');
mdSel.disabled=!mk;mdSel.innerHTML='<option>Select model...</option>';yrSel.disabled=true;yrSel.innerHTML='<option>Select year...</option>';
if(!mk)return;
fetch(API+'/models/'+encodeURIComponent(mk)).then(function(r){return r.json()}).then(function(d){
d.models.forEach(function(m){var o=document.createElement('option');o.value=m.model;o.textContent=m.model+' ('+m.year_range+')';mdSel.appendChild(o);});
});
};
el.querySelector('.fm-model').onchange=function(){
var yrSel=el.querySelector('.fm-year');yrSel.disabled=false;
if(yrSel.options.length<=1){for(var y=2026;y>=1990;y--){var o=document.createElement('option');o.value=y;o.textContent=y;yrSel.appendChild(o);}}
};
}

function readForm(id){
var el=document.getElementById(id);
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

async function doValuation(mode){
var fid=mode==='buy'?'buy-form':'sell-form';
if(mode==='buy'&&buyTabMode==='url'){
var urlEl=document.querySelector('#buy-form .fm-url');
if(!urlEl||!urlEl.value)return alert('Please paste a listing URL');
return doUrlValuation(urlEl.value);
}
var body=readForm(fid);if(!body)return alert('Please fill in make, model, and year');
if(mode==='buy'&&!body.asking_price)return alert('Please enter the asking price');

var ld=document.getElementById(mode+'-loading');ld.classList.remove('hidden');
var rs=document.getElementById(mode+'-results');rs.classList.add('hidden');
var er=document.getElementById(mode+'-error');er.classList.add('hidden');
var bt=document.getElementById(mode+'-btn');bt.disabled=true;

try{
var r=await fetch(API+'/valuate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}
ld.classList.add('hidden');showResults(mode,await r.json(),body);
}catch(e){ld.classList.add('hidden');er.classList.remove('hidden');er.innerHTML='<div class="error-msg">'+e.message+'</div>';}
finally{bt.disabled=false;}
}

async function doUrlValuation(url){
var priceEl=document.querySelector('#buy-form .fm-url-price');
var body={url:url};if(priceEl&&priceEl.value)body.asking_price=parseFloat(priceEl.value);
var ld=document.getElementById('buy-loading');ld.classList.remove('hidden');
var rs=document.getElementById('buy-results');rs.classList.add('hidden');
var er=document.getElementById('buy-error');er.classList.add('hidden');
var bt=document.getElementById('buy-btn');bt.disabled=true;
try{
var r=await fetch(API+'/valuate-url',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}
var d=await r.json();ld.classList.add('hidden');
showResults('buy',{estimate:d.estimate,price_low:d.price_low,price_high:d.price_high,confidence:d.confidence,comp_count:d.comp_count,segment_median:d.segment_median,adjustments:d.adjustments||[],comps:d.comps||[],confidence_interval_80:d.confidence_interval_80},{asking_price:body.asking_price||(d.parsed_from_url?d.parsed_from_url.price_found:d.estimate)});
}catch(e){ld.classList.add('hidden');er.classList.remove('hidden');er.innerHTML='<div class="error-msg">'+e.message+'</div>';}
finally{bt.disabled=false;}
}

function showResults(mode,d,body){
var c=document.getElementById(mode+'-results');c.classList.remove('hidden');
var ap=body.asking_price;
var h='<div class="card"><div class="price-hero"><div class="amount">'+d.estimate.toLocaleString()+' AED</div><div class="range">Range: '+d.price_low.toLocaleString()+' - '+d.price_high.toLocaleString()+' AED</div><div class="badge-row"><span class="badge badge-'+d.confidence+'">'+d.confidence.toUpperCase()+'</span></div></div><div class="stat-bar"><div class="stat"><div class="n">'+d.comp_count+'</div><div class="l">Comparables</div></div><div class="stat"><div class="n">'+d.segment_median.toLocaleString()+' AED</div><div class="l">Median</div></div></div></div>';

if(mode==='buy'&&ap){
var diff=ap-d.estimate;var dpct=((diff/d.estimate)*100).toFixed(1);var isOver=diff>0;
h+='<div class="card" style="border:2px solid '+(isOver?'var(--red)':'var(--green)')+'"><div style="text-align:center;padding:16px"><div style="font-size:1.5rem;font-weight:700;color:'+(isOver?'var(--red)':'var(--green)')+'">'+(isOver?'OVERPRICED':'GOOD DEAL')+'</div><div style="font-size:2rem;font-weight:800;color:'+(isOver?'var(--red)':'var(--green)')+'">'+(isOver?'+':'-')+Math.abs(dpct)+'%</div><div>You found: '+ap.toLocaleString()+' AED vs Market: '+d.estimate.toLocaleString()+' AED</div></div></div>';

var alts=d.comps.filter(function(x){return x.price_aed<ap;}).sort(function(a,b){return a.price_aed-b.price_aed;}).slice(0,4);
if(alts.length){h+='<div class="card" style="border:2px solid var(--gold)"><h3>Better Deals Online</h3>'+alts.map(function(x){return'<div class="alt-card"><div style="display:flex;justify-content:space-between"><div style="font-size:1.2rem;font-weight:700">'+x.price_aed.toLocaleString()+' AED</div><div style="background:var(--green-bg);color:var(--green);padding:3px 10px;border-radius:12px;font-size:0.72rem;font-weight:700">SAVE '+(ap-x.price_aed).toLocaleString()+' AED</div></div><div style="font-size:0.82rem;color:var(--muted);margin-top:4px">'+x.year+' &middot; '+(x.mileage_km?x.mileage_km.toLocaleString()+' km':'?')+' &middot; '+(x.spec||'?')+' &middot; '+x.city+'</div><div style="font-size:0.75rem;color:var(--gold-dark);margin-top:4px">'+x.found_on+'</div></div>';}).join('')+'</div>';}
}

h+='<div class="card"><h3>Similar Cars</h3>'+(d.comps||[]).map(function(x){return'<div class="comp-item"><div><div class="price">'+x.price_aed.toLocaleString()+' AED</div><div class="meta">'+x.year+' &middot; '+(x.mileage_km?x.mileage_km.toLocaleString()+' km':'?')+' &middot; '+(x.spec||'?')+'</div></div><div class="source">'+x.found_on+'</div></div>';}).join('')+'</div>';
c.innerHTML=h;
}

// Browse
var browseMake='';
async function loadBrowseMakes(){
var co=document.getElementById('browse-country').value;var url=API+'/models';if(co)url+='?country='+co;
var r=await fetch(url);var d=await r.json();
document.getElementById('browse-total').textContent=d.makes.length+' makes found';
document.getElementById('browse-makes-grid').innerHTML=d.makes.map(function(m){return'<div class="make-card" onclick="selectMake(''+m.make+'')"><div style="font-weight:600">'+m.make+'</div><div style="font-size:0.72rem;color:var(--muted)">'+m.model_count+' models, '+m.listing_count+' listings</div></div>';}).join('');
document.getElementById('browse-makes-card').style.display='block';document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';
}
async function selectMake(mk){browseMake=mk;
var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk);if(co)url+='?country='+co;
var r=await fetch(url);var d=await r.json();
document.getElementById('browse-make-title').textContent=mk;
document.getElementById('browse-models-list').innerHTML=d.models.map(function(m){return'<div class="row-link" onclick="selectModel(''+mk+'',''+m.model+'')"><div><div style="font-weight:600">'+m.model+'</div><div style="font-size:0.8rem;color:var(--muted)">'+m.year_range+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+m.listing_count+'</div></div>';}).join('');
document.getElementById('browse-makes-card').style.display='none';document.getElementById('browse-models-card').style.display='block';
}
async function selectModel(mk,md){
var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk)+'/'+encodeURIComponent(md);if(co)url+='?country='+co;
var r=await fetch(url);var d=await r.json();
document.getElementById('browse-model-title').textContent=mk+' '+md;
document.getElementById('browse-years-list').innerHTML=d.years.map(function(y){return'<div class="row-link"><div><div style="font-weight:600">'+y.year+'</div><div style="font-size:0.8rem;color:var(--muted)">'+(y.trims&&y.trims.length?y.trims.join(', '):'Standard')+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+y.listing_count+'</div></div>';}).join('');
document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='block';
}
function backToMakes(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-makes-card').style.display='block';}
function backToModels(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='block';}

// Market
async function loadMarketPage(){
try{var r=await fetch(API+'/admin/stats');var d=await r.json();document.getElementById('mkt-total').textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():'--');document.getElementById('mkt-active').textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():'--');document.getElementById('mkt-week').textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():'--');document.getElementById('mkt-all').textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():'--');}catch(e){}
try{var r2=await fetch(API+'/models');var d2=await r2.json();var top=d2.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);var max=top[0]?top[0].listing_count:1;document.getElementById('mkt-top-makes').innerHTML=top.map(function(m,i){return'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><span style="width:20px;color:var(--muted)">'+(i+1)+'</span><span style="flex:1">'+m.make+'</span><span style="color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</span><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';}).join('');}catch(e){}
}
