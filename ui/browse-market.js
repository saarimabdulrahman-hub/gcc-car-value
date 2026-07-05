function loadBrowseMakes(){
  var co=document.getElementById('browse-country').value;
  var url='http://localhost:8000/v1/models'; if(co) url+='?country='+co;
  fetch(url).then(function(r){return r.json()}).then(function(d){
    document.getElementById('browse-total').textContent=d.makes.length+' makes';
    var h='';
    for(var i=0;i<d.makes.length;i++){
      var m=d.makes[i];
      h+='<div class="make-card" onclick="selectMake(\''+m.make+'\')"><div style="font-weight:600">'+m.make+'</div><div style="font-size:0.72rem;color:var(--muted)">'+m.model_count+' models, '+m.listing_count+' listings</div></div>';
    }
    document.getElementById('browse-makes-grid').innerHTML=h;
    document.getElementById('browse-makes-card').style.display='block';
    document.getElementById('browse-models-card').style.display='none';
    document.getElementById('browse-years-card').style.display='none';
  });
}

function selectMake(mk){
  var co=document.getElementById('browse-country').value;
  var url='http://localhost:8000/v1/models/'+encodeURIComponent(mk); if(co) url+='?country='+co;
  fetch(url).then(function(r){return r.json()}).then(function(d){
    document.getElementById('browse-make-title').textContent=mk;
    var h='';
    for(var i=0;i<d.models.length;i++){
      var m=d.models[i];
      h+='<div class="row-link" onclick="selectModel(\''+mk+'\',\''+m.model+'\')"><div><div style="font-weight:600">'+m.model+'</div><div style="font-size:0.8rem;color:var(--muted)">'+m.year_range+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+m.listing_count+'</div></div>';
    }
    document.getElementById('browse-models-list').innerHTML=h;
    document.getElementById('browse-makes-card').style.display='none';
    document.getElementById('browse-models-card').style.display='block';
  });
}

function selectModel(mk,md){
  var co=document.getElementById('browse-country').value;
  var url='http://localhost:8000/v1/models/'+encodeURIComponent(mk)+'/'+encodeURIComponent(md); if(co) url+='?country='+co;
  fetch(url).then(function(r){return r.json()}).then(function(d){
    document.getElementById('browse-model-title').textContent=mk+' '+md;
    var h='';
    for(var i=0;i<d.years.length;i++){
      var y=d.years[i];
      h+='<div class="row-link"><div><div style="font-weight:600">'+y.year+'</div><div style="font-size:0.8rem;color:var(--muted)">'+(y.trims&&y.trims.length?y.trims.join(', '):'Standard')+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+y.listing_count+'</div></div>';
    }
    document.getElementById('browse-years-list').innerHTML=h;
    document.getElementById('browse-models-card').style.display='none';
    document.getElementById('browse-years-card').style.display='block';
  });
}

function backToMakes(){document.getElementById('browse-models-card').style.display='none';document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-makes-card').style.display='block';}
function backToModels(){document.getElementById('browse-years-card').style.display='none';document.getElementById('browse-models-card').style.display='block';}

function loadMarketPage(){
  fetch('http://localhost:8000/v1/admin/stats').then(function(r){return r.json()}).then(function(d){
    document.getElementById('mkt-total').textContent=(d.listings&&d.listings.total?d.listings.total.toLocaleString():'--');
    document.getElementById('mkt-active').textContent=(d.listings&&d.listings.active?d.listings.active.toLocaleString():'--');
    document.getElementById('mkt-week').textContent=(d.valuations&&d.valuations.last_7_days?d.valuations.last_7_days.toLocaleString():'--');
    document.getElementById('mkt-all').textContent=(d.valuations&&d.valuations.total?d.valuations.total.toLocaleString():'--');
  });
  fetch('http://localhost:8000/v1/models').then(function(r){return r.json()}).then(function(d){
    var top=d.makes.sort(function(a,b){return b.listing_count-a.listing_count;}).slice(0,10);
    var max=top[0]?top[0].listing_count:1;
    var h='';
    for(var i=0;i<top.length;i++){
      var m=top[i];
      h+='<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><span style="width:20px;color:var(--muted)">'+(i+1)+'</span><span style="flex:1">'+m.make+'</span><span style="color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</span><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';
    }
    document.getElementById('mkt-top-makes').innerHTML=h;
  });
}
