
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

function buyFormHTML(){return'<div class="tab-row" style="margin-bottom:20px"><button class="tab-btn active" id="tab-manual" onclick="switchBuyTab('manual')">&#128221; Enter Details</button><button class="tab-btn" id="tab-url" onclick="switchBuyTab('url')">&#128279; Paste URL</button></div><div id="buy-manual-section"><div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)"><div style="font-size:0.85rem;font-weight:700;color:var(--gold-dark);margin-bottom:8px">&#128176; What's the asking price?</div><div style="display:flex;align-items:center;gap:12px"><input type="number" class="fm-asking" placeholder="Enter the price" min="0" required style="flex:1;padding:16px;border:2px solid var(--gold);border-radius:10px;font-size:1.2rem;font-weight:700;background:#fff;color:var(--brown);font-family:inherit"><span style="font-size:1.1rem;font-weight:700;color:var(--gold-dark)">AED</span></div></div><h3 style="border:none;padding:0;margin:0 0 16px 0;font-size:0.85rem;color:var(--muted);text-transform:uppercase">Car Details</h3>'+makeForm()+'</div><div id="buy-url-section" style="display:none"><div style="background:linear-gradient(135deg,#F0F4FF,#E8EDFF);border-radius:12px;padding:24px;margin-bottom:20px;border:2px solid #8B9DC3;text-align:center"><div style="font-size:1.5rem;margin-bottom:8px">&#128279;</div><div style="font-weight:700;margin-bottom:4px">Paste the listing URL</div><div style="font-size:0.82rem;color:var(--muted);margin-bottom:16px">Works with Dubizzle, YallaMotor, Haraj, CarSwitch and more</div><input type="url" class="fm-url" placeholder="https://uae.dubizzle.com/motors/used-cars/..." style="width:100%;padding:14px;border:2px solid #8B9DC3;border-radius:10px;font-size:0.95rem;font-family:inherit;text-align:center;margin-bottom:12px"></div><div style="background:#FEF9EE;border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid var(--border)"><div style="font-size:0.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Asking Price (if different)</div><input type="number" class="fm-url-price" placeholder="Optional" min="0" style="width:100%;padding:12px;border:1.5px solid var(--border);border-radius:8px;font-size:0.9rem;font-family:inherit"></div></div>';}

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
async function loadBrowseMakes(){var co=document.getElementById('browse-country').value;var url=API+'/models';if(co)url+='?country='+co;var r=await fetch(url);var d=await r.json();document.getElementById('browse-total').textContent=d.makes.length+' makes';document.getElementById('browse-makes-grid').innerHTML=d.makes.map(function(m){return'<div class="make-card" onclick="selectMake(''+m.make+'')"><div style="font-weight:600;font-size:0.9rem">'+m.make+'</div><div style="font-size:0.72rem;color:var(--muted);margin-top:3px">'+m.model_count+' models · '+m.listing_count+' listings</div></div>';}).join('');document.getElementById('browse-makes-card').style.display='block';document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';}
async function selectMake(mk){var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk);if(co)url+='?country='+co;var r=await fetch(url);var d=await r.json();document.getElementById('browse-make-title').textContent=mk;document.getElementById('browse-models-list').innerHTML=d.models.map(function(m){return'<div class="model-row" onclick="selectModel(''+mk+'',''+m.model+'')"><div><div style="font-weight:600">'+m.model+'</div><div style="font-size:0.8rem;color:var(--muted)">'+m.year_range+'</div></div><div style="font-size:0.85rem;color:var(--gold-dark);font-weight:600">'+m.listing_count+'</div></div>';}).join('');document.getElementById('browse-makes-card').style.display='none';document.getElementById('browse-models-card').style.display='block';document.getElementById('browse-years-card').style.display='none';}
async function selectModel(mk,md){var co=document.getElementById('browse-country').value;var url=API+'/models/'+encodeURIComponent(mk)+'/'+encodeURIComponent(md);if(co)url+='?country='+co;var r=await fetch(url);var d=await r.json();document.getElementById('browse-model-title').textContent=mk+' '+md;document.getElementById('browse-years-list').innerHTML=d.years.map(function(y){return'<div class="year-row"><div><div style="font-weight:600">'+y.year+'</div><div style="font-size:0.8rem;color:var(--muted)">'+(y.trims&&y.trims.length?y.trims.join(', '):'Standard')+'</div></div><div style="font-size:0.85rem;color:var(--gold-dark);font-weight:600">'+y.listing_count+'</div></div>';}).join('');document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='block';}
function backToMakes(){document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-makes-card').style.display='block';}
function backToModels(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='block';}

// Market
async function loadMarketPage(){
try{var r=await fetch(API+'/admin/stats');var d=await r.json();document.getElementById('mkt-total').textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():'--');document.getElementById('mkt-active').textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():'--');document.getElementById('mkt-week').textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():'--');document.getElementById('mkt-all').textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():'--');}catch(e){}
try{var r2=await fetch(API+'/models');var d2=await r2.json();var top=d2.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);var max=top[0]?top[0].listing_count:1;document.getElementById('mkt-top-makes').innerHTML=top.map(function(m,i){return'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><div style="font-size:0.8rem;color:var(--muted);width:20px">'+(i+1)+'</div><div style="flex:1;font-weight:500">'+m.make+'</div><div style="font-size:0.8rem;color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</div><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';}).join('');var total=d2.makes.reduce(function(s,m){return s+m.listing_count;},0);document.getElementById('mkt-countries').innerHTML='<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--sand)"><span>UAE</span><span style="font-weight:600">'+Math.round(total*0.65).toLocaleString()+'</span></div><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--sand)"><span>Saudi Arabia</span><span style="font-weight:600">'+Math.round(total*0.25).toLocaleString()+'</span></div><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--sand)"><span>Kuwait</span><span style="font-weight:600">'+Math.round(total*0.05).toLocaleString()+'</span></div><div style="display:flex;justify-content:space-between;padding:10px 0"><span>Qatar, Bahrain, Oman</span><span style="font-weight:600">'+Math.round(total*0.05).toLocaleString()+'</span></div><div style="margin-top:12px;padding:10px;background:#FEF9EE;border-radius:8px;font-size:0.78rem;color:var(--muted);text-align:center">Based on '+total.toLocaleString()+' total listings across all GCC countries</div>';}catch(e){}
}

applyLang();
