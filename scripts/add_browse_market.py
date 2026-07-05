"""Add Browse and Market pages to working index.html."""

with open('ui/index.html', 'rb') as f:
    data = f.read()

# Step 1: Add HTML divs before </div></div>\r\n\r\n<script>
marker = b'</div></div>\r\n\r\n<script>'
pos = data.find(marker)

html_insert = (
    b'<div id="page-browse" class="hidden"><h2 class="page-title">Browse Models</h2>'
    b'<p class="page-sub">Explore every make and model.</p>'
    b'<div class="card" style="padding:16px 28px;margin-bottom:16px">'
    b'<select id="browse-country" onchange="loadBrowseMakes()" style="padding:8px 12px;border:1.5px solid var(--border);border-radius:8px;font-family:inherit;background:#FEFCF7">'
    b'<option value="">All GCC</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option>'
    b'<option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option>'
    b'</select><span id="browse-total" style="font-size:0.8rem;color:var(--muted);margin-left:12px"></span></div>'
    b'<div class="card" id="browse-makes-card"><div id="browse-makes-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px"></div></div>'
    b'<div class="card" id="browse-models-card" style="display:none"><button onclick="backToMakes()" class="back-btn">Back</button>'
    b'<span id="browse-make-title" style="font-weight:600;color:var(--gold-dark);margin-left:8px"></span><div id="browse-models-list" style="margin-top:12px"></div></div>'
    b'<div class="card" id="browse-years-card" style="display:none"><button onclick="backToModels()" class="back-btn">Back</button>'
    b'<span id="browse-model-title" style="font-weight:600;color:var(--gold-dark);margin-left:8px"></span><div id="browse-years-list" style="margin-top:12px"></div></div></div>'
    b'\r\n'
    b'<div id="page-market" class="hidden"><h2 class="page-title">Market Trends</h2>'
    b'<p class="page-sub">Gulf used car market overview.</p>'
    b'<div class="card"><div class="stat-bar" style="margin-top:0;padding-top:0;border-top:none">'
    b'<div class="stat"><div class="n" id="mkt-total">--</div><div class="l">Total Listings</div></div>'
    b'<div class="stat"><div class="n" id="mkt-active">--</div><div class="l">Active</div></div>'
    b'<div class="stat"><div class="n" id="mkt-week">--</div><div class="l">Valuations (7d)</div></div>'
    b'<div class="stat"><div class="n" id="mkt-all">--</div><div class="l">All-Time</div></div>'
    b'</div></div>'
    b'<div class="card"><h3>Most Popular Makes</h3><div id="mkt-top-makes"></div></div></div>'
    b'\r\n'
)

data = data[:pos] + html_insert + data[pos:]

# Step 2: Add JS functions before </script>
script_end = data.rfind(b'</script>')

js_insert = (
    b'\r\n'
    b'function loadBrowseMakes(){\r\n'
    b'  var co=document.getElementById("browse-country").value;\r\n'
    b'  var url="http://localhost:8000/v1/models"; if(co) url+="?country="+co;\r\n'
    b'  fetch(url).then(function(r){return r.json()}).then(function(d){\r\n'
    b'    document.getElementById("browse-total").textContent=d.makes.length+" makes";\r\n'
    b'    var h=""; for(var i=0;i<d.makes.length;i++){var m=d.makes[i];h+='\''<div class="make-card" onclick="selectMake(\\'\''+m.make+'\\'\')"><div style="font-weight:600">'\''+m.make+'\''</div><div style="font-size:0.72rem;color:var(--muted)">'\''+m.model_count+'\'' models, '\''+m.listing_count+'\'' listings</div></div>'\'';}\r\n'
    b'    document.getElementById("browse-makes-grid").innerHTML=h;\r\n'
    b'    document.getElementById("browse-makes-card").style.display="block";\r\n'
    b'    document.getElementById("browse-models-card").style.display="none";\r\n'
    b'    document.getElementById("browse-years-card").style.display="none";\r\n'
    b'  });\r\n'
    b'}\r\n'
    b'function selectMake(mk){\r\n'
    b'  var co=document.getElementById("browse-country").value;\r\n'
    b'  var url="http://localhost:8000/v1/models/"+encodeURIComponent(mk); if(co) url+="?country="+co;\r\n'
    b'  fetch(url).then(function(r){return r.json()}).then(function(d){\r\n'
    b'    document.getElementById("browse-make-title").textContent=mk;\r\n'
    b'    var h=""; for(var i=0;i<d.models.length;i++){var m=d.models[i];h+='\''<div class="row-link" onclick="selectModel(\\'\''+mk+'\\'\'',\\'\''+m.model+'\\'\')"><div><div style="font-weight:600">'\''+m.model+'\''</div><div style="font-size:0.8rem;color:var(--muted)">'\''+m.year_range+'\''</div></div><div style="font-weight:600;color:var(--gold-dark)">'\''+m.listing_count+'\''</div></div>'\'';}\r\n'
    b'    document.getElementById("browse-models-list").innerHTML=h;\r\n'
    b'    document.getElementById("browse-makes-card").style.display="none";\r\n'
    b'    document.getElementById("browse-models-card").style.display="block";\r\n'
    b'  });\r\n'
    b'}\r\n'
    b'function selectModel(mk,md){\r\n'
    b'  var co=document.getElementById("browse-country").value;\r\n'
    b'  var url="http://localhost:8000/v1/models/"+encodeURIComponent(mk)+"/"+encodeURIComponent(md); if(co) url+="?country="+co;\r\n'
    b'  fetch(url).then(function(r){return r.json()}).then(function(d){\r\n'
    b'    document.getElementById("browse-model-title").textContent=mk+" "+md;\r\n'
    b'    var h=""; for(var i=0;i<d.years.length;i++){var y=d.years[i];h+='\''<div class="row-link"><div><div style="font-weight:600">'\''+y.year+'\''</div><div style="font-size:0.8rem;color:var(--muted)">'\''+(y.trims&&y.trims.length?y.trims.join(", "):"Standard")+'\''</div></div><div style="font-weight:600;color:var(--gold-dark)">'\''+y.listing_count+'\''</div></div>'\'';}\r\n'
    b'    document.getElementById("browse-years-list").innerHTML=h;\r\n'
    b'    document.getElementById("browse-models-card").style.display="none";\r\n'
    b'    document.getElementById("browse-years-card").style.display="block";\r\n'
    b'  });\r\n'
    b'}\r\n'
    b'function backToMakes(){document.getElementById("browse-models-card").style.display="none";document.getElementById("browse-years-card").style.display="none";document.getElementById("browse-makes-card").style.display="block";}\r\n'
    b'function backToModels(){document.getElementById("browse-years-card").style.display="none";document.getElementById("browse-models-card").style.display="block";}\r\n'
    b'\r\n'
    b'function loadMarketPage(){\r\n'
    b'  fetch("http://localhost:8000/v1/admin/stats").then(function(r){return r.json()}).then(function(d){\r\n'
    b'    document.getElementById("mkt-total").textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():"--");\r\n'
    b'    document.getElementById("mkt-active").textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():"--");\r\n'
    b'    document.getElementById("mkt-week").textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():"--");\r\n'
    b'    document.getElementById("mkt-all").textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():"--");\r\n'
    b'  });\r\n'
    b'  fetch("http://localhost:8000/v1/models").then(function(r){return r.json()}).then(function(d){\r\n'
    b'    var top=d.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);\r\n'
    b'    var max=top[0]?top[0].listing_count:1;\r\n'
    b'    var h=""; for(var i=0;i<top.length;i++){var m=top[i];h+='\''<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><span style="width:20px;color:var(--muted)">'\''+(i+1)+'\''</span><span style="flex:1">'\''+m.make+'\''</span><span style="color:var(--muted);width:80px;text-align:right">'\''+m.listing_count.toLocaleString()+'\''</span><div class="bar-track"><div class="bar-fill" style="width:"+((m.listing_count/max)*100).toFixed(0)+"%"></div></div></div>'\'';}\r\n'
    b'    document.getElementById("mkt-top-makes").innerHTML=h;\r\n'
    b'  });\r\n'
    b'}\r\n'
)

data = data[:script_end] + js_insert + data[script_end:]

# Step 3: Wire goPage
old = b"if (p === 'home') document.body.classList.remove('has-sidebar');"
new = b"if(p==='home')document.body.classList.remove('has-sidebar');else document.body.classList.add('has-sidebar');if(p==='browse')loadBrowseMakes();if(p==='market')loadMarketPage();"
data = data.replace(old, new)

with open('ui/index.html', 'wb') as f:
    f.write(data)

print('Done. Size:', len(data))
print('Has goPage:', b'function goPage(p, el)' in data)
print('Has loadBrowseMakes:', b'function loadBrowseMakes()' in data)
print('Has loadMarketPage:', b'function loadMarketPage()' in data)
