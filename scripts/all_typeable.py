"""Replace ALL dropdowns with autocomplete typeable fields."""
with open('ui/index.html', 'rb') as f:
    t = f.read()

# 1. Replace makeForm function
old_form = b'function makeForm(showAsking){'
idx = t.find(old_form)

new_form = (
    b'function makeForm(showAsking){'
    b"var h='<div class=\"form-row\">"
    b'<div class="form-group"><label>Make</label><div class="autocomplete-wrap"><input type="text" class="fm-make" placeholder="Type make..." autocomplete="off" oninput="autocomplete(this)" onfocus="autocomplete(this)"><div class="autocomplete-suggestions"></div></div></div>'
    b'<div class="form-group"><label>Model</label><div class="autocomplete-wrap"><input type="text" class="fm-model" placeholder="Type model..." autocomplete="off" disabled oninput="autocomplete(this)" onfocus="autocomplete(this)"><div class="autocomplete-suggestions"></div></div></div>'
    b'<div class="form-group"><label>Year</label><input type="number" class="fm-year" placeholder="e.g. 2020" min="1990" max="2026"></div>'
    b'<div class="form-group"><label>Mileage (km)</label><input type="number" class="fm-mileage" placeholder="e.g. 80000"></div>'
    b'</div><div class="form-row">'
    b'<div class="form-group"><label>Spec</label><div class="autocomplete-wrap"><input type="text" class="fm-spec" placeholder="GCC, US, Japan..." autocomplete="off" oninput="autocomplete(this)" onfocus="autocomplete(this)"><div class="autocomplete-suggestions"></div></div></div>'
    b'<div class="form-group"><label>City</label><div class="autocomplete-wrap"><input type="text" class="fm-city" placeholder="Dubai, Riyadh..." autocomplete="off" oninput="autocomplete(this)" onfocus="autocomplete(this)"><div class="autocomplete-suggestions"></div></div></div>'
    b'<div class="form-group"><label>Country</label><div class="autocomplete-wrap"><input type="text" class="fm-country" placeholder="UAE, Saudi..." autocomplete="off" oninput="autocomplete(this)" onfocus="autocomplete(this)"><div class="autocomplete-suggestions"></div></div></div>'
    b"</div>';"
    b"if(showAsking)h='<div style=\"background:linear-gradient(135deg,#FEF9EE,#FFF8E1);border-radius:12px;padding:20px;margin-bottom:20px;border:2px solid var(--gold)\"><div style=\"font-size:0.85rem;font-weight:700;color:var(--gold-dark);margin-bottom:8px\">What\\'s the asking price?</div><div style=\"display:flex;align-items:center;gap:12px\"><input type=\"number\" class=\"fm-asking\" placeholder=\"Enter the price\" style=\"flex:1;padding:16px;border:2px solid var(--gold);border-radius:10px;font-size:1.2rem;font-weight:700;background:#fff;color:var(--brown);font-family:inherit\"><span style=\"font-size:1.1rem;font-weight:700;color:var(--gold-dark)\">AED</span></div></div><h3 style=\"border:none;padding:0;margin:0 0 16px 0;font-size:0.85rem;color:var(--muted);text-transform:uppercase\">Car Details</h3>'+h;"
    b"return h;"
    b"}\n"
)

# Find end of current makeForm (next function)
end = t.find(b'\nfunction loadBrowseMakes', idx)
if end < 0:
    end = t.find(b'\nfunction toggleLang', idx)
t = t[:idx] + new_form + t[end:]

# 2. Update autocomplete function to handle all field types
old_auto = b'function autocomplete(input, type){'
idx2 = t.find(old_auto)
# Find end of autocomplete
end2 = t.find(b'\n// Close on outside click', idx2)
if end2 < 0:
    end2 = t.find(b'\n}\n', idx2 + 200) + 2

new_auto = (
    b'function autocomplete(input){'
    b'var wrap=input.parentElement;var sug=wrap.querySelector(".autocomplete-suggestions");'
    b'var val=input.value.toLowerCase();sug.innerHTML="";'
    b'if(!val){sug.classList.remove("show");return;}'
    b'if(input.classList.contains("fm-make")){'
    b'var matches=ALL_MAKES.filter(function(m){return m.make.toLowerCase().indexOf(val)>=0;}).slice(0,8);'
    b'matches.forEach(function(m){var d=document.createElement("div");d.className="autocomplete-item";d.innerHTML=m.make+" <span class=\\"count\\">"+m.listing_count+"</span>";d.onclick=function(){input.value=m.make;sug.classList.remove("show");var form=input.closest(\'[id$="-form"]\');if(form){var mdl=form.querySelector(".fm-model");if(mdl){mdl.disabled=false;mdl.value="";mdl.placeholder="Type model...";}}};sug.appendChild(d);});'
    b'}else if(input.classList.contains("fm-model")){'
    b'var form=input.closest(\'[id$="-form"]\');var mk=form?form.querySelector(".fm-make").value:"";if(!mk)return;'
    b'fetch("http://localhost:8000/v1/models/"+encodeURIComponent(mk)).then(function(r){return r.json()}).then(function(d){'
    b'var matches=d.models.filter(function(m){return m.model.toLowerCase().indexOf(val)>=0;}).slice(0,8);'
    b'matches.forEach(function(m){var div=document.createElement("div");div.className="autocomplete-item";div.innerHTML=m.model+" <span class=\\"count\\">"+m.year_range+"</span>";div.onclick=function(){input.value=m.model;sug.classList.remove("show");};sug.appendChild(div);});'
    b'});'
    b'}else if(input.classList.contains("fm-spec")){'
    b'["GCC","US","Japan","European"].filter(function(s){return s.toLowerCase().indexOf(val)>=0;}).forEach(function(s){var d=document.createElement("div");d.className="autocomplete-item";d.textContent=s;d.onclick=function(){input.value=s;sug.classList.remove("show");};sug.appendChild(d);});'
    b'}else if(input.classList.contains("fm-city")){'
    b'["Dubai","Abu Dhabi","Sharjah","Riyadh","Jeddah","Dammam","Kuwait City","Doha","Muscat","Manama"].filter(function(s){return s.toLowerCase().indexOf(val)>=0;}).forEach(function(s){var d=document.createElement("div");d.className="autocomplete-item";d.textContent=s;d.onclick=function(){input.value=s;sug.classList.remove("show");};sug.appendChild(d);});'
    b'}else if(input.classList.contains("fm-country")){'
    b'[{v:"AE",l:"UAE"},{v:"SA",l:"Saudi Arabia"},{v:"KW",l:"Kuwait"},{v:"QA",l:"Qatar"},{v:"BH",l:"Bahrain"},{v:"OM",l:"Oman"}].filter(function(s){return s.l.toLowerCase().indexOf(val)>=0||s.v.toLowerCase().indexOf(val)>=0;}).forEach(function(s){var d=document.createElement("div");d.className="autocomplete-item";d.innerHTML=s.l+" <span class=\\"count\\">"+s.v+"</span>";d.onclick=function(){input.value=s.v;sug.classList.remove("show");};sug.appendChild(d);});'
    b'}'
    b'sug.classList.add("show");'
    b'setTimeout(function(){document.addEventListener("click",function closeSuggest(e){if(!wrap.contains(e.target)){sug.classList.remove("show");document.removeEventListener("click",closeSuggest);}});},100);'
    b'}\n'
)

t = t[:idx2] + new_auto + t[idx2 + len(old_auto):]

# 3. Update readForm - city and country are now text inputs, need to read correctly
t = t.replace(
    b"var sp=g('.fm-spec');if(sp)b.spec=sp; var ci=g('.fm-city');if(ci)b.city=ci; var co=g('.fm-country');if(co)b.country=co;",
    b"var sp=g('.fm-spec');if(sp)b.spec=sp;var ci=g('.fm-city');if(ci)b.city=ci;var co=g('.fm-country');if(co)b.country=co;"
)

with open('ui/index.html', 'wb') as f:
    f.write(t)
print('Done. Braces:', t.count(b'{')-t.count(b'}'))
