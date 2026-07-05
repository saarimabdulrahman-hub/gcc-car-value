"""Add autocomplete function back + fix doValuation for input fields"""
with open('ui/index.html', 'rb') as f:
    t = f.read()

# 1. Add autocomplete CSS
css = b'''
.autocomplete-wrap{position:relative}
.autocomplete-suggestions{position:absolute;top:100%;left:0;right:0;background:#fff;border:1.5px solid var(--gold);border-top:none;border-radius:0 0 10px 10px;max-height:200px;overflow-y:auto;z-index:100;display:none;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
.autocomplete-suggestions.show{display:block}
.autocomplete-item{padding:10px 14px;cursor:pointer;font-size:0.9rem;border-bottom:1px solid var(--sand)}
.autocomplete-item:hover{background:#FEF9EE;color:var(--gold-dark)}
.autocomplete-item .count{float:right;color:var(--muted);font-size:0.75rem}
'''
if b'.autocomplete-wrap' not in t:
    t = t.replace(b'</style>', css + b'</style>')

# 2. Add autocomplete JS + fix doValuation before </script>
fixes = b'''
var ALL_MAKES=[];
fetch('http://localhost:8000/v1/models').then(function(r){return r.json()}).then(function(d){ALL_MAKES=d.makes;});

function autocomplete(input){
  var wrap=input.parentElement;
  if(!wrap.classList.contains('autocomplete-wrap')) return;
  var sug=wrap.querySelector('.autocomplete-suggestions');
  if(!sug) return;
  var val=input.value.toLowerCase();
  sug.innerHTML='';
  if(!val){sug.classList.remove('show');return;}
  if(input.classList.contains('fm-make')){
    var matches=ALL_MAKES.filter(function(m){return m.make.toLowerCase().indexOf(val)>=0;}).slice(0,8);
    matches.forEach(function(m){var d=document.createElement('div');d.className='autocomplete-item';d.innerHTML=m.make+' <span class=\"count\">'+m.listing_count+'</span>';d.onclick=function(){input.value=m.make;sug.classList.remove('show');var form=input.closest('[id$=\"-form\"]')||input.closest('.card');if(form){var mdl=form.querySelector('.fm-model');if(mdl){mdl.disabled=false;mdl.value='';mdl.placeholder='Type model...';}}};sug.appendChild(d);});
  }else if(input.classList.contains('fm-model')){
    var form=input.closest('[id$=\"-form\"]')||input.closest('.card');
    if(!form) return;
    var mkInput=form.querySelector('.fm-make');
    var mk=mkInput?mkInput.value:'';
    if(!mk)return;
    fetch('http://localhost:8000/v1/models/'+encodeURIComponent(mk)).then(function(r){return r.json()}).then(function(d){
      var matches=d.models.filter(function(m){return m.model.toLowerCase().indexOf(val)>=0;}).slice(0,8);
      matches.forEach(function(m){var div=document.createElement('div');div.className='autocomplete-item';div.innerHTML=m.model+' <span class=\"count\">'+m.year_range+'</span>';div.onclick=function(){input.value=m.model;sug.classList.remove('show');};sug.appendChild(div);});
    });
  }
  sug.classList.add('show');
  setTimeout(function(){document.addEventListener('click',function closeSuggest(e){if(!wrap.contains(e.target)){sug.classList.remove('show');document.removeEventListener('click',closeSuggest);}});},100);
}

// Override doValuation to use class-based selectors
var _origDoValuation = doValuation;
doValuation = async function(mode) {
  var formEl = document.getElementById(mode+'-form');
  if(!formEl) { showError('Form not found'); return; }
  var g = function(cls) { var el = formEl.querySelector('.'+cls); return el ? el.value : null; };
  var mk = g('fm-make') || g('fm-make');
  var md = g('fm-model');
  var yr = g('fm-year');
  if(!mk || !md || !yr) { showWarning('Please fill in make, model, and year'); return; }
  var body = { make: mk, model: md, year: parseInt(yr) };
  var mi = g('fm-mileage'); if(mi) body.mileage_km = parseInt(mi);
  var sp = g('fm-spec'); if(sp) body.spec = sp;
  var ci = g('fm-city'); if(ci) body.city = ci;
  var co = g('fm-country'); if(co) { var cm={'UAE':'AE','Saudi Arabia':'SA','Saudi':'SA','Kuwait':'KW','Qatar':'QA','Bahrain':'BH','Oman':'OM','AE':'AE','SA':'SA','KW':'KW','QA':'QA','BH':'BH','OM':'OM'}; body.country = cm[co] || co; }
  if(mode==='buy') {
    var urlMode = document.getElementById('tab-url');
    if(urlMode && urlMode.classList.contains('active')) {
      var urlEl = formEl.querySelector('.fm-url') || document.getElementById('fm-url');
      if(urlEl && urlEl.value) return doUrlValuation(urlEl.value);
    }
    var ap = g('fm-asking'); if(ap) body.asking_price = parseFloat(ap);
  }

  var ld=document.getElementById(mode+'-loading'); if(ld)ld.classList.remove('hidden');
  var rs=document.getElementById(mode+'-results'); if(rs)rs.classList.add('hidden');
  var er=document.getElementById(mode+'-error'); if(er)er.classList.add('hidden');
  var bt=document.getElementById(mode+'-btn'); if(bt)bt.disabled=true;
  try {
    var r = await fetch('http://localhost:8000/v1/valuate', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    if(!r.ok) { var e = await r.json(); throw new Error(e.detail||'Failed'); }
    if(ld)ld.classList.add('hidden');
    showResults(mode, await r.json(), body);
  } catch(e) {
    if(ld)ld.classList.add('hidden');
    if(er) { er.classList.remove('hidden'); er.innerHTML='<div class=\"error-msg\">'+e.message+'</div>'; }
    else { showError(e.message); }
  } finally { if(bt) bt.disabled = false; }
};
'''
t = t.replace(b'</script>', fixes + b'</script>')

print('Braces:', t.count(b'{')-t.count(b'}'))
with open('ui/index.html', 'wb') as f:
    f.write(t)
