div><div style="font-weight:600">'+y.year+'</div><div style="font-size:0.8rem;color:var(--muted)">'+(y.trims&&y.trims.length?y.trims.join(', '):'Standard')+'</div></div><div style="font-weight:600;color:var(--gold-dark)">'+y.listing_count+'</div></div>';
    }
    document.getElementById('browse-years-list').innerHTML=html;
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
    var html='';
    for(var i=0;i<top.length;i++){
      var m=top[i];
      html+='<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sand)"><span style="width:20px;color:var(--muted)">'+(i+1)+'</span><span style="flex:1">'+m.make+'</span><span style="color:var(--muted);width:80px;text-align:right">'+m.listing_count.toLocaleString()+'</span><div class="bar-track"><div class="bar-fill" style="width:'+((m.listing_count/max)*100).toFixed(0)+'%"></div></div></div>';
    }
    document.getElementById('mkt-top-makes').innerHTML=html;
  });
}
