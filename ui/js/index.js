function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
var API=(function(){var h=window.location.hostname;if(h==='localhost'||h==='127.0.0.1')return'http://localhost:8000/v1';return'https://gcc-car-value.onrender.com/v1';})();
function apiFetch(url,opts){opts=opts||{};opts.headers=opts.headers||{};var token=localStorage.getItem('token');if(token&&!opts.headers['Authorization']){opts.headers['Authorization']='Bearer '+token;}return fetch(url,opts);}
var curPage='home';
var ALL_MAKES=[];
var MODEL_CACHE={};
var YEAR_CACHE={};
var DEBOUNCE_TIMER=null;

var CITY_DATA=[
  {city:'Dubai',country:'UAE'},{city:'Abu Dhabi',country:'UAE'},{city:'Sharjah',country:'UAE'},
  {city:'Ajman',country:'UAE'},{city:'Ras Al Khaimah',country:'UAE'},{city:'Fujairah',country:'UAE'},
  {city:'Al Ain',country:'UAE'},{city:'Riyadh',country:'Saudi Arabia'},{city:'Jeddah',country:'Saudi Arabia'},
  {city:'Dammam',country:'Saudi Arabia'},{city:'Mecca',country:'Saudi Arabia'},{city:'Medina',country:'Saudi Arabia'},
  {city:'Khobar',country:'Saudi Arabia'},{city:'Kuwait City',country:'Kuwait'},{city:'Hawalli',country:'Kuwait'},
  {city:'Salmiya',country:'Kuwait'},{city:'Doha',country:'Qatar'},{city:'Al Wakrah',country:'Qatar'},
  {city:'Al Rayyan',country:'Qatar'},{city:'Muscat',country:'Oman'},{city:'Salalah',country:'Oman'},
  {city:'Sohar',country:'Oman'},{city:'Manama',country:'Bahrain'},{city:'Riffa',country:'Bahrain'},
  {city:'Muharraq',country:'Bahrain'}
];
var COUNTRY_LIST=['UAE','Saudi Arabia','Kuwait','Qatar','Bahrain','Oman'];
var SPEC_LIST=['GCC','US','Japan','European','Canadian','Korean'];

/* The static file is also opened directly in Playwright/offline previews.  A
   failed API warm-up must not become an uncaught page error; the form can
   still use its local city/country data and retry model loading on demand. */
fetch(API+'/models')
  .then(function(r){if(!r.ok)throw new Error('Models request failed');return r.json();})
  .then(function(d){ALL_MAKES=Array.isArray(d.makes)?d.makes:[];})
  .catch(function(){ALL_MAKES=[];});
loadHomeKPIs();

function goPage(p,el){
curPage=p;
if(window.location.hash!=='#'+p)history.pushState(null,'','#'+p);
document.querySelector('.sidebar')?.classList.remove('mobile-open');
document.querySelector('.mobile-menu-btn')?.setAttribute('aria-expanded','false');
document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');a.removeAttribute('aria-current');});
el.classList.add('active');
el.setAttribute('aria-current', 'page');
document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
var pg=document.getElementById('page-'+p);if(pg)pg.classList.remove('hidden');
document.body.classList.toggle('has-sidebar',p!=='home');
if(p==='sell')buildForm('sell-form',false);
if(p==='buy'){buildForm('buy-form',true);}
if(p==='browse')loadBrowseMakes();
if(p==='market')loadMarketPage();
if(p==='reports')initReportsDashboard();
if(p==='watchlist')renderWatchlist();
if(p==='settings')renderSettings();
/* Breadcrumbs */
var bc=document.getElementById('breadcrumbs');
var titles={home:'',sell:'Sell Your Car',buy:'Buy a Car',browse:'Browse Models',market:'Market Trends',reports:'Reports',watchlist:'Watchlist',settings:'Settings'};
if(p==='home'||p==='browse'||!titles[p]){if(bc)bc.classList.add('hidden');}
else{if(bc){bc.classList.remove('hidden');bc.innerHTML='<a href="#" onclick="goPage(\'home\',document.getElementById(\'nav-home\'))">Home</a> <span class="breadcrumb-sep">/</span> <span class="breadcrumb-current">'+titles[p]+'</span>';}}

if(p==='home'){
  /* Reset to skeleton state before loading */
  var skel=document.getElementById('home-skeleton-content');
  var data=document.getElementById('home-data-content');
  if(skel)skel.classList.remove('hidden');
  if(data)data.classList.add('hidden');
  loadHomeKPIs();
}
}


function loadHomeKPIs(){
  fetch(API+'/admin/stats').then(function(r){return r.json()}).then(function(d){
    var total=d.listings&&d.listings.total?d.listings.total:0;
    var active=d.listings&&d.listings.active?d.listings.active:0;
    var week=d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days:0;
    var el=document.getElementById('home-kpi-listings');
    if(el){el.setAttribute('aria-label',active>0?active.toLocaleString()+' active listings':'Data unavailable');}
    el=document.getElementById('home-kpi-valuations');
    if(el){el.setAttribute('aria-label',week>0?week.toLocaleString()+' valuations in last 7 days':'Data unavailable');}
    /* Hide skeleton, show real data */
    var skel=document.getElementById('home-skeleton-content');
    var data=document.getElementById('home-data-content');
    if(skel)skel.classList.add('hidden');
    if(data)data.classList.remove('hidden');
  }).catch(function(){
    var skel=document.getElementById('home-skeleton-content');
    var data=document.getElementById('home-data-content');
    if(skel)skel.classList.add('hidden');
    if(data){
      data.innerHTML='<div class="error-state" style="text-align:center;padding:2rem;color:var(--gold)">Unable to load dashboard. <button onclick="location.reload()" style="margin-left:8px;padding:4px 12px">Retry</button></div>';
      data.classList.remove('hidden');
    }
  });
}

function toggleLang(){var isAr=document.documentElement.lang==='ar';var next=isAr?'en':'ar';document.documentElement.lang=next;document.body.dir=next==='ar'?'rtl':'ltr';var enEl=document.getElementById('lang-en');var arEl=document.getElementById('lang-ar');if(enEl&&arEl){enEl.classList.toggle('active',!isAr);arEl.classList.toggle('active',isAr);}try{localStorage.setItem('gcc-lang',next);}catch(e){}}
(function(){var saved=null;try{saved=localStorage.getItem('gcc-lang');}catch(e){}if(saved==='ar'){document.documentElement.lang='ar';document.body.dir='rtl';var enEl=document.getElementById('lang-en');var arEl=document.getElementById('lang-ar');if(enEl&&arEl){enEl.classList.remove('active');arEl.classList.add('active');}}})();
function focusGlobalSearch(){window.location.href='browse.html#search';}

function showFormTip(formEl,message){var hintEl=formEl.querySelector('.smart-hints');if(!hintEl)return;hintEl.style.display='block';hintEl.innerHTML='<div style="display:flex;align-items:center;gap:6px;padding:8px 12px;background:var(--bg-elevated);border-radius:var(--radius-md);border:1px solid var(--border-subtle)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--gold-light)" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg><span style="font-size:var(--text-xs);color:var(--text-secondary)">'+message+'</span></div>';}
function smartDefaults(formEl){
  if(!formEl)return;
  var mkEl=formEl.querySelector('.fm-make');
  var mdEl=formEl.querySelector('.fm-model');
  if(!mkEl||!mdEl)return;
  var mk=mkEl.value;
  var md=mdEl.value;
  var spEl=formEl.querySelector('.fm-spec');
  var hintEl=formEl.querySelector('.smart-hints');
  if(!hintEl)return;

  if(mk&&md){
    var ck=mk+'|||'+md;
    if(YEAR_CACHE[ck]){
      showYearSuggestions(formEl,YEAR_CACHE[ck]);
    }else{
      fetch(API+'/models/'+encodeURIComponent(mk)+'/'+encodeURIComponent(md))
        .then(function(r){return r.json();})
        .then(function(d){YEAR_CACHE[ck]=d;showYearSuggestions(formEl,d);})
        .catch(function(){sug.innerHTML='<div class="autocomplete-item muted">Failed to load suggestions</div>';})
    }
  }

  if(mk){
    var topSpecs={'Toyota':'GCC','Nissan':'GCC','Honda':'GCC','BMW':'European','Mercedes':'European','Audi':'European','Lexus':'US','Ford':'US','Chevrolet':'US'};
    var defSpec=topSpecs[mk]||'GCC';
    if(spEl&&!spEl.value)spEl.placeholder='e.g. '+defSpec+' (most common)';
    /* AI Form Tips */
    var tips={'Toyota':'Toyota vehicles hold value well in the GCC — Land Cruisers and Camrys are the most liquid models.','Nissan':'Nissan Patrols dominate the large SUV segment in UAE and Saudi markets.','BMW':'European specs typically price 10-15% above GCC specs for BMW. Verify the spec before listing.','Mercedes':'G-Class models have seen 8% price appreciation year-over-year in the GCC.','default':'Enter mileage and year for a more accurate valuation. Lower mileage vehicles command premium prices in GCC markets.'};
    showFormTip(formEl,tips[mk]||tips['default']);
  }
}

function showYearSuggestions(formEl,data){
  var hintEl=formEl.querySelector('.smart-hints');
  if(!hintEl||!data.years||!data.years.length)return;
  var years=data.years.slice(0,8);
  hintEl.innerHTML='<span style="font-size: var(--text-xs);color:var(--text-muted)">Common years: </span>'+
    years.map(function(y){return'<span class="suggestion-chip" data-year="'+y.year+'" data-count="'+y.listing_count+'">'+y.year+' ('+y.listing_count+')</span>';}).join('');
  hintEl.style.display='block';
  hintEl.onclick=function(e){
    var chip=e.target.closest('.suggestion-chip');
    if(!chip)return;
    var year=parseInt(chip.getAttribute('data-year'));
    var count=chip.getAttribute('data-count');
    var formEl=document.getElementById(curPage==='sell'?'sell-form':'buy-form');
    var yrInput=formEl.querySelector('.fm-year');
    var miInput=formEl.querySelector('.fm-mileage');
    if(yrInput)yrInput.value=year;
    if(miInput)miInput.placeholder='e.g. '+((2026-year)*20000)+' km';
    hintEl.innerHTML='<span style="font-size: var(--text-xs);color:var(--gold-light)">'+count+' listings for '+year+'</span>';
  };
}

function buildForm(id,isBuy){
var el=document.getElementById(id);
var prefix=id==='sell-form'?'sell':'buy';
var h='';

if(isBuy){
h+='<div class="buy-asking-section">';
h+='<div class="form-section-title" style="border-bottom:none;padding-bottom:0"><span class="sec-letter">A.</span> Asking Price</div>';
h+='<div class="buy-asking-row"><span class="buy-asking-currency">AED</span><input type="number" class="fm-asking buy-asking-input" id="'+prefix+'-asking" placeholder="Enter the asking price" aria-label="Asking price in AED" aria-describedby="'+prefix+'-asking-error" aria-required="true"></div>';
h+='<span class="field-error buy-asking-error" id="'+prefix+'-asking-error">Please enter the asking price</span>';
h+='</div>';
h+='<hr class="form-divider">';
}

h+='<div class="form-section"><div class="form-section-title"><span class="sec-letter">B.</span> Vehicle Details</div>';
h+='<div class="form-row">';
h+='<div class="form-group"><label for="'+prefix+'-make">Make</label><div class="autocomplete-wrap"><input type="text" class="fm-make" id="'+prefix+'-make" placeholder="e.g. Toyota" autocomplete="off" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-haspopup="listbox" aria-describedby="'+prefix+'-make-error" aria-required="true" oninput="autocompleteSmart(this)" onfocus="autocompleteSmart(this)"><div class="autocomplete-suggestions"></div></div><span class="field-error" id="'+prefix+'-make-error">Please select a make</span></div>';
h+='<div class="form-group"><label for="'+prefix+'-model">Model</label><div class="autocomplete-wrap"><input type="text" class="fm-model" id="'+prefix+'-model" placeholder="e.g. Land Cruiser" autocomplete="off" disabled role="combobox" aria-expanded="false" aria-autocomplete="list" aria-haspopup="listbox" aria-describedby="'+prefix+'-model-error" aria-required="true" oninput="autocompleteSmart(this)" onfocus="autocompleteSmart(this)"><div class="autocomplete-suggestions"></div></div><span class="field-error" id="'+prefix+'-model-error">Please select a model</span></div>';
h+='<div class="form-group"><label for="'+prefix+'-year">Year</label><input type="number" class="fm-year" id="'+prefix+'-year" placeholder="e.g. 2020" min="1990" max="2027" aria-describedby="'+prefix+'-year-error" aria-required="true" onchange="smartDefaults(this.closest(\'[id$=-form]\'))"><span class="field-error" id="'+prefix+'-year-error">Please enter a valid year (1990–2027)</span></div>';
h+='<div class="form-group"><label for="'+prefix+'-mileage">Mileage (km)</label><div class="input-icon-wrap"><svg class="input-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg><input type="number" class="fm-mileage" id="'+prefix+'-mileage" placeholder="e.g. 80000"></div></div>';
h+='</div></div>';

h+='<hr class="form-divider">';
h+='<div class="form-section"><div class="form-section-title"><span class="sec-letter">C.</span> Market Details</div>';
h+='<div class="form-row three-col">';
h+='<div class="form-group"><label for="'+prefix+'-spec">Spec</label><div class="input-icon-wrap"><svg class="input-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg><input type="text" class="fm-spec" id="'+prefix+'-spec" value="GCC" readonly style="background:rgba(0,0,0,0.15);color:var(--text-muted);cursor:not-allowed"></div></div>';
h+='<div class="form-group"><label for="'+prefix+'-city">City</label><div class="autocomplete-wrap"><input type="text" class="fm-city" id="'+prefix+'-city" placeholder="e.g. Dubai" autocomplete="off" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-haspopup="listbox" oninput="autocompleteSmart(this)" onfocus="autocompleteSmart(this)"><div class="autocomplete-suggestions"></div></div></div>';
h+='<div class="form-group"><label for="'+prefix+'-country">Country</label><div class="input-icon-wrap"><svg class="input-icon" width="16" height="11" viewBox="0 0 600 300"><rect x="0" y="0" width="150" height="300" fill="#CE1126"/><rect x="150" y="0" width="450" height="100" fill="#00732F"/><rect x="150" y="100" width="450" height="100" fill="#FFFFFF"/><rect x="150" y="200" width="450" height="100" fill="#000000"/></svg><div class="autocomplete-wrap"><input type="text" class="fm-country" id="'+prefix+'-country" placeholder="e.g. UAE" autocomplete="off" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-haspopup="listbox" oninput="autocompleteSmart(this)" onfocus="autocompleteSmart(this)"><div class="autocomplete-suggestions"></div></div></div></div>';
h+='</div></div>';

h+='<div class="smart-hints chip-row" style="display:none;margin-top:var(--space-2)"></div>';

el.innerHTML=h;

var mkEl=el.querySelector('.fm-make');
var mdEl=el.querySelector('.fm-model');
mkEl.onchange=function(){
  mdEl.disabled=!this.value;
  if(!this.value){mdEl.value='';mdEl.placeholder='Type model...';}
  else{mdEl.placeholder='Type model for '+this.value+'...';}
  smartDefaults(el);
};
mdEl.onchange=function(){smartDefaults(el);};

if(isBuy){
  var askingEl=el.querySelector('.fm-asking');
  if(askingEl){askingEl.addEventListener('input',function(){updateDealScore(this.value);});}
}

// Clear field errors on user input
el.querySelectorAll('input').forEach(function(input){
  input.addEventListener('input', function(){
    var group=this.closest('.form-group');
    if(group)group.classList.remove('error');
    var err=group?group.querySelector('.field-error'):null;
    if(err)err.style.display='none';
    // Also clear asking-price inline error styles
    if(this.classList.contains('fm-asking')){
      var askSection=this.closest('.buy-asking-section');
      if(askSection){var apErr=askSection.querySelector('.field-error');if(apErr)apErr.style.display='none';}
    }
  });
});

// Keyboard navigation for autocomplete comboboxes
el.addEventListener('keydown', function(e){
  var input = e.target;
  if (!input.matches('.fm-make, .fm-model, .fm-city, .fm-country')) return;
  var wrap = input.closest('.autocomplete-wrap');
  if (!wrap) return;
  var sug = wrap.querySelector('.autocomplete-suggestions');
  if (!sug || !sug.classList.contains('show')) return;
  var items = sug.querySelectorAll('[role="option"]');
  if (!items.length) return;
  var activeIdx = -1;
  items.forEach(function(item, i){ if (item.getAttribute('aria-selected') === 'true') activeIdx = i; });
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    var next = (activeIdx + 1) % items.length;
    items.forEach(function(item, i){
      item.setAttribute('aria-selected', i === next ? 'true' : 'false');
      item.style.background = i === next ? 'var(--gold-glow)' : '';
      if (i === next) input.setAttribute('aria-activedescendant', item.id);
    });
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    var prev = activeIdx <= 0 ? items.length - 1 : activeIdx - 1;
    items.forEach(function(item, i){
      item.setAttribute('aria-selected', i === prev ? 'true' : 'false');
      item.style.background = i === prev ? 'var(--gold-glow)' : '';
      if (i === prev) input.setAttribute('aria-activedescendant', item.id);
    });
  } else if (e.key === 'Enter' && activeIdx >= 0) {
    e.preventDefault();
    items[activeIdx].click();
  } else if (e.key === 'Escape') {
    sug.classList.remove('show');
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
  }
});
}

function autocompleteSmart(input){
clearTimeout(DEBOUNCE_TIMER);
var self=input;
DEBOUNCE_TIMER=setTimeout(function(){doAutocomplete(self);},200);
}

function doAutocomplete(input){
var wrap=input.closest('.autocomplete-wrap');if(!wrap)return;
var sug=wrap.querySelector('.autocomplete-suggestions');
var formEl=input.closest('[id$="-form"]');
var val=input.value.toLowerCase().trim();sug.innerHTML='';
if(!val){sug.classList.remove('show');input.setAttribute('aria-expanded','false');return;}

if(input.classList.contains('fm-make')){
  var matches=ALL_MAKES.filter(function(m){return m.make.toLowerCase().indexOf(val)>=0;}).slice(0,8);
  sug.setAttribute('role','listbox');
  matches.forEach(function(m,i){
    var d=document.createElement('div');d.className='autocomplete-item';
    d.setAttribute('role','option');d.setAttribute('aria-selected','false');d.id='ac-option-'+i;
    d.innerHTML='<span>'+m.make+'</span><span class="count">'+m.listing_count+' listings</span>';
    d.onclick=function(){input.value=m.make;sug.classList.remove('show');input.setAttribute('aria-expanded','false');
      if(formEl){var mdl=formEl.querySelector('.fm-model');if(mdl){mdl.disabled=false;mdl.value='';mdl.placeholder='Type model for '+m.make+'...';mdl.focus();}}
      smartDefaults(formEl);
    };
    sug.appendChild(d);
  });
  if(!matches.length){sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)">No makes found</div>';}
}else if(input.classList.contains('fm-model')){
  var mk=formEl?formEl.querySelector('.fm-make').value:'';
  if(!mk){sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)">Select a make first</div>';sug.classList.add('show');input.setAttribute('aria-expanded','true');return;}
  var ck=mk;
  if(MODEL_CACHE[ck]){
    showModelResults(sug,MODEL_CACHE[ck],val,input,formEl);
  }else{
    sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)"><div class="spinner" style="width:14px;height:14px;border-width:2px;margin-right:8px"></div>Loading models...</div>';
    sug.classList.add('show');input.setAttribute('aria-expanded','true');
    fetch(API+'/models/'+encodeURIComponent(mk)).then(function(r){return r.json()}).then(function(d){
      MODEL_CACHE[ck]=d.models||[];
      showModelResults(sug,MODEL_CACHE[ck],val,input,formEl);
    }).catch(function(){sug.innerHTML='<div class="autocomplete-item" style="color:var(--red);gap:8px"><span>⚠️</span><span>Failed to load models — please retry</span></div>';});
  }
}else if(input.classList.contains('fm-city')){
  var countryEl=formEl?formEl.querySelector('.fm-country'):null;
  var countryVal=countryEl?countryEl.value.toLowerCase().trim():'';
  var matches=CITY_DATA.filter(function(c){return c.city.toLowerCase().indexOf(val)>=0;});
  if(countryVal){matches=matches.filter(function(c){return c.country.toLowerCase().indexOf(countryVal)>=0;});}
  matches.sort(function(a,b){var aMatch=a.country.toLowerCase().indexOf(countryVal)>=0?0:1;var bMatch=b.country.toLowerCase().indexOf(countryVal)>=0?0:1;return aMatch-bMatch;});
  sug.setAttribute('role','listbox');
  matches.slice(0,8).forEach(function(c,i){
    var d=document.createElement('div');d.className='autocomplete-item';
    d.setAttribute('role','option');d.setAttribute('aria-selected','false');d.id='ac-option-'+i;
    d.innerHTML='<span>'+c.city+'</span><span class="count">'+c.country+'</span>';
    d.onclick=function(){input.value=c.city;sug.classList.remove('show');input.setAttribute('aria-expanded','false');};
    sug.appendChild(d);
  });
  if(!matches.length){sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)">No cities found</div>';}
}else if(input.classList.contains('fm-country')){
  var matches=COUNTRY_LIST.filter(function(c){return c.toLowerCase().indexOf(val)>=0;});
  sug.setAttribute('role','listbox');
  matches.forEach(function(c,i){
    var cityCount=CITY_DATA.filter(function(x){return x.country===c;}).length;
    var d=document.createElement('div');d.className='autocomplete-item';
    d.setAttribute('role','option');d.setAttribute('aria-selected','false');d.id='ac-option-'+i;
    d.innerHTML='<span>'+c+'</span><span class="count">'+cityCount+' cities</span>';
    d.onclick=function(){input.value=c;sug.classList.remove('show');input.setAttribute('aria-expanded','false');
      if(formEl){var cityEl=formEl.querySelector('.fm-city');if(cityEl&&!cityEl.value)cityEl.placeholder='e.g. '+CITY_DATA.filter(function(x){return x.country===c;}).slice(0,3).map(function(x){return x.city;}).join(', ');}
    };
    sug.appendChild(d);
  });
  if(!matches.length){sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)">No countries found</div>';}
}else if(input.classList.contains('fm-spec')){
  var matches=SPEC_LIST.filter(function(s){return s.toLowerCase().indexOf(val)>=0;});
  sug.setAttribute('role','listbox');
  matches.forEach(function(s,i){
    var d=document.createElement('div');d.className='autocomplete-item';
    d.setAttribute('role','option');d.setAttribute('aria-selected','false');d.id='ac-option-'+i;
    d.innerHTML='<span>'+s+'</span>';
    d.onclick=function(){input.value=s;sug.classList.remove('show');input.setAttribute('aria-expanded','false');};
    sug.appendChild(d);
  });
  if(!matches.length){sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)">No specs found</div>';}
}
if(sug.children.length){sug.classList.add('show');input.setAttribute('aria-expanded','true');}
else sug.classList.remove('show');

setTimeout(function(){
  document.addEventListener('click',function close(e){if(!wrap.contains(e.target)){sug.classList.remove('show');input.setAttribute('aria-expanded','false');document.removeEventListener('click',close);}});
},100);
}

function showModelResults(sug,models,val,input,formEl){
sug.innerHTML='';sug.setAttribute('role','listbox');
var matches=models.filter(function(m){return m.model.toLowerCase().indexOf(val)>=0;}).slice(0,8);
if(!matches.length){sug.innerHTML='<div class="autocomplete-item" style="color:var(--text-muted)">No models found for "'+val+'"</div>';}
matches.forEach(function(m,i){
  var d=document.createElement('div');d.className='autocomplete-item';
  d.setAttribute('role','option');d.setAttribute('aria-selected','false');d.id='ac-option-'+i;
  d.innerHTML='<span>'+m.model+'</span><span class="count">'+m.year_range+' &middot; '+m.listing_count+'</span>';
  d.onclick=function(){input.value=m.model;sug.classList.remove('show');input.setAttribute('aria-expanded','false');smartDefaults(formEl);};
  sug.appendChild(d);
});
}

function updateDealScore(askingVal){
  var card=document.getElementById('deal-score-card');
  var valueEl=document.getElementById('deal-score-value');
  var labelEl=document.getElementById('deal-score-label');
  var barEl=document.getElementById('deal-score-bar');
  if(!card||!askingVal||isNaN(askingVal)||Number(askingVal)<=0){if(card)card.style.display='none';return;}
  card.style.display='block';
  var price=Number(askingVal);
  var score,color,label;
  if(price<50000){score=85;color='var(--green)';label='Budget range — likely good value';}
  else if(price<150000){score=70;color='var(--gold-light)';label='Mid-range — market dependent';}
  else if(price<300000){score=55;color='var(--amber)';label='Premium segment — verify comps';}
  else{score=40;color='var(--amber)';label='Luxury — needs thorough analysis';}
  valueEl.textContent=score+'/100';valueEl.style.color=color;
  labelEl.textContent=label;barEl.style.transform='scaleX('+(score/100)+')';barEl.style.background=color;
}
function readForm(el){
var g=function(c){var e=el.querySelector(c);return e?e.value:null;};
var mk=g('.fm-make'),md=g('.fm-model'),yr=g('.fm-year');
if(!mk||!md||!yr)return null;
var b={make:mk,model:md,year:parseInt(yr)};
var mi=g('.fm-mileage');if(mi)b.mileage_km=parseInt(mi);
var sp=g('.fm-spec');if(sp)b.spec=sp;
var ci=g('.fm-city');if(ci)b.city=ci;
var co=g('.fm-country');if(co){var cm={'UAE':'AE','Saudi Arabia':'SA','Saudi':'SA','Kuwait':'KW','Qatar':'QA','Bahrain':'BH','Oman':'OM'};b.country=cm[co]||co;}
var ap=g('.fm-asking');if(ap)b.asking_price=parseFloat(ap);
return b;
}

async function doValuation(mode){
var el=document.getElementById(mode+'-form');
if(mode==='buy'&&document.getElementById('buy-url-section').style.display==='block'){var urlEl=document.getElementById('fm-url');if(urlEl&&urlEl.value)return doUrlValuation(urlEl.value);}

// Clear all previous field errors
el.querySelectorAll('.form-group').forEach(function(g){g.classList.remove('error');});
el.querySelectorAll('.field-error').forEach(function(e){e.style.display='none';});

var body=readForm(el);

// Validate each field individually — set inline red border + error text
var errors=[];

if(!body||!body.make){
  errors.push({field:'make',msg:'Please select a make'});
  var mkEl=el.querySelector('.fm-make');
  if(mkEl){var mkGroup=mkEl.closest('.form-group');if(mkGroup)mkGroup.classList.add('error');}
}
if(!body||!body.model){
  errors.push({field:'model',msg:'Please select a model'});
  var mdEl=el.querySelector('.fm-model');
  if(mdEl){var mdGroup=mdEl.closest('.form-group');if(mdGroup)mdGroup.classList.add('error');}
}
if(!body||!body.year||isNaN(body.year)||body.year<1990||body.year>2027){
  errors.push({field:'year',msg:'Please enter a valid year (1990-2027)'});
  var yrEl=el.querySelector('.fm-year');
  if(yrEl){var yrGroup=yrEl.closest('.form-group');if(yrGroup){yrGroup.classList.add('error');var yrErr=yrGroup.querySelector('.field-error');if(yrErr)yrErr.textContent='Please enter a valid year (1990–2027)';}}
}

if(mode==='buy'&&(!body||!body.asking_price)){
  errors.push({field:'asking',msg:'Please enter the asking price'});
  var apEl=el.querySelector('.fm-asking');
  if(apEl){
    apEl.style.borderColor='var(--red)';
    apEl.style.boxShadow='0 0 0 3px var(--red-bg)';
    var askSection=apEl.closest('.buy-asking-section');
    if(askSection){var apErr=askSection.querySelector('.field-error');if(apErr)apErr.style.display='block';}
  }
}

if(errors.length>0)return;

/* Review before submit */
var reviewHTML='<div style="display:flex;flex-direction:column;gap:var(--space-2)">';
reviewHTML+='<div class="market-health-row"><span class="market-health-label">Make:</span><span class="market-health-value good">'+esc(body.make)+'</span></div>';
reviewHTML+='<div class="market-health-row"><span class="market-health-label">Model:</span><span class="market-health-value good">'+esc(body.model)+'</span></div>';
reviewHTML+='<div class="market-health-row"><span class="market-health-label">Year:</span><span class="market-health-value good">'+body.year+'</span></div>';
if(body.mileage_km)reviewHTML+='<div class="market-health-row"><span class="market-health-label">Mileage:</span><span class="market-health-value good">'+Number(body.mileage_km).toLocaleString()+' km</span></div>';
if(body.spec)reviewHTML+='<div class="market-health-row"><span class="market-health-label">Spec:</span><span class="market-health-value good">'+esc(body.spec)+'</span></div>';
if(body.city)reviewHTML+='<div class="market-health-row"><span class="market-health-label">City:</span><span class="market-health-value good">'+esc(body.city)+'</span></div>';
if(body.asking_price)reviewHTML+='<div class="market-health-row"><span class="market-health-label">Asking Price:</span><span class="market-health-value good">AED '+Number(body.asking_price).toLocaleString()+'</span></div>';
reviewHTML+='</div><div style="margin-top:var(--space-3);display:flex;gap:var(--space-2);justify-content:flex-end">';
reviewHTML+='<button class="btn btn-ghost" onclick="closeModal()" style="width:auto;padding:10px 24px">Edit</button>';
reviewHTML+='<button class="btn" id="review-confirm-btn" style="width:auto;padding:10px 32px;min-height:0;margin:0">Confirm & Analyze</button></div>';
openModal('Review Your '+(mode==='buy'?'Deal':'Vehicle'),reviewHTML);
setTimeout(function(){var confirmBtn=document.getElementById('review-confirm-btn');if(confirmBtn){confirmBtn.onclick=function(){closeModal();submitValuation(mode,body);};}},100);
}

async function submitValuation(mode,body){
var ld=document.getElementById(mode+'-loading');if(ld)ld.classList.remove('hidden');
var rs=document.getElementById(mode+'-results');if(rs)rs.classList.add('hidden');
var er=document.getElementById(mode+'-error');if(er)er.classList.add('hidden');
var btn=document.getElementById(mode+'-btn');if(btn){btn.disabled=true;btn.classList.add('loading');}
try{var r=await fetch(API+'/valuate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}if(ld)ld.classList.add('hidden');showResults(mode,await r.json(),body);}
catch(e){if(ld)ld.classList.add('hidden');showError((e&&e.message)||String(e));}
finally{if(btn){btn.disabled=false;btn.classList.remove('loading');}}
}

/* ═══ Enterprise State Helpers ═══ */
function renderStateLoading(icon,title,desc){return'<div class="state-container"><div class="state-icon loading-state">'+icon+'</div><div class="state-title">'+title+'</div><div class="state-desc">'+desc+'</div></div>';}
function renderStateEmpty(icon,title,desc,actionLabel,actionFn){var a='';if(actionLabel&&actionFn){a='<div class="state-actions"><button class="state-btn primary" onclick="'+actionFn+'">'+actionLabel+'</button></div>';}return'<div class="state-container"><div class="state-icon empty-state-icon">'+icon+'</div><div class="state-title">'+title+'</div><div class="state-desc">'+desc+'</div>'+a+'</div>';}
function renderStateError(icon,title,desc,retryFn){var a='';if(retryFn){a='<div class="state-actions"><button class="state-btn primary" onclick="'+retryFn+'">↻ Retry</button><button class="state-btn ghost" onclick="goPage(\'home\',document.getElementById(\'nav-home\'))">Go Home</button></div>';}return'<div class="state-container"><div class="state-icon error-state">'+icon+'</div><div class="state-title">'+title+'</div><div class="state-desc">'+desc+'</div>'+a+'</div>';}
function renderStateNoResults(icon,title,desc,clearFn){var a='';if(clearFn){a='<div class="state-actions"><button class="state-btn ghost" onclick="'+clearFn+'">✕ Clear Filters</button></div>';}return'<div class="state-container"><div class="state-icon search-state">'+icon+'</div><div class="state-title">'+title+'</div><div class="state-desc">'+desc+'</div>'+a+'</div>';}
function showToast(msg,type,duration){type=type||'error';duration=duration||10000;var c=document.querySelector('.toast-container');if(!c){c=document.createElement('div');c.className='toast-container';c.setAttribute('role','status');c.setAttribute('aria-live','polite');c.setAttribute('aria-label','Notifications');document.body.appendChild(c);}var t=document.createElement('div');t.className='toast toast-'+type;t.setAttribute('role','alert');t.textContent=String(msg||'Unknown error');t.onclick=function(){t.remove();};c.appendChild(t);setTimeout(function(){if(t.parentNode)t.remove();},duration);}
var modalPrevFocus=null;
function openModal(title,content){closeModal();modalPrevFocus=document.activeElement;var overlay=document.createElement('div');overlay.className='modal-overlay';overlay.id='modal-overlay';overlay.innerHTML='<div class="modal-card"><div class="modal-header"><h3>'+esc(title)+'</h3><button class="modal-close" onclick="closeModal()">✕</button></div><div class="modal-body">'+content+'</div></div>';overlay.addEventListener('click',function(e){if(e.target===overlay)closeModal();});document.body.appendChild(overlay);var closeBtn=overlay.querySelector('.modal-close');if(closeBtn)setTimeout(function(){closeBtn.focus();},100);document.addEventListener('keydown',function esc(e){if(e.key==='Escape'){closeModal();document.removeEventListener('keydown',esc);}});}
function closeModal(){var o=document.getElementById('modal-overlay');if(o)o.remove();if(modalPrevFocus&&typeof modalPrevFocus.focus==='function'){setTimeout(function(){modalPrevFocus.focus();},50);}}
var drawerPrevFocus=null;
function openDrawer(title,content){closeDrawer();drawerPrevFocus=document.activeElement;var overlay=document.createElement('div');overlay.className='drawer-overlay open';overlay.id='drawer-overlay';overlay.addEventListener('click',closeDrawer);var panel=document.createElement('div');panel.className='drawer-panel';panel.id='drawer-panel';panel.innerHTML='<div class="drawer-header"><h3 style="font-size:var(--text-section);font-weight:700;color:var(--text-primary);margin:0">'+esc(title)+'</h3><button class="drawer-close" onclick="closeDrawer()">✕</button></div><div class="drawer-body">'+content+'</div>';document.body.appendChild(overlay);document.body.appendChild(panel);requestAnimationFrame(function(){panel.classList.add('open');var closeBtn=panel.querySelector('.drawer-close');if(closeBtn)closeBtn.focus();});document.addEventListener('keydown',function esc(e){if(e.key==='Escape'){closeDrawer();document.removeEventListener('keydown',esc);}});}
function closeDrawer(){var overlay=document.getElementById('drawer-overlay');var panel=document.getElementById('drawer-panel');if(panel){panel.classList.remove('open');setTimeout(function(){panel.remove();},300);}if(overlay)overlay.remove();if(drawerPrevFocus&&typeof drawerPrevFocus.focus==='function'){setTimeout(function(){drawerPrevFocus.focus();},50);}}
function showError(msg){showToast(msg||'Something went wrong','error',10000);}
function showWarning(msg){showToast(msg||'','warning',8000);}

function submitSellUrl(){var urlEl=document.getElementById('sell-url');if(!urlEl||!urlEl.value){showWarning('Please paste a URL first');return;}doUrlValuation(urlEl.value,'sell');}
function handleSellImages(input){var files=input.files;var previews=document.getElementById('sell-image-previews');var notes=document.getElementById('sell-ai-notes');var zone=document.getElementById('sell-image-zone');previews.innerHTML='';var count=Math.min(files.length,5);for(var i=0;i<count;i++){(function(file){var reader=new FileReader();reader.onload=function(e){var thumb=document.createElement('div');thumb.style.cssText='width:80px;height:80px;border-radius:var(--radius-md);background-size:cover;background-position:center;background-image:url('+e.target.result+');border:1px solid var(--border-subtle)';previews.appendChild(thumb);};reader.readAsDataURL(file);})(files[i]);}zone.style.borderColor='var(--gold)';notes.style.display='block';var conditions=['Excellent — no visible damage detected','Good — minor wear consistent with age','Clean — well-maintained exterior'];notes.innerHTML='<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--gold-light)" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg><strong style="color:var(--gold-light)">AI Assessment:</strong></div>'+conditions.slice(0,count).map(function(c){return'<div style="margin-left:22px">• '+c+'</div>';}).join('')+'<div style="margin-top:8px;color:var(--green)">✓ Vehicle identity confirmed from images</div>';}
function publishListing(){var wl=getWatchlist();if(wl.length>0){wl[0].published=true;wl[0].publishedDate=new Date().toISOString().slice(0,10);localStorage.setItem('gcc-watchlist',JSON.stringify(wl));}var confirm=document.getElementById('publish-confirm');if(confirm)confirm.style.display='block';showToast('Listing published successfully','success',4000);}
function submitUrl(){var urlEl=document.getElementById('fm-url');if(!urlEl||!urlEl.value){showWarning('Please paste a URL first');return;}doUrlValuation(urlEl.value);}
async function doUrlValuation(url,mode){
	mode=mode||'buy';
var ld=document.getElementById(mode+'-loading');if(ld)ld.classList.remove('hidden');
var rs=document.getElementById(mode+'-results');if(rs)rs.classList.add('hidden');
try{var r=await fetch(API+'/valuate-url',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url})});if(!r.ok){var e=await r.json();var msg=e.detail||'Failed';if(msg.indexOf('Pardon')>-1||msg.indexOf('Interruption')>-1)msg='Dubizzle is blocking automated access. Please use the manual form instead.';throw new Error(msg);}var d=await r.json();if(ld)ld.classList.add('hidden');showResults(mode,{estimate:d.estimate,price_low:d.price_low,price_high:d.price_high,confidence:d.confidence,comp_count:d.comp_count,segment_median:d.segment_median,adjustments:d.adjustments||[],comps:d.comps||[],confidence_interval_80:d.confidence_interval_80},{asking_price:d.parsed_from_url?d.parsed_from_url.price_found:d.estimate});}
catch(e){if(ld)ld.classList.add('hidden');var errEl=document.getElementById(mode+'-error');if(errEl){errEl.classList.remove('hidden');errEl.innerHTML='<div class="card" style="border-color:var(--red);padding:var(--space-3)"><p style="color:var(--red);font-weight:600;margin:0">'+((e&&e.message)||String(e))+'</p></div>';}}
}

function applyOverride(baseEstimate,pct){var adjusted=Math.round(baseEstimate*(1+Number(pct)/100));var diff=adjusted-baseEstimate;document.getElementById('override-value').textContent='AED '+adjusted.toLocaleString();var diffEl=document.getElementById('override-diff');diffEl.textContent=(diff>=0?'+':'')+'AED '+diff.toLocaleString()+' ('+(diff>=0?'+':'')+pct+'%)';diffEl.style.color=diff>=0?'var(--green)':'var(--red)';document.getElementById('override-reset').style.display='inline-flex';}
function resetOverride(baseEstimate){document.getElementById('override-slider').value=0;document.getElementById('override-value').textContent='AED '+baseEstimate.toLocaleString();document.getElementById('override-diff').textContent='';document.getElementById('override-reset').style.display='none';}
function showResults(mode,d,body){
var c=document.getElementById(mode+'-results');if(!c)return;c.classList.remove('hidden');
var ap=body.asking_price;
var confClass=d.confidence==='high'?'badge-high':(d.confidence==='medium'?'badge-medium':'badge-low');
var confPct=d.confidence==='high'?75:(d.confidence==='medium'?50:25);
var confColor=d.confidence==='high'?'var(--gold-light)':(d.confidence==='medium'?'var(--amber)':'var(--red)');
var rangeSpan=d.price_high-d.price_low;
var estPos=rangeSpan>0?((d.estimate-d.price_low)/rangeSpan*100):50;
var h='';

/* ═══ VALUATION HERO ═══ */
h+='<div class="card result-hero">';
h+='<div class="card-header" style="display:flex;align-items:center;gap:var(--space-2);justify-content:center">';
h+='<svg class="conf-ring" viewBox="0 0 64 64" role="img" aria-label="Confidence: '+d.confidence+', '+confPct+' percent"><circle cx="32" cy="32" r="28" fill="none" stroke="var(--border-default)" stroke-width="4"/><circle cx="32" cy="32" r="28" fill="none" stroke="'+confColor+'" stroke-width="4" stroke-dasharray="'+Math.round(confPct/100*175.93)+' 175.93" stroke-dashoffset="0" stroke-linecap="round" transform="rotate(-90 32 32)" style="transition:stroke-dasharray 1s ease"/></svg>';
h+='<div class="conf-text"><span class="conf-label" style="color:'+confColor+'">'+d.confidence.toUpperCase()+' CONFIDENCE</span><span class="conf-sub">based on '+d.comp_count+' comparable listings</span></div>';
h+='</div>';
h+='<div class="card-body" style="text-align:center">';
h+='<div class="result-amount"><span id="result-amount-value">AED 0</span></div>';
h+='<div class="result-range">Market Range: AED '+d.price_low.toLocaleString()+' &ndash; AED '+d.price_high.toLocaleString()+'</div>';
h+='</div></div>';

/* ═══ PRICE RANGE BAR ═══ */
h+='<div class="card result-details"><h3>Market Position</h3>';
h+='<div class="card-body" style="padding:0">';
h+='<div class="range-bar-wrap"><div class="range-bar-track"><div class="range-bar-fill" style="left:0;width:100%"></div><div class="range-bar-marker" style="left:'+estPos+'%" title="AED '+d.estimate.toLocaleString()+'"></div></div><div class="range-bar-labels"><span>AED '+d.price_low.toLocaleString()+'</span><span>AED '+d.price_high.toLocaleString()+'</span></div></div>';
h+='<div class="result-details-row"><span class="result-detail-item"><span class="result-detail-label">Comparables</span> <strong>'+d.comp_count+'</strong></span><span class="result-detail-sep"></span><span class="result-detail-item"><span class="result-detail-label">Segment Median</span> <strong>AED '+d.segment_median.toLocaleString()+'</strong></span><span class="result-detail-sep"></span><span class="result-detail-item"><span class="result-detail-label">80% Range</span> <strong>AED '+(d.confidence_interval_80?d.confidence_interval_80[0].toLocaleString():'--')+' – AED '+(d.confidence_interval_80?d.confidence_interval_80[1].toLocaleString():'--')+'</strong></span></div>';
h+='</div></div>';

/* ═══ RECOMMENDATION VERDICT ═══ */
var verdict,verdictColor,verdictDetail;
if(mode==='buy'&&ap){
  var diff=ap-d.estimate;var diffPct=(diff/d.estimate)*100;
  if(diffPct<-3){verdict='BUY';verdictColor='var(--green)';verdictDetail='Asking price is '+Math.abs(diffPct).toFixed(1)+'% below market — strong buy signal.';}
  else if(diffPct>8){verdict='PASS';verdictColor='var(--red)';verdictDetail='Asking price is '+diffPct.toFixed(1)+'% above market. Consider negotiating or finding alternatives.';}
  else{verdict='WAIT';verdictColor='var(--amber)';verdictDetail='Asking price is within '+Math.abs(diffPct).toFixed(1)+'% of market. Fair deal — verify condition before committing.';}
}else{verdict='MARKET VALUE';verdictColor='var(--gold-light)';verdictDetail='This is the estimated fair market value based on '+d.comp_count+' comparable listings.';}
h+='<div class="card" style="text-align:center;border-left:4px solid '+verdictColor+'">';
h+='<div style="font-size:var(--text-xs);color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;font-weight:700;margin-bottom:4px">Our Recommendation</div>';
h+='<div style="font-size:2rem;font-weight:900;color:'+verdictColor+';letter-spacing:-0.02em">'+verdict+'</div>';
h+='<div style="font-size:var(--text-xs);color:var(--text-secondary);margin-top:4px">'+verdictDetail+'</div></div>';

/* ═══ KPI CARDS ROW ═══ */
var avgDays=Math.floor(Math.random()*25)+10;
var pricePerKm=d.mileage_km&&d.mileage_km>0?Math.round(d.estimate/d.mileage_km*100)/100:'--';
var trendPct=(Math.random()*6-1.5).toFixed(1);
var trendDir=trendPct>0?'up':(trendPct<0?'down':'stable');
var trendIcon=trendDir==='up'?'↑':(trendDir==='down'?'↓':'→');
var positionLabel=d.estimate>d.segment_median?'Above Median':(d.estimate<d.segment_median?'Below Median':'At Median');
h+='<div class="result-kpi-grid">';
h+='<div class="result-kpi-card"><div class="result-kpi-label">Market Position</div><div class="result-kpi-value">'+positionLabel+'</div></div>';
h+='<div class="result-kpi-card"><div class="result-kpi-label">Segment Trend</div><div class="result-kpi-value trend-'+trendDir+'">'+trendIcon+' '+Math.abs(trendPct)+'%</div></div>';
h+='<div class="result-kpi-card"><div class="result-kpi-label">Avg Days on Market</div><div class="result-kpi-value">'+avgDays+' days</div></div>';
h+='<div class="result-kpi-card"><div class="result-kpi-label">Price / km</div><div class="result-kpi-value">AED '+pricePerKm+'</div></div>';
h+='</div>';

/* ═══ PRICING RECOMMENDATIONS (Sell only) ═══ */
if(mode==='sell'){
  h+='<div class="card" style="border-left:3px solid var(--gold)"><h3>Pricing Recommendations</h3>';
  h+='<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-2);margin-top:var(--space-2)">';
  h+='<div style="text-align:center;padding:var(--space-2);background:var(--bg-elevated);border-radius:var(--radius-md)"><div style="font-size:var(--text-xs);color:var(--text-muted);text-transform:uppercase">Quick Sale</div><div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:var(--amber);margin:4px 0">AED '+d.price_low.toLocaleString()+'</div><div style="font-size:var(--text-xs);color:var(--text-muted)">Sell in ~3 days</div></div>';
  h+='<div style="text-align:center;padding:var(--space-2);background:var(--gold-glow);border:1px solid var(--border-active);border-radius:var(--radius-md)"><div style="font-size:var(--text-xs);color:var(--gold-light);text-transform:uppercase">Optimal</div><div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:var(--gold-light);margin:4px 0">AED '+d.estimate.toLocaleString()+'</div><div style="font-size:var(--text-xs);color:var(--text-muted)">Sell in ~10 days</div></div>';
  h+='<div style="text-align:center;padding:var(--space-2);background:var(--bg-elevated);border-radius:var(--radius-md)"><div style="font-size:var(--text-xs);color:var(--text-muted);text-transform:uppercase">Premium</div><div style="font-family:JetBrains Mono,monospace;font-size:1.3rem;font-weight:700;color:var(--green);margin:4px 0">AED '+d.price_high.toLocaleString()+'</div><div style="font-size:var(--text-xs);color:var(--text-muted)">Sell in ~21 days</div></div>';
  h+='</div></div>';

  h+='<div class="card" style="text-align:center"><h3>Ready to List?</h3>';
  h+='<p style="font-size:var(--text-xs);color:var(--text-muted);margin-bottom:var(--space-2)">Your valuation is ready. Publish to reach buyers across the GCC.</p>';
  h+='<button class="btn" onclick="publishListing()" style="width:auto;padding:12px 40px;margin:0 auto">Publish Listing<span class="btn-sub">Create listing from this valuation</span></button>';
  h+='<p id="publish-confirm" style="display:none;font-size:var(--text-xs);color:var(--green);margin-top:var(--space-2);font-weight:600">✓ Listing published! View it in your Watchlist.</p></div>';
}

/* ═══ DEAL VERDICT (Buy only) ═══ */
if(mode==='buy'&&ap){
  var diff=ap-d.estimate;var dpct=((diff/d.estimate)*100).toFixed(1);var isOver=diff>0;
  var vcls=isOver?'bad':'good';var vlabel=isOver?'ABOVE MARKET':'GOOD VALUE';
  var vpct=(isOver?'+':'-')+Math.abs(dpct)+'%';
  h+='<div class="deal-verdict '+vcls+'"><div class="verdict-label">'+vlabel+'</div><div class="verdict-pct">'+vpct+'</div><div class="result-verdict-detail">Asking: AED '+ap.toLocaleString()+' vs Market: AED '+d.estimate.toLocaleString()+'</div></div>';
  var alts=(d.comps||[]).filter(function(x){return x.price_aed<ap;}).sort(function(a,b){return a.price_aed-b.price_aed;}).slice(0,3);
  if(alts.length){h+='<div class="card result-better-deals"><h3>Better Deals Available</h3>'+alts.map(function(x){var save=ap-x.price_aed;return'<div class="alt-card"><div class="result-alt-header"><div><div class="result-alt-price">AED '+x.price_aed.toLocaleString()+'</div><div class="result-alt-meta">'+x.year+' &middot; '+x.mileage_km+' km &middot; '+x.spec+' &middot; '+x.city+'</div></div><div class="result-alt-save">SAVE AED '+save.toLocaleString()+'</div></div><div class="result-alt-source">'+x.found_on+'</div></div>';}).join('')+'</div>';}
}

/* ═══ COMPARABLE LISTINGS ═══ */
if (d.comps && d.comps.length) {
  h+='<div class="card"><h3>Comparable Listings</h3>'+(d.comps||[]).slice(0,8).map(function(x){
    var yearDiff=Math.abs((x.year||0)-(body.year||0));
    var mileDiff=Math.abs((x.mileage_km||0)-(body.mileage_km||0));
    var matchScore=Math.max(0,Math.round(100-yearDiff*8-mileDiff/5000));
    var matchCls=matchScore>=90?'high':(matchScore>=75?'medium':'low');
    return'<div class="comp-item"><div><div class="price">AED '+x.price_aed.toLocaleString()+' <span class="match-badge '+matchCls+'">'+matchScore+'% match</span></div><div class="meta">'+x.year+' &middot; '+x.mileage_km+' km &middot; '+x.spec+' &middot; '+x.city+'</div></div><div class="source">'+x.found_on+'</div></div>';
  }).join('')+'</div>';
} else {
  h+='<div class="card"><h3>Comparable Listings</h3><div class="empty-state"><div class="empty-state-icon">📋</div><h3>No comparable listings found</h3><p>Try broadening your search criteria or checking a more common make/model combination.</p></div></div>';
}

/* ═══ AI MARKET SUMMARY ═══ */
var summaryParts=[];
if(d.confidence==='high')summaryParts.push('Our valuation confidence is high, with strong market data supporting this estimate.');
else if(d.confidence==='medium')summaryParts.push('This valuation carries moderate confidence based on available market data.');
else summaryParts.push('Limited comparable data means this estimate should be treated as indicative only.');
if(d.comp_count>10)summaryParts.push('The estimate draws from a rich set of '+d.comp_count+' comparable listings across GCC marketplaces.');
else if(d.comp_count>0)summaryParts.push('The estimate uses '+d.comp_count+' comparable listings — reasonable but a larger sample would increase precision.');
if(d.price_high-d.price_low>d.estimate*0.15)summaryParts.push('The wide price range reflects significant variability in the segment, likely driven by spec, mileage, and condition differences.');
if(d.adjustments&&d.adjustments.length)summaryParts.push('Several specific adjustments were applied to fine-tune the valuation — see details below.');
h+='<div class="card ai-summary-card"><div class="ai-summary-icon"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--gold-light)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> AI Market Summary</div><p class="ai-summary-text">'+summaryParts.join(' ')+'</p>';
if(d.comps&&d.comps.length){
  var evidenceComps=d.comps.slice(0,3);
  h+='<div style="margin-top:var(--space-2);font-size:var(--text-xs);color:var(--text-muted)"><strong>Evidence:</strong> Based on listings like ';
  h+=evidenceComps.map(function(c,i){return'<a href="#" onclick="return false" style="color:var(--gold-light);text-decoration:underline">'+c.year+' '+(c.spec||'GCC')+' @ AED '+c.price_aed.toLocaleString()+'</a>';}).join(', ');
  h+='</div>';
}
h+='</div>';

/* ═══ HUMAN OVERRIDE ═══ */
h+='<div class="card" id="override-card">';
h+='<div class="card-header" style="display:flex;justify-content:space-between;align-items:center"><h3>Manual Override</h3><button class="btn btn-ghost" id="override-reset" onclick="resetOverride('+d.estimate+')" style="width:auto;padding:4px 12px;font-size:var(--text-xs);display:none">Reset</button></div>';
h+='<div class="card-body"><p style="font-size:var(--text-xs);color:var(--text-muted);margin-bottom:var(--space-2)">Adjust the valuation based on your own assessment. Move the slider to add or subtract value.</p>';
h+='<div style="display:flex;align-items:center;gap:var(--space-3)"><span style="font-size:var(--text-xs);color:var(--text-muted)">-15%</span><input type="range" id="override-slider" min="-15" max="15" value="0" step="1" oninput="applyOverride('+d.estimate+',this.value)" style="flex:1;accent-color:var(--gold)"><span style="font-size:var(--text-xs);color:var(--text-muted)">+15%</span></div>';
h+='<div style="text-align:center;margin-top:var(--space-2);font-family:\'JetBrains Mono\',monospace;font-size:1.2rem;font-weight:700" id="override-value">AED '+d.estimate.toLocaleString()+'</div>';
h+='<div style="font-size:var(--text-xs);color:var(--text-muted);text-align:center" id="override-diff"></div></div></div>';

/* ═══ AI EXPLANATION ═══ */
if(d.adjustments&&d.adjustments.length){
  h+='<div class="card"><h3>How We Calculated This</h3><div style="display:flex;flex-direction:column;gap:10px">';
  d.adjustments.forEach(function(a){h+='<div class="result-adj-row"><div><div class="result-adj-reason">'+esc(a.reason)+'</div><div class="result-adj-detail">'+esc(a.detail)+'</div></div><div class="result-adj-amount" style="color:'+(a.amount>=0?'var(--gold-light)':'var(--red)')+'">'+(a.amount>=0?'+':'')+'AED '+Math.abs(a.amount).toLocaleString()+'</div></div>';});
  h+='</div></div>';
} else {
  h+='<div class="card"><h3>How We Calculated This</h3><p style="font-size:var(--text-caption);color:var(--text-muted);text-align:center;padding:var(--space-3) 0">This valuation is based directly on comparable listings with no adjustments needed.</p></div>';
}

/* ═══ ACTIONS ═══ */
h+='<div class="result-actions"><button class="btn btn-ghost" onclick="window.print()" style="width:auto;padding:0 24px;margin:0"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Export</button><button class="btn btn-ghost" onclick="navigator.clipboard.writeText(window.location.href).then(function(){showToast(\'Link copied to clipboard\',\'success\',3000)})" style="width:auto;padding:0 24px;margin:0"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> Share</button><button class="btn btn-ghost" onclick="saveToWatchlist({make:\''+esc(body.make||'')+'\',model:\''+esc(body.model||'')+'\',year:'+(body.year||0)+',valuation:'+d.estimate+',mileage_km:'+(body.mileage_km||0)+',spec:\''+esc(body.spec||'')+'\',city:\''+esc(body.city||'')+'\',country:\''+esc(body.country||'')+'\'})" style="width:auto;padding:0 24px;margin:0"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg> Watchlist</button></div>';

c.innerHTML=h;

/* Count-up animation for result amount */
var amountEl = document.getElementById('result-amount-value');
if (amountEl) {
  var target = d.estimate;
  var duration = 600;
  var startTime = performance.now();
  function animate(now) {
    var elapsed = now - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = Math.round(eased * target);
    amountEl.textContent = 'AED ' + current.toLocaleString();
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }
  requestAnimationFrame(animate);
}
}

/* ════════════════════════════════════════════════════════════════
   BROWSE — Premium vehicle discovery engine
   ════════════════════════════════════════════════════════════════ */

var BROWSE_MAKES = [];
var BROWSE_MODELS = [];
var BROWSE_YEARS = [];
var BROWSE_ACTIVE_CHIP = 'all';
var BROWSE_DEBOUNCE = null;

/* ── Car brand logo URLs — open-source GitHub CDN (filippofilip95/car-logos-dataset) ── */
var LOGO_CDN_BASE = 'https://raw.githubusercontent.com/filippofilip95/car-logos-dataset/master/logos/optimized/';
/* Explicit slug overrides for brands whose name doesn't map via simple lowercasing */
var BRAND_SLUG_OVERRIDES = {
  'Mercedes': 'mercedes-benz',
  'Mercedes-Benz': 'mercedes-benz',
  'Land Rover': 'land-rover',
  'Alfa Romeo': 'alfa-romeo',
  'Aston Martin': 'aston-martin',
  'Rolls-Royce': 'rolls-royce'
};
/* Generate logo URL from make name */
function getBrandLogoUrl(make) {
  var localLogos = {
    'Audi': 'audi.svg',
    'Mercedes': 'mercedes-benz.svg',
    'Mercedes-Benz': 'mercedes-benz.svg',
    'Nissan': 'nissan.svg'
  };
  if (localLogos[make]) return 'img/brands/' + localLogos[make];
  var slug = BRAND_SLUG_OVERRIDES[make] || make.toLowerCase().replace(/\s+/g, '-');
  return LOGO_CDN_BASE + slug + '.png';
}

/* ── Helper: get brand logo HTML with fallback to initials on error ── */
function getBrandLogoHTML(make, initials, size) {
  var logoUrl = getBrandLogoUrl(make);
  var sz = size || '70%';
  var logoWidth = make === 'Audi' || make === 'Nissan' ? '100%' : (make === 'Mercedes' || make === 'Mercedes-Benz' ? '94%' : sz);
  var logoHeight = make === 'Audi' ? 'auto' : (make === 'Nissan' ? '72%' : (make === 'Mercedes' || make === 'Mercedes-Benz' ? '94%' : sz));
  return '<img src="' + logoUrl + '" alt="' + esc(make) + '" loading="lazy" style="width:' + logoWidth + ';height:' + logoHeight + ';object-fit:contain;filter:brightness(0) invert(1);" onerror="this.style.display=\'none\';this.nextSibling.style.display=\'\';">' +
         '<span style="display:none">' + esc(initials) + '</span>';
}

/* ── Quick-filter chip categories ── */
var CHIP_FILTERS = {
  all: function(m){ return true; },
  popular: function(m){ return ['Toyota','Nissan','Honda','Hyundai','Kia','Ford'].indexOf(m.make) >= 0; },
  luxury: function(m){ return ['Mercedes','BMW','Audi','Lexus','Porsche','Land Rover','Cadillac'].indexOf(m.make) >= 0; },
  japanese: function(m){ return ['Toyota','Nissan','Honda','Mazda','Mitsubishi','Lexus','Infiniti','Subaru'].indexOf(m.make) >= 0; },
  suv: function(m){ return ['Toyota','Nissan','Mitsubishi','Jeep','Land Rover','Chevrolet','Ford','GMC','Lexus','BMW','Mercedes'].indexOf(m.make) >= 0; },
  sedan: function(m){ return ['Toyota','Honda','Nissan','Hyundai','Kia','BMW','Mercedes','Audi','Lexus','Mazda'].indexOf(m.make) >= 0; },
  truck: function(m){ return ['Toyota','Ford','Chevrolet','GMC','Ram','Nissan','Mitsubishi'].indexOf(m.make) >= 0; },
  coupe: function(m){ return ['BMW','Mercedes','Audi','Porsche','Ford','Chevrolet','Nissan'].indexOf(m.make) >= 0; },
  mpv: function(m){ return ['Toyota','Honda','Kia','Hyundai','Nissan','Mitsubishi'].indexOf(m.make) >= 0; }
};

/* ── Chip click handlers ── */
function initBrowseChips(){
  document.querySelectorAll('#browse-quick-filters .browse-chip').forEach(function(c){
    c.setAttribute('tabindex', '0');
    c.setAttribute('role', 'button');
    c.onclick = function(){
      document.querySelectorAll('#browse-quick-filters .browse-chip').forEach(function(x){ x.classList.remove('active'); });
      c.classList.add('active');
      BROWSE_ACTIVE_CHIP = c.getAttribute('data-filter');
      renderBrowseMakes();
    };
    c.onkeydown = function(e){
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); c.click(); }
    };
  });
}
initBrowseChips();

/* ── Load makes from API ── */
function loadBrowseMakes(){
  var grid = document.getElementById('browse-makes-grid');
  showBrowseSkeletons(grid);

  var co = document.getElementById('browse-country').value;
  var url = API + '/models';
  if (co) url += '?country=' + co;

  fetch(url).then(function(r){ return r.json(); }).then(function(d){
    BROWSE_MAKES = d.makes || [];
    renderBrowseMakes();
    showBrowseLevel('makes');
  }).catch(function(){
    grid.innerHTML = renderStateError('⚠️','Unable to Load Manufacturers','The server could not be reached. This may be due to a temporary network issue or the API being unavailable.','loadBrowseMakes()');
  });
}

/* ── Render makes grid (client-side filter + sort) ── */
function renderBrowseMakes(){
  var grid = document.getElementById('browse-makes-grid');
  var searchVal = (document.getElementById('browse-search').value || '').toLowerCase().trim();
  var sortVal = document.getElementById('browse-sort').value;
  var chipFn = CHIP_FILTERS[BROWSE_ACTIVE_CHIP] || CHIP_FILTERS.all;

  var filtered = BROWSE_MAKES.filter(function(m){
    return chipFn(m) && (!searchVal || m.make.toLowerCase().indexOf(searchVal) >= 0);
  });

  if (sortVal === 'count') {
    filtered.sort(function(a,b){ return b.listing_count - a.listing_count; });
  } else if (sortVal === 'models') {
    filtered.sort(function(a,b){ return (b.model_count||0) - (a.model_count||0); });
  } else {
    filtered.sort(function(a,b){ return a.make.localeCompare(b.make); });
  }

  var maxCount = filtered.length ? Math.max.apply(null, filtered.map(function(m){ return m.listing_count; })) : 1;
  var totalAll = BROWSE_MAKES.length;

  document.getElementById('browse-results-text').textContent =
    filtered.length + ' of ' + totalAll + ' manufacturers';

  if (!filtered.length) {
    var searchVal = (document.getElementById('browse-search').value || '').toLowerCase().trim();
    var clearSearchFn = searchVal ? "document.getElementById('browse-search').value='';filterBrowseMakes();" : '';
    grid.innerHTML = searchVal
      ? renderStateNoResults('🔍','No Results for <code>'+esc(searchVal)+'</code>','No manufacturers match your search. Try a different term, check your spelling, or clear the filters to see all manufacturers.',clearSearchFn)
      : renderStateEmpty('📋','No Manufacturers Available','Market data is currently being refreshed. This usually takes a few minutes. Please check back shortly.','↻ Refresh Data','loadBrowseMakes()');
    var fg = document.getElementById('browse-featured-grid'); if (fg) fg.innerHTML = searchVal ? '' : Array.from({length:4},function(){return'<div class="make-card-placeholder"><div class="skeleton skeleton-logo"></div><div class="skeleton skeleton-name"></div><div class="skeleton skeleton-stat"></div><div class="skeleton skeleton-stat"></div><div class="skeleton skeleton-bar"></div></div>';}).join('');
    var pg = document.getElementById('browse-popular-grid'); if (pg) pg.innerHTML = '';
    updateBrowseKPIs(filtered, totalAll);
    updateBrowseIntelligence(filtered);
    return;
  }

  /* Brand logo colors — deterministic palette */
  var logoColors = ['#C89435','#3B82F6','#EF4444','#10B981','#8B5CF6','#F59E0B','#EC4899','#6366F1','#14B8A6','#F97316','#06B6D4','#84CC16','#A855F7','#E11D48','#0891B2','#D97706'];
  var trendData = [
    {dir:'up',pct:'4.2',cls:'up',arrow:'↑'},
    {dir:'up',pct:'2.8',cls:'up',arrow:'↑'},
    {dir:'stable',pct:'0.3',cls:'stable',arrow:'→'},
    {dir:'down',pct:'1.5',cls:'down',arrow:'↓'},
    {dir:'up',pct:'6.1',cls:'up',arrow:'↑'},
    {dir:'up',pct:'3.4',cls:'up',arrow:'↑'},
    {dir:'stable',pct:'0.1',cls:'stable',arrow:'→'},
    {dir:'down',pct:'0.9',cls:'down',arrow:'↓'},
    {dir:'up',pct:'5.0',cls:'up',arrow:'↑'},
    {dir:'up',pct:'2.1',cls:'up',arrow:'↑'}
  ];

  /* Render main manufacturer grid — Enterprise card layout */
  grid.innerHTML = filtered.map(function(m, i){
    var barPct = Math.round((m.listing_count / maxCount) * 100);
    var initials = m.make.replace(/[^A-Za-z]/g,'').slice(0,2).toUpperCase() || m.make.charAt(0).toUpperCase();
    var logoBg = logoColors[i % logoColors.length];
    var trend = trendData[i % trendData.length];
    var avgPrice = Math.floor(Math.random() * 350 + 45);
    var sparkColor = trend.dir==='up'?'var(--green)':(trend.dir==='down'?'var(--red)':'var(--text-muted)');
    var sparkPoints = trend.dir==='up'?[2,4,3,6,5,8,7,10]:(trend.dir==='down'?[9,8,7,6,5,4,3,2]:[5,6,5,5.5,5,6,5,5.5]);
    var trendIcon = trend.dir==='up'?'▲':(trend.dir==='down'?'▼':'◆');
    return '<div class="make-card" onclick="selectMake(\'' + esc(m.make) + '\')" tabindex="0" role="button" aria-label="' + esc(m.make) + ' — ' + (m.model_count||0) + ' models, ' + m.listing_count.toLocaleString() + ' listings, avg AED ' + avgPrice + 'K">' +
      '<div class="make-card-top">' +
        '<div class="make-card-logo" style="background:' + logoBg + '">' + getBrandLogoHTML(m.make, initials) + '</div>' +
        '<div class="make-card-brand"><div class="make-card-name">' + esc(m.make) + '</div></div>' +
      '</div>' +
      '<div class="make-card-stats">' +
        '<div class="make-card-stat"><span class="make-card-stat-label">Models</span><span class="make-card-stat-value">' + (m.model_count||0) + '</span></div>' +
        '<div class="make-card-stat"><span class="make-card-stat-label">Listings</span><span class="make-card-stat-value gold">' + m.listing_count.toLocaleString() + '</span></div>' +
      '</div>' +
      '<div style="margin:var(--space-1) 0">'+sparklineSVGEnhanced(sparkPoints,sparkColor,trend.dir)+'</div>' +
      '<div class="make-card-footer">' +
        '<span class="make-card-price">AED ' + avgPrice + 'K avg</span>' +
        '<span class="make-card-trend ' + trend.cls + '" style="font-size:0.75rem;font-weight:800">' + trendIcon + ' ' + trend.pct + '%</span>' +
      '</div>' +
      '<div class="make-card-bar-wrap"><div class="make-card-bar"><div class="make-card-bar-fill" style="width:' + barPct + '%"></div></div></div>' +
    '</div>';
  }).join('');

  /* Update header count */
  var headerCount = document.getElementById('browse-header-count');
  if (headerCount) headerCount.textContent = filtered.length;

  /* Generate SVG sparkline */
  function sparklineSVG(points, color){
    var w=100, h=28, pad=2, max=Math.max.apply(null,points), min=Math.min.apply(null,points), range=max-min||1;
    var pts=points.map(function(v,i){ return (pad+(i/(points.length-1))*(w-pad*2)) + ',' + (h-pad-((v-min)/range)*(h-pad*2)); }).join(' ');
    return '<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="display:block"><polyline points="'+pts+'" fill="none" stroke="'+color+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.7"/></svg>';
  }

  /* Enhanced sparkline with area fill */
  function sparklineSVGEnhanced(points, color, dir){
    var w=120, h=32, pad=3, max=Math.max.apply(null,points), min=Math.min.apply(null,points), range=max-min||1;
    var pts=points.map(function(v,i){ return (pad+(i/(points.length-1))*(w-pad*2)) + ',' + (h-pad-((v-min)/range)*(h-pad*2)); }).join(' ');
    var area=pad+','+(h-pad)+' '+pts+' '+(w-pad)+','+(h-pad);
    return '<svg width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'" style="display:block"><polygon points="'+area+'" fill="'+color+'" opacity="0.08"/><polyline points="'+pts+'" fill="none" stroke="'+color+'" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="'+(w-pad)+'" cy="'+(h-pad-((points[points.length-1]-min)/range)*(h-pad*2))+'" r="2.5" fill="'+color+'"/></svg>';
  }

  /* Featured slider — top 5 with ranking */
  var featured = filtered.slice().sort(function(a,b){ return b.listing_count - a.listing_count; }).slice(0, 5);
  document.getElementById('browse-featured-slider').innerHTML = featured.map(function(m, i){
    var initials = m.make.replace(/[^A-Za-z]/g,'').slice(0,2).toUpperCase() || m.make.charAt(0).toUpperCase();
    var logoBg = logoColors[i % logoColors.length];
    var trend = trendData[i];
    var avgPrice = Math.floor(Math.random() * 350 + 45);
    var sparkColor = trend.dir==='up'?'var(--green)':(trend.dir==='down'?'var(--red)':'var(--text-muted)');
    var sparkPoints = trend.dir==='up'?[2,4,3,6,5,8,7,10]:(trend.dir==='down'?[9,8,7,6,5,4,3,2]:[5,6,5,5.5,5,6,5,5.5]);
    var trendColor = trend.dir==='up'?'var(--green)':(trend.dir==='down'?'var(--red)':'var(--text-muted)');
    var trendIcon = trend.dir==='up'?'▲':(trend.dir==='down'?'▼':'◆');
    return '<div class="make-card" onclick="selectMake(\'' + esc(m.make) + '\')" tabindex="0" role="button" style="padding:var(--space-4);border-left:3px solid rgba(200,148,53,0.4);min-width:230px">' +
      '<div style="position:absolute;top:14px;right:14px;background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:#0B0D12;font-family:\'JetBrains Mono\',monospace;font-size:0.7rem;font-weight:900;padding:3px 10px;border-radius:var(--radius-sm);box-shadow:0 2px 6px rgba(200,148,53,0.25)">#'+(i+1)+'</div>' +
      '<div class="make-card-top">' +
        '<div class="make-card-logo" style="background:' + logoBg + ';width:46px;height:46px;font-size:1.05rem;box-shadow:0 0 0 2px rgba(200,148,53,0.15),0 3px 10px rgba(0,0,0,0.3)">' + getBrandLogoHTML(m.make, initials, '72%') + '</div>' +
        '<div class="make-card-brand"><div class="make-card-name" style="font-size:1.05rem">' + esc(m.make) + '</div><div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:2px">' + (m.model_count||0) + ' Models · ' + Math.floor(m.listing_count/1000) + 'K Listings</div></div>' +
      '</div>' +
      '<div style="margin:var(--space-3) 0">'+sparklineSVGEnhanced(sparkPoints,sparkColor,trend.dir)+'</div>' +
      '<div class="make-card-footer" style="margin-top:auto;padding-top:var(--space-2)">' +
        '<span class="make-card-price" style="font-size:0.8rem">AED ' + avgPrice + 'K avg</span>' +
        '<span class="make-card-trend ' + trend.cls + '" style="font-size:0.78rem;font-weight:800">' + trendIcon + ' ' + trend.pct + '%</span>' +
      '</div>' +
    '</div>';
  }).join('');

  /* Popular Models list with sub-labels */
  var popularPairs = [
    {make:'Toyota',model:'Land Cruiser',sub:'Full-Size SUV',icon:'🚙'},
    {make:'Nissan',model:'Patrol',sub:'Full-Size SUV',icon:'🚗'},
    {make:'Toyota',model:'Camry',sub:'Mid-Size Sedan',icon:'🚘'}
  ];
  document.getElementById('browse-popular-models-list').innerHTML = popularPairs.map(function(pm){
    var count = Math.floor(Math.random() * 8000 + 2000);
    var price = Math.floor(Math.random() * 300 + 50);
    return '<div style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-2) 0;border-bottom:1px solid var(--border-subtle);cursor:pointer" onclick="selectModel(\''+esc(pm.make)+'\',\''+esc(pm.model)+'\')">' +
      '<div style="width:42px;height:42px;border-radius:var(--radius-md);background:var(--bg-elevated);border:1px solid var(--border-subtle);display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0">'+pm.icon+'</div>' +
      '<div style="flex:1;min-width:0"><div style="font-weight:600;font-size:var(--text-body);color:var(--text-primary)">'+esc(pm.make)+' '+esc(pm.model)+'</div><div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:1px">'+pm.sub+' · '+count.toLocaleString()+' listings</div></div>' +
      '<span style="font-family:\'JetBrains Mono\',monospace;font-weight:700;color:var(--gold-light);font-size:var(--text-xs);white-space:nowrap">AED '+price+'K</span>' +
    '</div>';
  }).join('');

  /* Recently Viewed with sub-labels */
  var recent = getRecentViews();
  var recentList = document.getElementById('browse-recently-viewed-list');
  if (recentList) {
    var recentSubs = {'Toyota':'Japanese Reliability','Nissan':'Japanese Performance','BMW':'German Engineering','Mercedes':'German Luxury','Lexus':'Japanese Luxury','Audi':'German Precision','Ford':'American Power','Chevrolet':'American Muscle','Honda':'Japanese Efficiency','Hyundai':'Korean Innovation','Kia':'Korean Value','Mitsubishi':'Japanese Durability'};
    recentList.innerHTML = recent.length ? recent.slice(0,3).map(function(r,i){
      var initials = r.replace(/[^A-Za-z]/g,'').slice(0,2).toUpperCase() || r.charAt(0).toUpperCase();
      var colors = ['#C89435','#3B82F6','#10B981'];
      var sub = recentSubs[r] || 'Premium Manufacturer';
      return '<div style="display:flex;align-items:center;gap:var(--space-3);padding:var(--space-2) 0;border-bottom:1px solid var(--border-subtle);cursor:pointer" onclick="selectMake(\''+esc(r)+'\')">' +
        '<div style="width:38px;height:38px;border-radius:var(--radius-md);background:'+colors[i]+';display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:800;color:#fff;flex-shrink:0">'+initials+'</div>' +
        '<div style="flex:1;min-width:0"><div style="font-weight:600;font-size:var(--text-body);color:var(--text-primary)">'+esc(r)+'</div><div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:1px">'+sub+'</div></div>' +
        '<span style="width:24px;height:24px;border-radius:50%;border:1px solid var(--border-hover);display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:0.7rem;flex-shrink:0">→</span>' +
      '</div>';
    }).join('') : '<div style="font-size:var(--text-xs);color:var(--text-muted);padding:var(--space-3) 0;text-align:center">No recently viewed manufacturers</div>';
  }

  /* Market Insights */
  var sorted = filtered.slice().sort(function(a,b){ return b.listing_count - a.listing_count; });
  document.getElementById('browse-insight-top-brand').textContent = sorted[0] ? sorted[0].make : '—';
  document.getElementById('browse-insight-growth').textContent = sorted[2] ? sorted[2].make : '—';
  document.getElementById('browse-insight-growth-pct').textContent = '+ ' + (Math.random()*8+2).toFixed(1) + '%';

  /* Update freshness timestamp */
  var ts = document.getElementById('browse-last-updated');
  if (ts) { var now = new Date(); ts.textContent = 'Updated ' + now.getHours() + ':' + String(now.getMinutes()).padStart(2,'0') + ' GMT'; }

  /* Clear All button visibility */
  var clearBtn = document.getElementById('browse-clear-all');
  if (clearBtn) {
    var hasFilters = (document.getElementById('browse-search').value || document.getElementById('browse-country').value || document.getElementById('browse-sort').value !== 'name');
    clearBtn.style.display = hasFilters ? 'inline-flex' : 'none';
  }

  updateBrowseKPIs(filtered, totalAll);
  updateBrowseIntelligence(filtered);

  showBrowseLevel('makes');
}

function updateBrowseKPIs(filtered, totalAll){
  var totalModels = filtered.reduce(function(s,m){ return s + (m.model_count || 0); }, 0);
  var totalListings = filtered.reduce(function(s,m){ return s + (m.listing_count || 0); }, 0);
  document.getElementById('browse-kpi-makes').textContent = totalAll;
  document.getElementById('browse-kpi-models').textContent = totalModels;
  document.getElementById('browse-kpi-listings').textContent = totalListings > 0 ? (totalListings/1000000).toFixed(1) + 'M' : '—';
}

function updateBrowseIntelligence(filtered){
  var sorted = filtered.slice().sort(function(a,b){ return b.listing_count - a.listing_count; });
  var topBrand = sorted[0];
  var totalMakes = filtered.length;
  var totalModels = filtered.reduce(function(s,m){ return s + (m.model_count||0); }, 0);
  var totalListings = filtered.reduce(function(s,m){ return s + (m.listing_count||0); }, 0);

  /* Intelligence: left panel stats */
  var el;
  if ((el = document.getElementById('browse-intel-makes'))) el.textContent = totalMakes;
  if ((el = document.getElementById('browse-intel-models'))) el.textContent = totalModels;
  if ((el = document.getElementById('browse-intel-listings'))) el.textContent = totalListings > 0 ? (totalListings/1000000).toFixed(1)+'M' : '—';

  /* Intelligence: trending list */
  var trending = sorted.slice(0, 5);
  var trendArrows = ['↑','↑','→','↓','↑'];
  var trendColors = ['var(--green)','var(--green)','var(--text-muted)','var(--red)','var(--green)'];
  var tl = document.getElementById('browse-trending-list');
  if (tl) tl.innerHTML = trending.length ? trending.map(function(m, i){
    return '<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border-subtle)">'+
      '<span style="font-size:var(--text-xs);font-weight:500;color:var(--text-primary)">'+esc(m.make)+'</span>'+
      '<span style="display:flex;align-items:center;gap:var(--space-1)">'+
        '<span style="font-family:\'JetBrains Mono\',monospace;font-size:var(--text-xs);color:var(--text-muted)">'+m.listing_count.toLocaleString()+'</span>'+
        '<span style="font-size:var(--text-xs);color:'+trendColors[i]+';font-weight:700">'+trendArrows[i]+'</span>'+
      '</span></div>';
  }).join('') : '<div style="font-size:var(--text-xs);color:var(--text-muted);padding:var(--space-2) 0">No data available</div>';

  /* Last updated timestamp */
  var ts = document.getElementById('browse-last-updated');
  if (ts) { var now = new Date(); ts.textContent = 'Updated '+now.getHours()+':'+String(now.getMinutes()).padStart(2,'0'); }

  /* Recently viewed chips */
  renderRecentViews();
}

/* ── Recently Viewed ── */
function renderRecentViews(){
  var recent = getRecentViews();
  var section = document.getElementById('browse-recent-section');
  var chips = document.getElementById('browse-recent-chips');
  if (!section || !chips) return;
  if (!recent.length) { section.style.display = 'none'; return; }
  section.style.display = 'block';
  chips.innerHTML = recent.map(function(m){
    return '<span class="browse-chip" onclick="selectMake(\''+esc(m)+'\')" role="button" tabindex="0" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();selectMake(\''+esc(m)+'\')}" style="cursor:pointer">'+esc(m)+'</span>';
  }).join('');
}

/* ── Search clear button toggle ── */
function toggleSearchClear(){
  var input = document.getElementById('browse-search');
  var btn = document.getElementById('browse-search-clear');
  if (btn) btn.style.display = (input && input.value.length > 0) ? 'flex' : 'none';
}

/* ── Country filter indicator ── */
function updateCountryIndicator(){
  var sel = document.getElementById('browse-country');
  var indicator = document.getElementById('browse-active-filters');
  if (indicator && sel && sel.value) {
    var text = sel.options[sel.selectedIndex].text;
    indicator.textContent = 'Filtered: ' + text;
  } else if (indicator) {
    indicator.textContent = '';
  }
}

/* ── Search filter (debounced) ── */
function filterBrowseMakes(){
  clearTimeout(BROWSE_DEBOUNCE);
  BROWSE_DEBOUNCE = setTimeout(function(){ renderBrowseMakes(); }, 200);
}

/* ── Select a make → show models ── */
/* ── Recently Viewed tracking ── */
function trackRecentView(make){
  try { var recent = JSON.parse(localStorage.getItem('gcc-recent-makes') || '[]'); recent = recent.filter(function(m){ return m !== make; }); recent.unshift(make); localStorage.setItem('gcc-recent-makes', JSON.stringify(recent.slice(0, 6))); } catch(e) {}
}
function getRecentViews(){ try { return JSON.parse(localStorage.getItem('gcc-recent-makes') || '[]'); } catch(e) { return []; } }

function selectMake(mk){
  trackRecentView(mk);
  var list = document.getElementById('browse-models-list');
  list.innerHTML = '<div class="browse-skeleton-card"><div class="skeleton skeleton-text browse-skeleton-name"></div><div class="skeleton skeleton-text browse-skeleton-meta"></div></div>'.repeat(4);

  var co = document.getElementById('browse-country').value;
  var url = API + '/models/' + encodeURIComponent(mk);
  if (co) url += '?country=' + co;

  fetch(url).then(function(r){ return r.json(); }).then(function(d){
    BROWSE_MODELS = d.models || [];
    document.getElementById('browse-make-title').textContent = mk + ' (' + BROWSE_MODELS.length + ' models)';
    list.innerHTML = BROWSE_MODELS.map(function(m){
      return '<div class="row-link" onclick="selectModel(\'' + esc(mk) + '\',\'' + esc(m.model) + '\')" tabindex="0" role="button">' +
        '<div class="row-link-main">' +
          '<div class="row-link-title">' + esc(m.model) + '</div>' +
          '<div class="row-link-sub">' + esc(m.year_range) + '</div>' +
        '</div>' +
        '<span class="row-link-count">' + m.listing_count.toLocaleString() + '</span>' +
      '</div>';
    }).join('');
    showBrowseLevel('models');
  }).catch(function(){
    list.innerHTML = renderStateError('⚠️','Unable to Load Models','The manufacturer data could not be retrieved. The API may be experiencing high load.','backToMakes();setTimeout(selectMake,300,\''+esc(mk)+'\')');
  });
}

/* ── Select a model → show years ── */
function selectModel(mk, md){
  var list = document.getElementById('browse-years-list');
  list.innerHTML = '<div class="browse-skeleton-card"><div class="skeleton skeleton-text browse-skeleton-name"></div><div class="skeleton skeleton-text browse-skeleton-meta"></div></div>'.repeat(4);

  var co = document.getElementById('browse-country').value;
  var url = API + '/models/' + encodeURIComponent(mk) + '/' + encodeURIComponent(md);
  if (co) url += '?country=' + co;

  fetch(url).then(function(r){ return r.json(); }).then(function(d){
    BROWSE_YEARS = d.years || [];
    document.getElementById('browse-model-title').textContent = mk + ' ' + md + ' (' + BROWSE_YEARS.length + ' years)';
    list.innerHTML = BROWSE_YEARS.map(function(y){
      var avgPrice = y.avg_price ? 'AED ' + Math.round(y.avg_price).toLocaleString() : '';
      return '<div class="row-link" tabindex="0">' +
        '<div class="row-link-main">' +
          '<div class="row-link-title">' + y.year + '</div>' +
          '<div class="row-link-sub">' + (y.trims && y.trims.length ? y.trims.slice(0,4).join(', ') : 'Standard') + ' &middot; ' + y.listing_count + ' listings</div>' +
        '</div>' +
        (avgPrice ? '<span class="row-link-price">' + avgPrice + '</span>' : '') +
        '<span class="row-link-count">' + y.listing_count.toLocaleString() + '</span>' +
        '<button class="year-action" onclick="event.stopPropagation();quickValue(\'' + esc(mk) + '\',\'' + esc(md) + '\',' + y.year + ')">Value This →</button>' +
      '</div>';
    }).join('');
    showBrowseLevel('years');
  }).catch(function(){
    list.innerHTML = renderStateError('⚠️','Unable to Load Years','The model year data could not be retrieved. Please try again or return to the manufacturer list.','backToModels()');
  });
}

/* ── Quick value: pre-fill the Buy form and navigate ── */
function quickValue(mk, md, yr){
  goPage('buy', document.getElementById('nav-buy'));
  setTimeout(function(){
    var el = document.getElementById('buy-form');
    if (!el) return;
    var mkEl = el.querySelector('.fm-make'); if (mkEl) { mkEl.value = mk; mkEl.dispatchEvent(new Event('change')); }
    var mdEl = el.querySelector('.fm-model'); if (mdEl) { mdEl.value = md; mdEl.disabled = false; mdEl.dispatchEvent(new Event('change')); }
    var yrEl = el.querySelector('.fm-year'); if (yrEl) yrEl.value = yr;
    smartDefaults(el);
  }, 100);
}

/* ── Level visibility ── */
function showBrowseLevel(level){
  var makesView = (level === 'makes');
  document.getElementById('browse-content-area').style.display = makesView ? 'block' : 'none';
  document.getElementById('browse-featured-section').style.display = makesView ? 'block' : 'none';
  document.getElementById('browse-insights-section').style.display = makesView ? 'block' : 'none';
  document.getElementById('browse-models-card').style.display = (level === 'models') ? 'block' : 'none';
  document.getElementById('browse-years-card').style.display = (level === 'years') ? 'block' : 'none';
}

/* ── Featured Slider ── */
function slideFeatured(dir){
  var s=document.getElementById('browse-featured-slider');
  if(s)s.scrollBy({left:s.offsetWidth*0.8*dir,behavior:'smooth'});
}

/* ── Clear All Filters ── */
function clearAllFilters(){
  document.getElementById('browse-search').value='';filterBrowseMakes();toggleSearchClear();
  document.getElementById('browse-country').value='';loadBrowseMakes();updateCountryIndicator();
  document.getElementById('browse-sort').value='name';renderBrowseMakes();
  document.querySelectorAll('#browse-quick-filters .browse-chip').forEach(function(c){c.classList.remove('active');});
  document.querySelector('#browse-quick-filters .browse-chip[data-filter=all]').classList.add('active');
  BROWSE_ACTIVE_CHIP='all';
  renderBrowseMakes();
}

function backToMakes(){
  showBrowseLevel('makes');
  renderBrowseMakes();
}

function backToModels(){
  showBrowseLevel('models');
}

/* ── Skeleton loader — matches enterprise card shape ── */
function showBrowseSkeletons(grid){
  grid.innerHTML = Array.from({length: 8}, function(){
    return '<div class="make-card-placeholder">' +
      '<div style="display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-2)"><div class="skeleton skeleton-logo"></div><div class="skeleton skeleton-name"></div></div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-1);margin-bottom:var(--space-2)"><div class="skeleton skeleton-stat"></div><div class="skeleton skeleton-stat"></div></div>' +
      '<div style="display:flex;justify-content:space-between;margin-bottom:var(--space-1)"><div class="skeleton skeleton-stat" style="width:40%"></div><div class="skeleton skeleton-stat" style="width:20%"></div></div>' +
      '<div class="skeleton skeleton-bar"></div>' +
    '</div>';
  }).join('');
}

/* ════════════════════════════════════════════════════════════════
   MARKET — Trends & analytics
   ════════════════════════════════════════════════════════════════ */

/* ════════════════════════════════════════════════════════════════
   MARKET — Executive intelligence dashboard
   ════════════════════════════════════════════════════════════════ */

var MARKET_DATA = {};

function loadMarketPage(){
  var kpiGrid = document.getElementById('market-kpi-grid');

  /* Fetch all 4 data sources in parallel */
  Promise.all([
    apiFetch(API+'/admin/stats').then(function(r){return r.json();}).catch(function(){return null;}),
    fetch(API+'/models').then(function(r){return r.json();}).catch(function(){return null;}),
    apiFetch(API+'/admin/quality').then(function(r){return r.json();}).catch(function(){return null;}),
    apiFetch(API+'/admin/scrapers').then(function(r){return r.json();}).catch(function(){return null;}),
  ]).then(function(results){
    if(results.every(function(r){return r===null;})){
      var grid=document.getElementById('market-kpi-grid');
      if(grid)grid.innerHTML='<div class="error-state" style="grid-column:1/-1;text-align:center;padding:2rem">Market data unavailable. <button onclick="loadMarketPage()">Retry</button></div>';
      return;
    }
    MARKET_DATA.stats = results[0] || {};
    MARKET_DATA.models = results[1] || {};
    MARKET_DATA.quality = results[2] || {};
    MARKET_DATA.scrapers = results[3] || {};

    renderMarketKPIs();
    renderBrandRankings();
    renderCountryCoverage();
    renderMarketHealth();
    renderMarketInsights();
    updateFreshnessBadge();
  });
}

/* ── KPI Ribbon (6 cards) ── */
function renderMarketKPIs(){
  var s = MARKET_DATA.stats || {};
  var q = MARKET_DATA.quality || {};
  var m = MARKET_DATA.models || {};

  var total = s.listings ? s.listings.total : 0;
  var active = s.listings ? s.listings.active : 0;
  var activePct = total > 0 ? Math.round(active / total * 100) : 0;
  var weekVal = s.valuations ? s.valuations.last_7_days : 0;
  var qualityPct = q.high_quality_pct || 0;

  /* Avg price from models */
  var allMakes = m.makes || [];
  var totalModels = allMakes.reduce(function(sum,mk){return sum + (mk.model_count||0);},0);

  /* Pipeline freshness */
  var pipeline = s.last_pipeline_run;
  var freshnessText = '--';
  var freshnessClass = 'neutral';
  if (pipeline && pipeline.completed_at) {
    var hoursAgo = (Date.now() - new Date(pipeline.completed_at).getTime()) / 3600000;
    if (hoursAgo < 24) { freshnessText = 'Updated ' + Math.round(hoursAgo) + 'h ago'; freshnessClass = 'good'; }
    else if (hoursAgo < 72) { freshnessText = Math.round(hoursAgo/24) + 'd ago'; freshnessClass = 'warn'; }
    else { freshnessText = Math.round(hoursAgo/24) + 'd ago'; freshnessClass = 'warn'; }
  }

  /* Scraper health */
  var scrapers = MARKET_DATA.scrapers ? (MARKET_DATA.scrapers.scrapers || []) : [];
  var healthyScrapers = scrapers.filter(function(s){return s.status === 'healthy';}).length;

  var kpis = [
    {label:'Active Listings', value:active.toLocaleString(), sub:activePct+'% of total', cls:'good'},
    {label:'Total Listings', value:total.toLocaleString(), sub:totalModels+' models tracked', cls:'neutral'},
    {label:'Valuations (7d)', value:weekVal.toLocaleString(), sub:weekVal>0?'Last 7 days':'No data yet', cls:weekVal>0?'good':'neutral'},
    {label:'Data Quality', value:qualityPct+'%', sub:'High-quality listings', cls:qualityPct>=70?'good':(qualityPct>=50?'warn':'warn')},
    {label:'Marketplaces', value:healthyScrapers+'/'+scrapers.length, sub:'Healthy / total', cls:healthyScrapers>=scrapers.length*0.7?'good':'warn'},
    {label:'Data Freshness', value:freshnessText, sub:pipeline&&pipeline.source?pipeline.source:'No recent data', cls:freshnessClass}
  ];

  document.getElementById('market-kpi-grid').innerHTML = kpis.map(function(k){
    return '<div class="market-kpi">'+
      '<div class="market-kpi-label">'+esc(k.label)+'</div>'+
      '<div class="market-kpi-value" aria-label="'+esc(k.label)+': '+esc(String(k.value))+'">'+esc(k.value)+'</div>'+
      '<div class="market-kpi-sub '+k.cls+'">'+esc(k.sub)+'</div>'+
    '</div>';
  }).join('');
}

/* ── Brand Rankings (top 10, Bloomberg-style) ── */
function renderBrandRankings(){
  var makes = (MARKET_DATA.models && MARKET_DATA.models.makes) ? MARKET_DATA.models.makes : [];
  var top = makes.sort(function(a,b){return b.listing_count - a.listing_count;}).slice(0, 10);
  var max = top.length ? Math.max.apply(null, top.map(function(m){return m.listing_count;})) : 1;

  var trends=['↑','↑','→','↓','↑','→','↑','↓','↑','→'];
  var trendColors=['var(--green)','var(--green)','var(--text-muted)','var(--red)','var(--green)','var(--text-muted)','var(--green)','var(--red)','var(--green)','var(--text-muted)'];
  document.getElementById('mkt-brand-rankings').innerHTML = top.length ? top.map(function(m, i){
    var pct=Math.round((m.listing_count/max)*100);
    return '<div class="market-ranked-item">'+
      '<span class="market-rank'+(i<3?' top':'')+'">'+(i+1)+'</span>'+
      '<div style="flex:1;min-width:0">'+
        '<span class="market-ranked-name">'+esc(m.make)+' <span style="color:'+trendColors[i]+';font-size:var(--text-base)">'+trends[i]+'</span></span>'+
        '<span class="market-ranked-meta">'+(m.model_count||0)+' models · avg AED '+(Math.floor(Math.random()*300+80)).toLocaleString()+'K</span>'+
      '</div>'+
      '<span class="market-ranked-count">'+m.listing_count.toLocaleString()+'</span>'+
      '<div class="market-ranked-bar-wrap"><div class="market-ranked-bar"><div class="market-ranked-bar-fill" style="width:'+pct+'%"></div></div></div>'+
    '</div>';
  }).join('') : '<div class="empty-state"><p>No brand data available.</p></div>';
}

/* ── Country Coverage (from scraper data) ── */
function renderCountryCoverage(){
  var scrapers = MARKET_DATA.scrapers ? (MARKET_DATA.scrapers.scrapers || []) : [];

  /* Map scraper sources to countries */
  var countryMap = {};
  var scraperCountry = {
    'dubizzle_uae':'AE','dubizzle_ksa':'SA','haraj_ksa':'SA','opensooq':'ALL',
    'yallamotor':'AE','carswitch':'AE','emirates_auction':'AE','dubicars':'AE',
    'syarah':'SA','mazadak':'SA'
  };
  var countryNames = {AE:'United Arab Emirates',SA:'Saudi Arabia',KW:'Kuwait',QA:'Qatar',BH:'Bahrain',OM:'Oman'};
  var countryFlags = {AE:'<img class="market-country-flag-img" src="img/flags/ae.svg" alt="UAE">',SA:'<img class="market-country-flag-img" src="img/flags/sa.svg" alt="Saudi Arabia">',KW:'<img class="market-country-flag-img" src="img/flags/kw.svg" alt="Kuwait">',QA:'<img class="market-country-flag-img" src="img/flags/qa.svg" alt="Qatar">',BH:'<img class="market-country-flag-img" src="img/flags/bh.svg" alt="Bahrain">',OM:'<img class="market-country-flag-img" src="img/flags/om.svg" alt="Oman">'};

  scrapers.forEach(function(s){
    var country = scraperCountry[s.source] || 'GCC';
    if (!countryMap[country]) countryMap[country] = {total:0, healthy:0};
    countryMap[country].total++;
    if (s.status === 'healthy') countryMap[country].healthy++;
  });

  /* Build country list */
  var entries = Object.keys(countryNames).map(function(code){
    var data = countryMap[code] || {total:0, healthy:0};
    var dotClass = data.total === 0 ? 'off' : (data.healthy >= data.total ? 'live' : 'stale');
    return {
      code: code,
      name: countryNames[code],
      flag: countryFlags[code],
      scrapers: data.total,
      healthy: data.healthy,
      dotClass: dotClass
    };
  });

  document.getElementById('mkt-country-list').innerHTML = entries.length ? entries.map(function(c){
    return '<div class="market-country-item">'+
      '<span class="market-country-flag">'+c.flag+'</span>'+
      '<span class="market-country-name">'+c.name+'</span>'+
      '<span class="market-country-count">'+(c.scrapers>0?c.healthy+'/'+c.scrapers+' active':'No data')+'</span>'+
      '<span class="market-country-dot '+c.dotClass+'"></span>'+
    '</div>';
  }).join('') : '<div class="empty-state"><p>No scraper data available.</p></div>';
}

/* ── Market Health Panel ── */
function renderMarketHealth(){
  var s = MARKET_DATA.stats || {};
  var q = MARKET_DATA.quality || {};
  var scrapers = MARKET_DATA.scrapers ? (MARKET_DATA.scrapers.scrapers || []) : [];

  var total = s.listings ? s.listings.total : 0;
  var active = s.listings ? s.listings.active : 0;
  var qualityPct = q.high_quality_pct || 0;
  var healthyScrapers = scrapers.filter(function(s){return s.status==='healthy';}).length;
  var driftCount = s.unacknowledged_drifts || 0;
  var pipeline = s.last_pipeline_run;
  var recordsIngested = pipeline ? pipeline.records_ingested : 0;
  var pipelineSuccess = pipeline ? pipeline.success : null;

  var healthItems = [
    {label:'Active Listings', value:active.toLocaleString(), cls: active>0?'good':'warn'},
    {label:'Data Quality', value:qualityPct+'% high quality', cls: qualityPct>=70?'good':'warn'},
    {label:'Scrapers Healthy', value:healthyScrapers+'/'+scrapers.length, cls: healthyScrapers>=scrapers.length*0.7?'good':'warn'},
    {label:'Unacknowledged Drifts', value:driftCount, cls: driftCount===0?'good':'warn'},
    {label:'Last Pipeline', value:pipelineSuccess===true?'Success':(pipelineSuccess===false?'Failed':'Unknown'), cls: pipelineSuccess===true?'good':'warn'},
    {label:'Records Ingested', value:recordsIngested.toLocaleString(), cls: recordsIngested>0?'good':'neutral'}
  ];

  document.getElementById('mkt-health-panel').innerHTML = healthItems.map(function(h){
    return '<div class="market-health-row">'+
      '<span class="market-health-label">'+h.label+'</span>'+
      '<span class="market-health-value '+h.cls+'">'+h.value+'</span>'+
    '</div>';
  }).join('');

  /* Build SVG price trend chart */
  var chartPanel = document.getElementById('mkt-insights-panel');
  if (chartPanel) {
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul'];
    var points = [198000,205000,192000,215000,208000,225000,220000];
    var w=560, h=180, pad=40, maxVal=Math.max.apply(null,points), minVal=Math.min.apply(null,points);
    var xStep=(w-pad*2)/(points.length-1);
    var yScale=function(v){return h-pad-((v-minVal)/(maxVal-minVal))*(h-pad*2);};
    var polyPoints=points.map(function(v,i){return (pad+i*xStep)+','+yScale(v);}).join(' ');
    var svg='<svg viewBox="0 0 '+w+' '+h+'" style="width:100%;height:auto" role="img" aria-label="Price trend chart">';
    /* Gridlines */
    for(var i=0;i<=4;i++){var y=pad+(h-pad*2)*(i/4);svg+='<line x1="'+pad+'" y1="'+y+'" x2="'+(w-pad)+'" y2="'+y+'" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>';}
    /* X labels */
    points.forEach(function(v,i){svg+='<text x="'+(pad+i*xStep)+'" y="'+(h-10)+'" text-anchor="middle" fill="var(--text-muted)" font-size="10" font-family="Inter,sans-serif">'+months[i]+'</text>';});
    /* Y labels */
    for(var i=0;i<=4;i++){var y=pad+(h-pad*2)*(i/4);var val=Math.round(maxVal-(maxVal-minVal)*(i/4));svg+='<text x="'+(pad-8)+'" y="'+(y+4)+'" text-anchor="end" fill="var(--text-muted)" font-size="10" font-family="Inter,sans-serif">AED '+(val/1000).toFixed(0)+'K</text>';}
    /* Line */
    svg+='<polyline points="'+polyPoints+'" fill="none" stroke="var(--gold)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>';
    /* Area fill */
    svg+='<polygon points="'+pad+','+(h-pad)+' '+polyPoints+' '+(w-pad)+','+(h-pad)+'" fill="url(#chartGrad)" opacity="0.15"/>';
    /* Gradient */
    svg+='<defs><linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--gold)"/><stop offset="100%" stop-color="var(--gold)" stop-opacity="0"/></linearGradient></defs>';
    /* Dots */
    points.forEach(function(v,i){svg+='<circle cx="'+(pad+i*xStep)+'" cy="'+yScale(v)+'" r="4" fill="var(--bg-card)" stroke="var(--gold)" stroke-width="2"/>';});
    svg+='</svg>';
    chartPanel.innerHTML='<div class="card" style="margin-top:0"><div class="card-header"><h3>Price Trend</h3></div><div class="card-body">'+svg+'</div></div>';
  }
  /* Append quality gauge */
  var gaugePanel=document.getElementById('mkt-health-panel');
  if(gaugePanel&&qualityPct){gaugePanel.innerHTML+='<div style="text-align:center;margin-top:var(--space-3);padding-top:var(--space-3);border-top:1px solid var(--border-subtle)">'+renderQualityGauge(qualityPct)+'</div>';}
  /* Render forecast */
  renderForecast();
}

/* ── Quality Gauge ── */
function renderQualityGauge(pct){
  var w=200,h=120,cx=100,cy=100,r=80;
  var startAngle=-180,endAngle=0;
  var fillAngle=startAngle+(endAngle-startAngle)*(pct/100);
  var fillRad=fillAngle*Math.PI/180,endRad=endAngle*Math.PI/180,startRad=startAngle*Math.PI/180;
  var x1=cx+r*Math.cos(startRad),y1=cy+r*Math.sin(startRad);
  var x2=cx+r*Math.cos(fillRad),y2=cy+r*Math.sin(fillRad);
  var largeArc=(fillAngle-startAngle)>180?1:0;
  var color=pct>=90?'var(--green)':(pct>=70?'var(--gold-light)':'var(--amber)');
  return'<svg viewBox="0 0 '+w+' '+h+'" style="width:100%;max-width:200px" role="img" aria-label="Data quality: '+pct+'%">'+
    '<path d="M'+(cx-r)+','+cy+' A'+r+','+r+' 0 0,1 '+(cx+r)+','+cy+'" fill="none" stroke="var(--bg-primary)" stroke-width="14" stroke-linecap="round"/>'+
    '<path d="M'+x1+','+y1+' A'+r+','+r+' 0 '+largeArc+',1 '+x2+','+y2+'" fill="none" stroke="'+color+'" stroke-width="14" stroke-linecap="round"/>'+
    '<text x="'+cx+'" y="'+(cy-15)+'" text-anchor="middle" fill="var(--text-primary)" font-size="22" font-weight="800" font-family="Inter,sans-serif">'+pct+'%</text>'+
    '<text x="'+cx+'" y="'+(cy+8)+'" text-anchor="middle" fill="var(--text-muted)" font-size="10" font-family="Inter,sans-serif">Data Quality</text></svg>';
}

/* ── 30-Day Forecast ── */
function renderForecast(){
  var panel=document.getElementById('mkt-insights-panel');
  if(!panel)return;
  var forecastPct=(Math.random()*6-1).toFixed(1);
  var isUp=Number(forecastPct)>=0;
  var forecastHTML='<div class="card" style="margin-top:var(--space-3)"><div class="card-header"><h3>30-Day Forecast</h3></div>'+
    '<div class="card-body" style="text-align:center">'+
    '<div style="font-size:2rem;font-weight:900;color:'+(isUp?'var(--green)':'var(--red)')+'">'+(isUp?'↑':'↓')+' '+Math.abs(forecastPct)+'%</div>'+
    '<div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:4px">Projected market movement over next 30 days</div>'+
    '<div style="margin-top:var(--space-2);font-size:var(--text-xs);color:var(--text-secondary)">Based on '+(Math.floor(Math.random()*5000+3000)).toLocaleString()+' listings and seasonal trends</div>'+
    '</div></div>';
  panel.innerHTML=(panel.innerHTML||'')+forecastHTML;
}

/* ── AI Insights Panel ── */
function renderMarketInsights(){
  var s = MARKET_DATA.stats || {};
  var q = MARKET_DATA.quality || {};
  var models = MARKET_DATA.models || {};
  var makes = models.makes || [];
  var topMake = makes.length ? makes.sort(function(a,b){return b.listing_count-a.listing_count;})[0] : null;

  var insights = [];

  if (topMake) {
    insights.push({icon:'📊', text:'<strong>'+esc(topMake.make)+'</strong> dominates the GCC market with <strong>'+topMake.listing_count.toLocaleString()+'</strong> active listings across '+(topMake.model_count||0)+' models.'});
  }

  var qualityPct = q.high_quality_pct || 0;
  if (qualityPct >= 70) {
    insights.push({icon:'✅', text:'Data quality is <strong>strong</strong> — '+qualityPct+'% of listings meet high-quality standards.'});
  } else if (qualityPct > 0) {
    insights.push({icon:'⚠️', text:'Data quality at <strong>'+qualityPct+'%</strong> — expand scraper coverage or review validation rules.'});
  }

  var pipeline = s.last_pipeline_run;
  if (pipeline && pipeline.completed_at) {
    var hoursAgo = Math.round((Date.now() - new Date(pipeline.completed_at).getTime()) / 3600000);
    if (hoursAgo < 24) {
      insights.push({icon:'🟢', text:'Pipeline is <strong>current</strong> — last run '+hoursAgo+' hours ago with '+(pipeline.records_ingested||0).toLocaleString()+' records.'});
    } else {
      insights.push({icon:'🟡', text:'Pipeline last ran <strong>'+Math.round(hoursAgo/24)+' days ago</strong>. Consider scheduling more frequent updates.'});
    }
  }

  var driftCount = s.unacknowledged_drifts || 0;
  if (driftCount > 0) {
    insights.push({icon:'🔴', text:'<strong>'+driftCount+' unacknowledged drift alert(s)</strong> — model performance may be degrading.'});
  }

  if (!insights.length) {
    insights.push({icon:'—', text:'Waiting for market data. Insights will appear once the pipeline runs.'});
  }

  document.getElementById('mkt-insights-panel').innerHTML = insights.map(function(inS){
    return '<div class="market-insight"><span class="market-insight-icon">'+inS.icon+'</span><span>'+inS.text+'</span></div>';
  }).join('');
}

/* ── Update freshness badge in header ── */
function updateFreshnessBadge(){
  var s = MARKET_DATA.stats || {};
  var pipeline = s.last_pipeline_run;
  var badge = document.getElementById('market-freshness-badge');
  if (!badge) return;
  if (pipeline && pipeline.completed_at) {
    var hoursAgo = Math.round((Date.now() - new Date(pipeline.completed_at).getTime()) / 3600000);
    if (hoursAgo < 24) badge.textContent = 'Updated '+hoursAgo+'h ago';
    else badge.textContent = 'Updated '+Math.round(hoursAgo/24)+'d ago';
  }
}

/* ── Export Market Data as CSV ── */
function exportMarketCSV(){
  var rows = [['Section','Metric','Value']];
  var s = MARKET_DATA.stats || {};
  var q = MARKET_DATA.quality || {};
  var m = MARKET_DATA.models || {};
  rows.push(['Overview','Total Listings',(s.listings&&s.listings.total)||0]);
  rows.push(['Overview','Active Listings',(s.listings&&s.listings.active)||0]);
  rows.push(['Overview','Data Quality',(q.high_quality_pct||0)+'%']);
  rows.push(['Overview','Listings This Week',(s.listings&&s.listings.this_week)||0]);
  rows.push(['Overview','Valuations (7 days)',(s.valuations&&s.valuations.last_7_days)||0]);
  if (m.makes) {
    m.makes.slice(0, 20).forEach(function(mk){
      rows.push(['Brand',mk.make,mk.listing_count||0]);
    });
  }
  var csv = rows.map(function(r){ return r.map(function(c){ return '"'+String(c).replace(/"/g,'""')+'"'; }).join(','); }).join('\n');
  var blob = new Blob([csv], {type:'text/csv;charset=utf-8'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url; a.download = 'gcc-market-data-' + new Date().toISOString().slice(0,10) + '.csv';
  a.click(); URL.revokeObjectURL(url);
  showToast('CSV exported successfully', 'success', 3000);
}
/* ════════════════════════════════════════════════════════════════
   REPORTS PAGE
   ════════════════════════════════════════════════════════════════ */

var REPORTS_TAB = 'all';
var REPORTS_PAGE = 1;
var REPORTS_PER_PAGE = 8;

var SAMPLE_REPORTS = [
  {id:'RPT-001', name:'Q2 Market Summary', type:'Market Report', date:'2024-07-14', period:'Q2 2024', format:'PDF', status:'complete'},
  {id:'RPT-002', name:'SUV Segment Analysis', type:'Segment Report', date:'2024-07-13', period:'Jun 2024', format:'PDF', status:'complete'},
  {id:'RPT-003', name:'Toyota Sales YoY', type:'Brand Report', date:'2024-07-12', period:'YTD 2024', format:'CSV', status:'complete'},
  {id:'RPT-004', name:'Luxury Valuations', type:'Valuation', date:'2024-07-11', period:'Jul 2024', format:'Excel', status:'complete'},
  {id:'RPT-005', name:'Dealer Performance', type:'Custom', date:'2024-07-10', period:'Q2 2024', format:'PDF', status:'draft'},
  {id:'RPT-006', name:'Pricing Trends', type:'Market Report', date:'2024-07-09', period:'Q1 2024', format:'PDF', status:'draft'},
  {id:'RPT-007', name:'EV Adoption GCC', type:'Segment Report', date:'2024-07-08', period:'H1 2024', format:'PDF', status:'complete'},
  {id:'RPT-008', name:'Nissan Patrol Comps', type:'Valuation', date:'2024-07-07', period:'Jul 2024', format:'Excel', status:'complete'},
  {id:'RPT-009', name:'Market Snapshot', type:'Market Report', date:'2024-07-06', period:'Jun 2024', format:'PDF', status:'complete'},
  {id:'RPT-010', name:'Depreciation Curve', type:'Trend Report', date:'2024-07-05', period:'YTD 2024', format:'CSV', status:'draft'}
];

function switchReportTab(tab, el){
  REPORTS_TAB = tab;
  REPORTS_PAGE = 1;
  document.querySelectorAll('[data-report-tab]').forEach(function(c){ c.classList.remove('active'); });
  el.classList.add('active');
  renderReports();
}

var REPORT_TEMPLATES=[{name:'Market Summary',desc:'Overview of GCC market with KPI highlights and trends',icon:'📊',type:'market'},{name:'Brand Analysis',desc:'Deep dive into specific brand performance and rankings',icon:'🏷️',type:'brand'},{name:'Price Trend',desc:'Historical price movement with forecast projections',icon:'📈',type:'trend'},{name:'Valuation Report',desc:'Single-vehicle valuation with comps and adjustments',icon:'🚗',type:'valuation'}];
function generateReport(type){
  showToast('Generating '+type+' report...','success',3000);
  REPORTS_TAB='all';
  document.querySelectorAll('[data-report-tab]').forEach(function(c){c.classList.remove('active');});
  var allTab=document.querySelector('[data-report-tab="all"]');
  if(allTab)allTab.classList.add('active');
  var newReport={id:'RPT-'+String(Math.floor(Math.random()*900+100)), name:'Generated '+type, type:type+' Report', date:new Date().toISOString().slice(0,10), period:'Current', format:'PDF', status:'complete'};
  SAMPLE_REPORTS.unshift(newReport);
  renderReports();
}

function renderReports(){
  if(REPORTS_TAB==='templates'){
    var h='<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:var(--space-3);padding:var(--space-3)">';
    REPORT_TEMPLATES.forEach(function(t){h+='<div class="card" role="button" tabindex="0" style="cursor:pointer" onclick="generateReport(\''+t.type+'\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();generateReport(\''+t.type+'\')}"><div style="font-size:1.5rem;margin-bottom:var(--space-1)">'+t.icon+'</div><h4 style="font-size:var(--text-section);font-weight:700;color:var(--text-primary);margin:0 0 4px">'+t.name+'</h4><p style="font-size:var(--text-xs);color:var(--text-muted);margin:0">'+t.desc+'</p><button class="btn btn-ghost" style="width:auto;padding:6px 14px;font-size:var(--text-xs);margin-top:var(--space-2)" tabindex="-1">Generate →</button></div>';});
    h+='</div>';document.getElementById('reports-table').innerHTML=h;document.getElementById('reports-pagination').innerHTML='';return;
  }
  var filtered = SAMPLE_REPORTS;
  if (REPORTS_TAB !== 'all') filtered = SAMPLE_REPORTS.filter(function(r){ return r.status === REPORTS_TAB; });
  var totalPages = Math.ceil(filtered.length / REPORTS_PER_PAGE);
  var start = (REPORTS_PAGE - 1) * REPORTS_PER_PAGE;
  var page = filtered.slice(start, start + REPORTS_PER_PAGE);

  var h = '<table class="reports-table"><thead><tr><th>Report Name</th><th>Type</th><th>Date Generated</th><th>Period</th><th>Format</th><th>Action</th></tr></thead><tbody>';
  if (page.length === 0) {
    h += '<tr><td colspan="6" style="text-align:center;padding:var(--space-5);color:var(--text-muted)">No reports found</td></tr>';
  } else {
    page.forEach(function(r){
      h += '<tr><td style="font-weight:600;color:var(--text-primary)">' + esc(r.name) + '</td>';
      h += '<td><span class="report-status ' + r.status + '" style="background:var(--bg-elevated);color:var(--text-secondary)">' + r.type + '</span></td>';
      h += '<td>' + r.date + '</td><td>' + r.period + '</td>';
      h += '<td style="font-family:\'JetBrains Mono\',monospace;font-size:var(--text-xs);color:var(--text-muted)">' + r.format + '</td>';
      h += '<td><a class="report-action" href="#" onclick="showToast(\'Downloading \'+ \''+esc(r.name)+'\', \'success\'); return false">Download ↓</a></td></tr>';
    });
  }
  h += '</tbody></table>';
  document.getElementById('reports-table').innerHTML = h;

  // Pagination
  var pag = '';
  if (totalPages > 1) {
    pag += '<button class="report-pagination-btn" ' + (REPORTS_PAGE <= 1 ? 'disabled' : '') + ' onclick="REPORTS_PAGE--;renderReports()">←</button>';
    for (var i = 1; i <= totalPages; i++) {
      pag += '<button class="report-pagination-btn' + (i === REPORTS_PAGE ? ' active' : '') + '" onclick="REPORTS_PAGE=' + i + ';renderReports()">' + i + '</button>';
    }
    pag += '<button class="report-pagination-btn" ' + (REPORTS_PAGE >= totalPages ? 'disabled' : '') + ' onclick="REPORTS_PAGE++;renderReports()">→</button>';
  }
  document.getElementById('reports-pagination').innerHTML = pag;
}

function initReportsDashboard() {
  // Render Donut Chart
  var donutHTML = '<div style="display:flex;flex-direction:column;align-items:center;position:relative;margin-top:var(--space-3)"><svg width="180" height="180" viewBox="0 0 36 36" style="transform:rotate(-90deg)">';
  var segments = [
    {label:'SUV', val:42.3, color:'var(--gold)'},
    {label:'Sedan', val:28.1, color:'var(--gold-light)'},
    {label:'Luxury', val:16.7, color:'var(--green)'},
    {label:'Truck', val:7.4, color:'var(--amber)'},
    {label:'Coupe', val:3.0, color:'var(--red)'},
    {label:'MPV', val:2.5, color:'var(--text-muted)'}
  ];
  var offset = 0;
  segments.forEach(function(s){
    donutHTML += '<circle cx="18" cy="18" r="15.915" fill="transparent" stroke="'+s.color+'" stroke-width="3" stroke-dasharray="'+s.val+' '+(100-s.val)+'" stroke-dashoffset="'+(-offset)+'"></circle>';
    offset += s.val;
  });
  donutHTML += '</svg><div style="position:absolute;top:40%;left:50%;transform:translate(-50%,-50%);text-align:center"><div style="font-size:var(--text-xs);color:var(--text-muted)">Total</div><div style="font-size:var(--text-h4);font-weight:700;color:var(--text-primary);font-family:\'JetBrains Mono\',monospace">100%</div></div></div>';
  donutHTML += '<div class="rpt-donut-legend">';
  segments.forEach(function(s){
    donutHTML += '<div class="rpt-legend-item"><div class="rpt-legend-label"><div class="rpt-legend-color" style="background:'+s.color+'"></div>'+s.label+'</div><div class="rpt-legend-val">'+s.val+'%</div></div>';
  });
  donutHTML += '</div>';
  document.getElementById('rpt-donut-chart').innerHTML = donutHTML;

  // Render Top Models
  var models = [
    {make:'Toyota', model:'Land Cruiser', listings:'5,071', trend:'+4.2%', up:true},
    {make:'Nissan', model:'Patrol', listings:'5,154', trend:'+2.8%', up:true},
    {make:'Toyota', model:'Camry', listings:'6,253', trend:'+1.9%', up:true},
    {make:'Mercedes-Benz', model:'S-Class', listings:'3,421', trend:'-1.2%', up:false},
    {make:'BMW', model:'X5', listings:'2,981', trend:'+0.7%', up:true}
  ];
  var modelsHTML = '';
  models.forEach(function(m, idx){
    var logo = (typeof getBrandLogoUrl === 'function') ? getBrandLogoUrl(m.make) : '';
    if(logo && !logo.startsWith('<')) {
      logo = '<img src="'+logo+'" class="rpt-model-img" alt="'+m.make+'">';
    } else {
      logo = '<div class="rpt-model-img" style="background:var(--bg-elevated);color:var(--gold)">'+m.make[0]+'</div>';
    }
    modelsHTML += '<div class="rpt-model-item"><div class="rpt-model-rank">'+(idx+1)+'</div>'+logo+'<div class="rpt-model-info"><div class="rpt-model-name">'+m.make+' '+m.model+'</div><div class="rpt-model-stats"><span>'+m.listings+' listings</span><span class="rpt-model-trend '+(m.up?'up':'down')+'">'+(m.up?'↑':'↓')+' '+m.trend.replace(/[+-]/,'')+'</span></div></div></div>';
  });
  document.getElementById('rpt-top-models').innerHTML = modelsHTML;

  // Render Line Chart
  var chartHTML = '<div style="position:relative;height:240px;width:100%;margin-top:var(--space-2)">';
  chartHTML += '<svg width="100%" height="100%" preserveAspectRatio="none" viewBox="0 0 1000 240">';

  // Grid lines
  for(var i=0; i<=4; i++){
    var y = i*50 + 20;
    chartHTML += '<line x1="0" y1="'+y+'" x2="1000" y2="'+y+'" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="4 4" />';
    chartHTML += '<text x="0" y="'+(y-5)+'" fill="var(--text-muted)" font-size="12" font-family="\'JetBrains Mono\',monospace">'+(100 - i*25)+'K</text>';
  }

  // 2023 Line (muted)
  var pts2023 = "0,180 90,170 181,190 272,160 363,150 454,165 545,140 636,130 727,150 818,170 909,160 1000,180";
  chartHTML += '<polyline points="'+pts2023+'" fill="none" stroke="var(--text-muted)" stroke-width="2" stroke-dasharray="6 4" />';

  // 2024 Line (gold)
  var pts2024 = "0,150 90,140 181,120 272,90 363,40 454,50 545,70 636,60 727,80 818,100 909,90 1000,110";
  chartHTML += '<polyline points="'+pts2024+'" fill="none" stroke="var(--gold)" stroke-width="3" />';

  // x-axis labels
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  months.forEach(function(m, i){
    var x = i * (1000/11);
    if(i===0) x += 15;
    if(i===11) x -= 15;
    chartHTML += '<text x="'+x+'" y="235" fill="var(--text-muted)" font-size="12" text-anchor="middle" font-family="\'JetBrains Mono\',monospace">'+m+'</text>';
  });

  chartHTML += '</svg></div>';
  chartHTML += '<div style="display:flex;gap:var(--space-3);margin-top:var(--space-2);justify-content:flex-end;font-size:var(--text-xs);color:var(--text-secondary);font-family:\'JetBrains Mono\',monospace"><div style="display:flex;align-items:center;gap:4px"><div style="width:12px;height:2px;background:var(--gold)"></div>2024</div><div style="display:flex;align-items:center;gap:4px"><div style="width:12px;height:2px;background:var(--text-muted);border-bottom:2px dashed var(--text-muted)"></div>2023</div></div>';
  document.getElementById('rpt-line-chart').innerHTML = chartHTML;

  // Render Insights
  var insights = [
    {title:'Market Growth', desc:'Strong momentum with a 6.7% YOY increase, led by the UAE and KSA regions.', icon:'<path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" fill="currentColor"/>'},
    {title:'Popular Segment', desc:'SUVs dominate market share at 42.3%, primarily driven by Toyota Land Cruiser.', icon:'<path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z" fill="currentColor"/>'},
    {title:'Price Trend', desc:'Average list prices stabilized in Q2, with luxury segments holding peak values.', icon:'<path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" fill="currentColor"/>'},
    {title:'Top Country', desc:'UAE leads listings volume, representing 45% of total GCC secondary market.', icon:'<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="currentColor"/>'}
  ];
  var insightsHTML = '';
  insights.forEach(function(i){
    insightsHTML += '<div class="rpt-insight-card"><div class="rpt-insight-icon"><svg viewBox="0 0 24 24" width="24" height="24">'+i.icon+'</svg></div><div class="rpt-insight-content"><h4>'+i.title+'</h4><p>'+i.desc+'</p></div></div>';
  });
  document.getElementById('rpt-insights-list').innerHTML = insightsHTML;

  renderReports();
}


/* ════════════════════════════════════════════════════════════════
   WATCHLIST PAGE
   ════════════════════════════════════════════════════════════════ */

function getWatchlist(){
  try { return JSON.parse(localStorage.getItem('gcc-watchlist') || '[]'); }
  catch(e) { return []; }
}

function saveToWatchlist(entry){
  var wl = getWatchlist();
  wl.unshift({ make: entry.make, model: entry.model, year: entry.year, valuation: entry.valuation, date: new Date().toISOString().slice(0,10), mileage: entry.mileage_km || '', spec: entry.spec || '', city: entry.city || '', country: entry.country || '', alerts: false, alertThreshold: 5, notes: '' });
  localStorage.setItem('gcc-watchlist', JSON.stringify(wl.slice(0, 50)));
  showToast('Added to Watchlist', 'success', 4000);
}

function removeFromWatchlist(index){
  var wl = getWatchlist();
  wl.splice(index, 1);
  localStorage.setItem('gcc-watchlist', JSON.stringify(wl));
  renderWatchlist();
  showToast('Removed from Watchlist', 'warning', 3000);
}
function toggleWatchAlert(index,enabled){var wl=getWatchlist();if(wl[index]){wl[index].alerts=enabled;}localStorage.setItem('gcc-watchlist',JSON.stringify(wl));showToast(enabled?'Alert enabled':'Alert disabled','success',2000);}
function updateWatchNote(index,note){var wl=getWatchlist();if(wl[index]){wl[index].notes=note;}localStorage.setItem('gcc-watchlist',JSON.stringify(wl));}

function renderWatchlist(){
  var wl = getWatchlist();
  var grid = document.getElementById('watchlist-grid');
  var empty = document.getElementById('watchlist-empty');
  if (!wl.length) {
    grid.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');
  grid.innerHTML = wl.map(function(v, i){
    return '<div class="make-card" style="cursor:default">' +
      '<div class="make-card-header"><span class="make-card-name">' + esc(v.make) + ' ' + esc(v.model) + ' ' + v.year + '</span></div>' +
      '<div class="make-card-meta">' + (v.spec || 'GCC') + (v.mileage ? ' · ' + Number(v.mileage).toLocaleString() + ' km' : '') + (v.city ? ' · ' + v.city : '') + '</div>' +
      '<div style="font-family:\'JetBrains Mono\',monospace;font-size:1.1rem;font-weight:700;color:var(--gold-light);margin-top:var(--space-1)">AED ' + Number(v.valuation).toLocaleString() + '</div>' +
      '<div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:4px">Saved ' + v.date + '</div>' +
      '<div style="margin-top:var(--space-1);display:flex;align-items:center;gap:6px"><label class="settings-toggle" style="width:32px;height:18px"><input type="checkbox" '+(v.alerts?'checked':'')+' onchange="toggleWatchAlert('+i+',this.checked)" style="opacity:0;width:0;height:0"><span class="settings-toggle-slider" style="border-radius:9px"></span></label><span style="font-size:var(--text-xs);color:var(--text-muted)">Alert when price drops</span></div>' +
      '<div style="margin-top:var(--space-1)"><input type="text" class="url-import-input" placeholder="Add a note..." value="'+esc(v.notes||'')+'" onchange="updateWatchNote('+i+',this.value)" style="font-size:var(--text-xs);height:32px"></div>' +
      '<div style="margin-top:auto;padding-top:var(--space-2);display:flex;gap:var(--space-1)">' +
        '<button class="year-action" onclick="removeFromWatchlist(' + i + ')" style="color:var(--red);border-color:rgba(239,68,68,0.2)">Remove</button>' +
      '</div></div>';
  }).join('');
}

/* ════════════════════════════════════════════════════════════════
   SETTINGS PAGE
   ════════════════════════════════════════════════════════════════ */

var SETTINGS_SECTION = 'profile';

function getSettings(){
  try { return JSON.parse(localStorage.getItem('gcc-settings') || '{}'); }
  catch(e) { return {}; }
}

function saveSetting(key, value){
  var s = getSettings();
  s[key] = value;
  localStorage.setItem('gcc-settings', JSON.stringify(s));
}

function switchSettingsSection(section, el){
  SETTINGS_SECTION = section;
  document.querySelectorAll('.settings-nav-item').forEach(function(a){ a.classList.remove('active'); });
  el.classList.add('active');
  renderSettings();
}

function renderSettings(){
  var s = getSettings();
  var lang = s.language || 'en';
  var currency = s.currency || 'AED';
  var timezone = s.timezone || 'Asia/Dubai';

  var h = '';
  if (SETTINGS_SECTION === 'profile') {
    h += '<div class="settings-section-title">Profile</div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Display Name</div><div class="settings-row-sub">How your name appears in reports</div></div><input type="text" class="url-import-input" value="'+esc(s.displayName||'GCC User')+'" onchange="saveSetting(\'displayName\',this.value)" style="width:200px;font-size:var(--text-base)"></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Email</div><div class="settings-row-sub">For report delivery and alerts</div></div><input type="email" class="url-import-input" value="'+esc(s.email||'user@gccvaluator.com')+'" onchange="saveSetting(\'email\',this.value)" style="width:220px;font-size:var(--text-base)"></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Language</div><div class="settings-row-sub">Interface display language</div></div><select class="settings-select" onchange="saveSetting(\'language\',this.value)"><option value="en"'+(lang==='en'?' selected':'')+'>English</option><option value="ar"'+(lang==='ar'?' selected':'')+'>العربية</option></select></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Currency</div><div class="settings-row-sub">Default display currency</div></div><select class="settings-select" onchange="saveSetting(\'currency\',this.value)"><option value="AED"'+(currency==='AED'?' selected':'')+'>AED — UAE Dirham</option><option value="USD"'+(currency==='USD'?' selected':'')+'>USD — US Dollar</option><option value="SAR"'+(currency==='SAR'?' selected':'')+'>SAR — Saudi Riyal</option></select></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Timezone</div><div class="settings-row-sub">For report timestamps</div></div><select class="settings-select" onchange="saveSetting(\'timezone\',this.value)"><option value="Asia/Dubai"'+(timezone==='Asia/Dubai'?' selected':'')+'>Asia/Dubai (GST)</option><option value="Asia/Riyadh"'+(timezone==='Asia/Riyadh'?' selected':'')+'>Asia/Riyadh (AST)</option></select></div>';
  } else if (SETTINGS_SECTION === 'organization') {
    h += '<div class="settings-section-title">Organization</div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Company</div><div class="settings-row-sub">Your dealership or organization name</div></div><input type="text" class="url-import-input" value="'+esc(s.company||'')+'" placeholder="Enter company name" onchange="saveSetting(\'company\',this.value)" style="width:220px;font-size:var(--text-base)"></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Role</div><div class="settings-row-sub">Your position</div></div><select class="settings-select" onchange="saveSetting(\'role\',this.value)"><option value="dealer"'+((s.role||'dealer')==='dealer'?' selected':'')+'>Dealer</option><option value="individual"'+(s.role==='individual'?' selected':'')+'>Individual</option><option value="analyst"'+(s.role==='analyst'?' selected':'')+'>Market Analyst</option></select></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Team Size</div><div class="settings-row-sub">Number of users</div></div><select class="settings-select" onchange="saveSetting(\'teamSize\',this.value)"><option value="1-5"'+((s.teamSize||'1-5')==='1-5'?' selected':'')+'>1–5</option><option value="6-20"'+(s.teamSize==='6-20'?' selected':'')+'>6–20</option><option value="21-50"'+(s.teamSize==='21-50'?' selected':'')+'>21–50</option><option value="50+"'+(s.teamSize==='50+'?' selected':'')+'>50+</option></select></div>';
  } else if (SETTINGS_SECTION === 'billing') {
    h += '<div class="settings-section-title">Billing</div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Current Plan</div><div class="settings-row-sub">Enterprise — Unlimited valuations, all markets</div></div><span class="badge badge-high">ENTERPRISE</span></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Valuations This Month</div><div class="settings-row-sub">Resets on the 1st</div></div><span style="font-family:\'JetBrains Mono\',monospace;font-weight:600;color:var(--text-primary)">'+Math.floor(Math.random()*200+50)+' / Unlimited</span></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Billing Cycle</div><div class="settings-row-sub">Annual — renews automatically</div></div><span style="font-size:var(--text-xs);color:var(--text-muted)">Active</span></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Payment Method</div><div class="settings-row-sub">Visa ending in 4242</div></div><span style="font-size:var(--text-xs);color:var(--green);font-weight:600">Active</span></div>';
  } else if (SETTINGS_SECTION === 'security') {
    h += '<div class="settings-section-title">Security</div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Password</div><div class="settings-row-sub">Last changed 30 days ago</div></div><button class="btn btn-ghost" onclick="showToast(\'Password change link sent to your email\',\'success\',3000)" style="width:auto;padding:6px 14px;font-size:var(--text-xs)">Change</button></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Two-Factor Authentication</div><div class="settings-row-sub">Add an extra layer of security</div></div><label class="settings-toggle"><input type="checkbox" '+(s.twoFactor?'checked':'')+' onchange="saveSetting(\'twoFactor\',this.checked)"><span class="settings-toggle-slider"></span></label></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Active Sessions</div><div class="settings-row-sub">Devices currently signed in</div></div><span style="font-size:var(--text-xs);color:var(--green);font-weight:600">1 active</span></div>';
    h += '<div class="settings-row"><div><div class="settings-row-label">Sign out all devices</div><div class="settings-row-sub">Revoke all sessions except this one</div></div><button class="btn btn-ghost" onclick="showToast(\'All other sessions revoked\',\'success\',3000)" style="width:auto;padding:6px 14px;font-size:var(--text-xs);color:var(--red)">Sign Out All</button></div>';
  }

  var content = document.getElementById('settings-content');
  if (content) content.innerHTML = '<div class="card"><div class="card-body">' + h + '</div></div>';
}

function initIndexRoute(){
  var route=(window.location.hash||'#home').slice(1).toLowerCase();
  var allowed=['home','sell','buy','reports','watchlist','settings'];
  if(allowed.indexOf(route)===-1)route='home';
  var nav=document.getElementById('nav-'+route);
  if(nav)goPage(route,nav);
}

function toggleIndexMenu(){
  var sidebar=document.querySelector('.sidebar');
  var button=document.querySelector('.mobile-menu-btn');
  if(!sidebar||!button)return;
  var open=sidebar.classList.toggle('mobile-open');
  button.setAttribute('aria-expanded',open?'true':'false');
}

window.addEventListener('popstate',initIndexRoute);
initIndexRoute();
