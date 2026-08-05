/* Shared sidebar loader — include on every standalone page.
   Injects the standard GCC Car Valuator sidebar with SVG sprite icons.
   Usage: <script src="js/sidebar.js"></script>
   The sidebar needs: <aside id="sidebar"></aside> and an SVG sprite sheet. */
(function(){
  var html='<div class="sidebar-brand"><div class="sidebar-logo">CV</div><div class="sidebar-titles"><span class="sidebar-name">CAR VALUATOR</span><span class="sidebar-subtitle">GCC MARKET INTELLIGENCE</span></div></div>';
  html+='<nav class="sidebar-nav" aria-label="Primary navigation">';
  html+='<div class="sidebar-section-label">Main</div>';
  html+='<a href="index.html"><svg class="nav-icon" width="18" height="18"><use href="#i-home"/></svg> Home</a>';
  html+='<a href="index.html#sell"><svg class="nav-icon" width="18" height="18"><use href="#i-sell"/></svg> Sell</a>';
  html+='<a href="index.html#buy"><svg class="nav-icon" width="18" height="18"><use href="#i-buy"/></svg> Buy</a>';
  html+='<div class="sidebar-section-label">Analysis</div>';
  html+='<a href="browse.html"><svg class="nav-icon" width="18" height="18"><use href="#i-grid"/></svg> Browse</a>';
  html+='<a href="market.html"><svg class="nav-icon" width="18" height="18"><use href="#i-chart"/></svg> Market</a>';
  html+='<a href="reports.html"><svg class="nav-icon" width="18" height="18"><use href="#i-file"/></svg> Reports</a>';
  html+='<a href="watchlist.html"><svg class="nav-icon" width="18" height="18"><use href="#i-star"/></svg> Watchlist</a>';
  html+='<div class="sidebar-section-label">Admin</div>';
  html+='<a href="settings.html"><svg class="nav-icon" width="18" height="18"><use href="#i-gear"/></svg> Settings</a>';
  html+='</nav>';
  html+='<div class="sidebar-footer"><div class="sidebar-profile"><div class="profile-avatar">GCC</div><div class="profile-info"><div class="profile-name">GCC Car Valuator</div><div class="profile-plan">Enterprise</div></div></div><div class="sidebar-system-health"><div class="health-dot"></div><span class="health-label">All systems operational</span></div></div>';

  function setActive(){
    var path=window.location.pathname.replace(/\/$/,'').split('/').pop()||'index.html';
    var links=document.querySelectorAll('.sidebar-nav a');
    for(var i=0;i<links.length;i++){
      var href=links[i].getAttribute('href');
      if(href===path||(path===''&&href==='index.html')){
        links[i].classList.add('active');
        links[i].setAttribute('aria-current','page');
      }
    }
  }

  function init(){
    var sidebar=document.getElementById('sidebar');
    if(!sidebar) return;
    sidebar.setAttribute('aria-label','Main navigation');
    sidebar.innerHTML=html;
    setActive();
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init);
  else init();
})();
