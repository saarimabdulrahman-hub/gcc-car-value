"""Replace make/model dropdowns with smart autocomplete search."""
with open('ui/index.html', 'rb') as f:
    t = f.read()

# Add autocomplete CSS
css = b'''
.autocomplete-wrap{position:relative}
.autocomplete-suggestions{position:absolute;top:100%;left:0;right:0;background:#fff;border:1.5px solid var(--gold);border-top:none;border-radius:0 0 10px 10px;max-height:200px;overflow-y:auto;z-index:100;display:none;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
.autocomplete-suggestions.show{display:block}
.autocomplete-item{padding:10px 14px;cursor:pointer;font-size:0.9rem;border-bottom:1px solid var(--sand)}
.autocomplete-item:hover,.autocomplete-item.active{background:#FEF9EE;color:var(--gold-dark)}
.autocomplete-item .count{float:right;color:var(--muted);font-size:0.75rem}
'''
t = t.replace(b'</style>', css + b'</style>')

# Add autocomplete JS before </script>
js = b'''
var ALL_MAKES=[];
fetch('http://localhost:8000/v1/models').then(function(r){return r.json()}).then(function(d){ALL_MAKES=d.makes;});

function autocomplete(input, type){
  var wrap=input.parentElement;
  var sug=wrap.querySelector('.autocomplete-suggestions');
  var val=input.value.toLowerCase();
  sug.innerHTML='';
  if(!val){sug.classList.remove('show');return;}

  if(type==='make'){
    var matches=ALL_MAKES.filter(function(m){return m.make.toLowerCase().indexOf(val)>=0;}).slice(0,8);
    matches.forEach(function(m){
      var div=document.createElement('div');
      div.className='autocomplete-item';
      div.innerHTML=m.make+' <span class=\"count\">'+m.listing_count+'</span>';
      div.onclick=function(){input.value=m.make;sug.classList.remove('show');var form=input.closest('[id$=\"-form\"]');if(form){var mdl=form.querySelector('.fm-model');if(mdl){mdl.disabled=false;mdl.value='';mdl.placeholder='Type model...';}}};
      sug.appendChild(div);
    });
  }else{
    var makeInput=input.closest('[id$=\"-form\"]').querySelector('.fm-make');
    var mk=makeInput?makeInput.value:'';
    if(!mk)return;
    fetch('http://localhost:8000/v1/models/'+encodeURIComponent(mk)).then(function(r){return r.json()}).then(function(d){
      var matches=d.models.filter(function(m){return m.model.toLowerCase().indexOf(val)>=0;}).slice(0,8);
      matches.forEach(function(m){
        var div=document.createElement('div');
        div.className='autocomplete-item';
        div.innerHTML=m.model+' <span class=\"count\">'+m.year_range+'</span>';
        div.onclick=function(){input.value=m.model;sug.classList.remove('show');var form=input.closest('[id$=\"-form\"]');if(form){var yr=form.querySelector('.fm-year');if(yr){yr.disabled=false;if(yr.options.length<=1)for(var y=2026;y>=1990;y--){var o=document.createElement('option');o.value=y;o.textContent=y;yr.appendChild(o);}}}};
        sug.appendChild(div);
      });
    });
  }
  sug.classList.add('show');
  // Close on outside click
  setTimeout(function(){
    document.addEventListener('click',function closeSuggest(e){if(!wrap.contains(e.target)){sug.classList.remove('show');document.removeEventListener('click',closeSuggest);}});
  },100);
}
'''
t = t.replace(b'</script>', js + b'</script>')

# Remove the old wireDropdowns/wireForm/initForm functions that reference .fm-make as select
# and replace with simpler versions that work with inputs
# Update readForm to get values from inputs
t = t.replace(
    b"var g=function(c){var e=el.querySelector(c);return e?e.value:null;};",
    b"var g=function(c){var e=el.querySelector(c);return e?e.value:null;};"
)

# Update initForm/buildForm to use the new autocomplete HTML
# The makeForm function in the JS already generates HTML - we need to update it
# Find and replace the hardcoded form HTML in makeForm
old_form_start = b"function makeForm(showAsking){"
if old_form_start in t:
    idx = t.find(old_form_start)
    end = t.find(b"\n}", idx) + 2
    new_form = b"""function makeForm(showAsking){
var h='<div class="form-row"><div class="form-group"><label>Make</label><div class="autocomplete-wrap"><input type="text" class="fm-make" placeholder="Type make..." autocomplete="off" oninput="autocomplete(this,\\'make\\')" onfocus="autocomplete(this,\\'make\\')"><div class="autocomplete-suggestions"></div></div></div><div class="form-group"><label>Model</label><div class="autocomplete-wrap"><input type="text" class="fm-model" placeholder="Type model..." autocomplete="off" disabled oninput="autocomplete(this,\\'model\\')" onfocus="autocomplete(this,\\'model\\')"><div class="autocomplete-suggestions"></div></div></div><div class="form-group"><label>Year</label><select class="fm-year" disabled><option>Select year</option></select></div></div><div class="form-row"><div class="form-group"><label>Mileage (km)</label><input type="number" class="fm-mileage" placeholder="e.g. 80000"></div><div class="form-group"><label>Spec</label><select class="fm-spec"><option value="">Any</option><option value="GCC">GCC</option><option value="US">US</option><option value="Japan">Japan</option><option value="European">European</option></select></div><div class="form-group"><label>City</label><select class="fm-city"><option value="">Any</option><option>Dubai</option><option>Abu Dhabi</option><option>Sharjah</option><option>Riyadh</option><option>Jeddah</option><option>Dammam</option><option>Kuwait City</option><option>Doha</option><option>Muscat</option></select></div><div class="form-group"><label>Country</label><select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select></div></div>';
if(showAsking)h='<div style="background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)"><div style="font-size:0.85rem;font-weight:700;color:var(--gold-dark);margin-bottom:8px">What\\'s the asking price?</div><div style="display:flex;align-items:center;gap:12px"><input type="number" class="fm-asking" placeholder="Enter the price" style="flex:1;padding:16px;border:2px solid var(--gold);border-radius:10px;font-size:1.2rem;font-weight:700;background:#fff;color:var(--brown);font-family:inherit"><span style="font-size:1.1rem;font-weight:700;color:var(--gold-dark)">AED</span></div></div><h3 style="border:none;padding:0;margin:0 0 16px 0;font-size:0.85rem;color:var(--muted);text-transform:uppercase">Car Details</h3>'+h;
return h;
}"""
    t = t[:idx] + new_form + t[end:]

# Remove old initForm/wireDropdowns functions that are no longer needed
# (keep them but they won't do much since we use autocomplete now)

with open('ui/index.html', 'wb') as f:
    f.write(t)
print('Autocomplete added. Braces:', t.count(b'{')-t.count(b'}'))
