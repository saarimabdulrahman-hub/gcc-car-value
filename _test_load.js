
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
document.getElementById('browse-makes-grid').innerHTML=d.makes.map(function(m){return'<div class="make-card" onclick="selectMake(''+m.make+'')"><div style="font-weight:600">'+m.make+'</div><div style="font-size:0.72rem;color:var(--muted)">'+m.model_count+' models, '+m.listing_count+' listings</div></div>';}).join('');
document.getElementById('browse-makes-card').style.display='block';document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';
}
async function selectMake(mk){bmake=mk;
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
function backToMakes(){document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-makes-card').style.display='block';}
function backToModels(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='block';}

// ---- Market ----
async function loadMarketPage(){
try{var r=await fetch(API+'/admin/stats');var d=await r.json();document.getElementById('mkt-total').textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():'--');document.getElementById('mkt-active').textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():'--');document.getElementById('mkt-week').textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():'--');document.getElementById('mkt-all').textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():'--');}catch(e){}
try{var r2=await fetch(API+'/models');var d2=await r2.json();var top=d2.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);var max=top[0]?top[0].listing_count:1;document.getElementById('mkt-top-makes').innerHTML=top.map(function(m,i){return'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><span style="width:20px;color:var(--muted)">'+(i+1)+'</span><span style="flex:1">'+m.make+'</span><span style="color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</span><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';}).join('');}catch(e){}
}
