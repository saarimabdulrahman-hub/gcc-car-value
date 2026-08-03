(function(){
  var demoPages=['reports.html','results.html','vehicle.html','comparables.html','report-detail.html','notifications.html'];
  var pageName=location.pathname.split('/').pop()||'index.html';
  var isDemo=demoPages.indexOf(pageName)!==-1;

  window.toast=function(message){
    if(isDemo&&/(sent|marked|opened|duplicated|archive|schedule)/i.test(message))message='This action is unavailable in preview mode';
    var el=document.createElement('div');el.className='toast';el.setAttribute('role','status');el.setAttribute('aria-live','polite');el.textContent=message;document.body.appendChild(el);setTimeout(function(){el.remove()},2600)
  };
  window.toggleMenu=function(){var n=document.querySelector('.nav');if(n)n.classList.toggle('open')};
  window.togglePassword=function(id,button){var input=document.getElementById(id);if(!input)return;input.type=input.type==='password'?'text':'password';if(button)button.textContent=input.type==='password'?'Show':'Hide'};
  window.setTab=function(group,tab){document.querySelectorAll('[data-tab-group="'+group+'"] .tab').forEach(function(b){b.classList.toggle('active',b.dataset.tab===tab)});document.querySelectorAll('[data-tab-panel="'+group+'"]').forEach(function(p){p.classList.toggle('hide',tab!=='all'&&p.dataset.panel!==tab)})};
  window.downloadReport=function(){toast('Report export is unavailable in preview mode')};
  window.sharePage=function(){if(navigator.clipboard)navigator.clipboard.writeText(location.href);toast('Link copied to clipboard')};
  window.saveVehicle=function(){toast('Watchlist saving is unavailable in preview mode')};
  window.goHome=function(){location.href='index.html'};
  if(isDemo){
    var toolbar=document.querySelector('.toolbar');
    if(toolbar){
      var state=document.createElement('div');
      state.className='preview-state';
      state.setAttribute('role','status');
      state.innerHTML='<strong>Preview data</strong><span>Not connected to a live workspace</span>';
      toolbar.insertBefore(state,toolbar.firstChild);
    }
  }
})();
