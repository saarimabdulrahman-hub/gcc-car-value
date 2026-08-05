/* Shared sidebar loader — generates the canonical GCC Car Valuator sidebar.
   Include on every standalone page: <script src="js/sidebar.js"></script>
   Injects into <aside id="sidebar"></aside>. Matches the original
   browse/market/settings/watchlist sidebar exactly (brand, nav-group,
   nav-heading, nav-item, account-card, health-card). */
(function(){
  function item(href, id, label) {
    return '<a class="nav-item" href="' + href + '"' + (id ? ' id="' + id + '"' : '') + '>' +
      '<svg class="icon"><use href="#i-' + id + '"/></svg><span data-i18n="' + id + '">' + label + '</span></a>';
  }
  var html =
    '<a class="brand" href="index.html">' +
      '<span class="brand-mark">CV</span>' +
      '<span><span class="brand-title">CAR VALUATOR</span><span class="brand-subtitle">GCC MARKET INTELLIGENCE</span></span>' +
    '</a>' +
    '<div class="sidebar-scroll"><nav>' +
      '<div class="nav-group"><div class="nav-heading">Main</div>' +
        item('index.html', 'home', 'Home') +
        item('index.html#sell', 'sell', 'Sell') +
        item('index.html#buy', 'buy', 'Buy') +
      '</div>' +
      '<div class="nav-group"><div class="nav-heading">Analysis</div>' +
        item('browse.html', 'grid', 'Browse') +
        item('market.html', 'chart', 'Market') +
        item('reports.html', 'file', 'Reports') +
        item('watchlist.html', 'star', 'Watchlist') +
      '</div>' +
      '<div class="nav-group"><div class="nav-heading">Admin</div>' +
        item('settings.html', 'gear', 'Settings') +
      '</div>' +
    '</nav></div>' +
    '<div class="sidebar-footer">' +
      '<div class="account-card"><div class="account-logo">GCC</div><div><div class="account-name">GCC Car Valuator</div><div class="account-plan">Enterprise</div></div></div>' +
      '<div class="health-card"><div class="health-title"><span class="health-dot"></span>All systems operational</div><div class="health-copy"><span class="health-pulse"></span>All services are running normally</div></div>' +
    '</div>';

  function setActive() {
    /* Normalize .html suffix so clean URLs (/reports) match nav hrefs (reports.html) */
    function norm(p) { return (p || '').replace(/\.html$/, '').replace(/\/$/, ''); }
    var path = norm(window.location.pathname.split('/').pop());
    var links = document.querySelectorAll('.sidebar-scroll .nav-item');
    for (var i = 0; i < links.length; i++) {
      var target = norm(links[i].getAttribute('href').split('#')[0]);
      if (target === path) {
        links[i].classList.add('active');
        links[i].setAttribute('aria-current', 'page');
      }
    }
  }

  function init() {
    var sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    sidebar.setAttribute('aria-label', 'Primary navigation');
    sidebar.innerHTML = html;
    setActive();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
