/* Shared EN/AR language toggle — flips RTL, persists choice, translates chrome.
 * Include on every page: <script src="js/lang.js"></script>
 * Mark translatable elements with data-i18n="key" (see I18N dictionary below).
 * The toolbar lang buttons call setLang('en'|'ar'). */
(function(){
  var I18N = {
    home:'Home', buy:'Buy', sell:'Sell', browse:'Browse', market:'Market',
    reports:'Reports', watchlist:'Watchlist', settings:'Settings',
    notifications:'Notifications', search:'Search', darkmode:'Theme',
    back:'Back to platform', signin:'Sign In', register:'Register',
    gcc:'GCC Car Valuator', enterprise:'Enterprise', allsystems:'All systems operational',
    selltitle:'I\'m Selling', buytitle:'I\'m Buying', searchph:'Search vehicles and markets'
  };
  var I18N_AR = {
    home:'الرئيسية', buy:'شراء', sell:'بيع', browse:'تصفح', market:'السوق',
    reports:'التقارير', watchlist:'المفضلة', settings:'الإعدادات',
    notifications:'الإشعارات', search:'بحث', darkmode:'المظهر',
    back:'العودة للمنصة', signin:'تسجيل الدخول', register:'إنشاء حساب',
    gcc:'مقيّم السيارات الخليجي', enterprise:'المؤسسات', allsystems:'جميع الأنظمة تعمل',
    selltitle:'أنا أبيع', buytitle:'أنا أشتري', searchph:'ابحث عن السيارات والأسواق'
  };
  function dict(lang){ return lang === 'ar' ? I18N_AR : I18N; }
  function translate(lang){
    var d = dict(lang);
    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++){
      var key = els[i].getAttribute('data-i18n');
      if (d[key] !== undefined) els[i].textContent = d[key];
    }
  }
  function setActive(lang){
    document.querySelectorAll('[data-lang-btn]').forEach(function(b){
      b.classList.toggle('active', b.getAttribute('data-lang-btn') === lang);
    });
  }
  window.setLang = function(lang){
    lang = (lang === 'ar') ? 'ar' : 'en';
    document.documentElement.lang = lang;
    document.body.dir = (lang === 'ar') ? 'rtl' : 'ltr';
    translate(lang);
    setActive(lang);
    try { localStorage.setItem('gcc-lang', lang); } catch(e) { console.warn('lang: localStorage write failed', e); }
    return lang;
  };
  window.toggleLang = function(){
    var cur = document.documentElement.lang === 'ar' ? 'ar' : 'en';
    return window.setLang(cur === 'ar' ? 'en' : 'ar');
  };
  function applySaved(){
    var saved = null;
    try { saved = localStorage.getItem('gcc-lang'); } catch(e) { console.warn('lang: localStorage read failed', e); }
    if (saved === 'ar' || saved === 'en') window.setLang(saved);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applySaved);
  } else {
    applySaved();
  }
})();
