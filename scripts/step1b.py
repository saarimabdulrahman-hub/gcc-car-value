# Take step1 (working) and just add dynamic dropdowns
with open('ui/index.html', 'r', encoding='utf-8') as f:
    original = f.read()

# The step1 file was overwritten. Let me check git for it
import subprocess
result = subprocess.run(['git', 'show', 'd5fd256:ui/index.html'], capture_output=True, text=True, cwd='C:/Users/saari/projects/gcc-car-value')
step1 = result.stdout
print('Step 1 length:', len(step1))

# Just replace the hardcoded form with dynamic version + add simple buildForm
old_form_area = '''<div id="sell-form">
<div class="form-row">
<div class="form-group"><label>Make</label><select id="smake"><option value="Toyota">Toyota</option></select></div>
<div class="form-group"><label>Model</label><select id="smodel"><option value="Land Cruiser">Land Cruiser</option></select></div>
<div class="form-group"><label>Year</label><select id="syear"><option>2018</option><option>2019</option><option>2020</option></select></div>
<div class="form-group"><label>Mileage</label><input id="smileage" type="number" placeholder="80000" value="80000"></div>
</div>
</div>
<button class="btn" id="sell-btn" onclick="doValuation('sell')">Get Value</button>
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
<button class="btn" id="buy-btn" onclick="doValuation('buy')">Check Deal</button>'''

new_form_area = '''<div id="sell-form"></div>
<button class="btn" id="sell-btn" onclick="doValuation('sell')">Get Value</button>
</div>
<div id="sell-result" class="hidden"></div>
</div>
<div id="page-buy" class="hidden"><h2>Buy a Car</h2>
<div class="card"><h3>Car Details</h3>
<div id="buy-form"></div>
<button class="btn" id="buy-btn" onclick="doValuation('buy')">Check Deal</button>'''

if old_form_area in step1:
    step1 = step1.replace(old_form_area, new_form_area)
    print('Form area replaced')
else:
    print('Form area NOT found in step1')
    # Debug
    idx = step1.find('id="sell-form"')
    if idx > 0:
        print('Found at', idx)
        print(step1[idx:idx+300])
    else:
        print('sell-form not found at all')

# Now replace the doValuation function to use dynamic reads
old_doval = """async function doValuation(mode) {
  var prefix = mode === 'buy' ? 'b' : 's';
  var body = {
    make: document.getElementById(prefix+'make').value,
    model: document.getElementById(prefix+'model').value,
    year: parseInt(document.getElementById(prefix+'year').value),
    mileage_km: parseInt(document.getElementById(prefix+'mileage').value) || 80000,
    spec: 'GCC', city: 'Dubai', country: 'AE'
  };
  if (mode === 'buy') body.asking_price = parseFloat(document.getElementById('bprice').value);"""

new_doval = """var API2='http://localhost:8000/v1';
function buildForm(id, isBuy){
  var el=document.getElementById(id);
  el.innerHTML='<div class=\"form-row\"><div class=\"form-group\"><label>Make</label><select class=\"fm-make\"><option>Loading...</option></select></div><div class=\"form-group\"><label>Model</label><select class=\"fm-model\" disabled><option>Select model</option></select></div><div class=\"form-group\"><label>Year</label><select class=\"fm-year\" disabled><option>Select year</option></select></div><div class=\"form-group\"><label>Mileage</label><input type=\"number\" class=\"fm-mileage\" placeholder=\"80000\"></div></div>'+(isBuy?'<div class=\"form-row\"><div class=\"form-group\"><label>Price (AED)</label><input type=\"number\" class=\"fm-asking\" placeholder=\"125000\"></div></div>':'');
  // Wire dropdowns
  var mk=el.querySelector('.fm-make'), md=el.querySelector('.fm-model'), yr=el.querySelector('.fm-year');
  fetch(API2+'/models').then(function(r){return r.json()}).then(function(d){
    mk.innerHTML='<option value=\"\">Select make...</option>';
    d.makes.forEach(function(m){var o=document.createElement('option');o.value=m.make;o.textContent=m.make+' ('+m.listing_count+')';mk.appendChild(o);});
  });
  mk.onchange=function(){
    md.disabled=!this.value;md.innerHTML='<option>Select model</option>';yr.disabled=true;yr.innerHTML='<option>Select year</option>';
    if(!this.value)return;
    fetch(API2+'/models/'+encodeURIComponent(this.value)).then(function(r){return r.json()}).then(function(d){
      d.models.forEach(function(m){var o=document.createElement('option');o.value=m.model;o.textContent=m.model+' ('+m.year_range+')';md.appendChild(o);});
    });
  };
  md.onchange=function(){yr.disabled=false;for(var y=2026;y>=1990;y--){var o=document.createElement('option');o.value=y;o.textContent=y;yr.appendChild(o);}};
}
function readForm(el){
  var g=function(c){var e=el.querySelector(c);return e?e.value:null;};
  var mk=g('.fm-make'),md=g('.fm-model'),yr=g('.fm-year');
  if(!mk||!md||!yr)return null;
  var b={make:mk,model:md,year:parseInt(yr)};
  var mi=g('.fm-mileage');if(mi)b.mileage_km=parseInt(mi);
  b.spec='GCC';b.city='Dubai';b.country='AE';
  var ap=g('.fm-asking');if(ap)b.asking_price=parseFloat(ap);
  return b;
}
async function doValuation(mode) {
  var el=document.getElementById(mode+'-form');
  var body=readForm(el);if(!body)return alert('Please fill in make, model, and year');
  if(mode==='buy'&&!body.asking_price)return alert('Please enter the asking price');"""

if old_doval in step1:
    step1 = step1.replace(old_doval, new_doval)
    print('doValuation replaced')
else:
    print('doValuation NOT found')
    idx = step1.find('async function doValuation')
    if idx > 0:
        print(step1[idx:idx+400])

# Update goPage to call buildForm
old_go = """function goPage(p, el) {
  document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');});
  el.classList.add('active');
  document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
  var pg = document.getElementById('page-'+p);
  if(pg) pg.classList.remove('hidden');
  document.body.classList.toggle('has-sidebar', p!=='home');
}"""

new_go = """function goPage(p, el) {
  document.querySelectorAll('.sidebar-nav a').forEach(function(a){a.classList.remove('active');});
  el.classList.add('active');
  document.querySelectorAll('[id^="page-"]').forEach(function(pg){pg.classList.add('hidden');});
  var pg = document.getElementById('page-'+p);
  if(pg) pg.classList.remove('hidden');
  document.body.classList.toggle('has-sidebar', p!=='home');
  if(p==='sell')buildForm('sell-form',false);
  if(p==='buy')buildForm('buy-form',true);
}"""

if old_go in step1:
    step1 = step1.replace(old_go, new_go)
    print('goPage replaced')
else:
    print('goPage NOT found')

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(step1)
print('Step 1b written - ' + str(len(step1)) + ' chars')
