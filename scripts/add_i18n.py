"""Inject i18n translations into index.html"""
with open('ui/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Add RTL and lang support to :root CSS
rtl_css = '''
/* ── RTL Support ── */
[dir="rtl"] .sidebar{border-left:none;border-right:none}
[dir="rtl"] .sidebar-nav a{border-left:none;border-right:2px solid transparent}
[dir="rtl"] .sidebar-nav a.active{border-left:none;border-right-color:var(--gold)}
[dir="rtl"] .header-brand{flex-direction:row-reverse}
[dir="rtl"] .sidebar-brand .logo{flex-direction:row-reverse}
'''

c = c.replace('/* ── Form ── */', rtl_css + '\n/* ── Form ── */')

# Add i18n system before </script>
i18n_js = '''
// ── i18n ──
const I18N = {
  en: {
    home: "Home", selling: "I'm Selling", buying: "I'm Buying",
    browse: "Browse", market: "Market",
    carValuator: "CAR VALUATOR",
    tagline: "Know what it's worth",
    whatDo: "What would you like to do?",
    choosePath: "Choose your path and we'll guide you through it.",
    sellTitle: "I'm Selling My Car",
    sellSub: "Tell us about your car and we'll tell you what the market says it's worth.",
    myCar: "My Car",
    getValue: "Get Market Value",
    analyzing: "Analyzing market data...",
    buyTitle: "I'm Buying a Car",
    buySub: "Enter the car you're looking at and the asking price. We'll tell you if it's a good deal — and show you better options.",
    carConsidering: "The Car I'm Considering",
    analyzeDeal: "Analyze This Deal",
    searchingDeals: "Searching for better deals...",
    askingPriceQ: "What's the asking price?",
    enterPrice: "Enter the price you saw",
    enterPriceHint: "Enter the price the seller is asking — we'll tell you if it's fair and show you better alternatives",
    carDetails: "Car Details",
    make: "Make", model: "Model", year: "Year",
    mileage: "Mileage (km)", spec: "Spec", city: "City", country: "Country",
    any: "Any", select_: "Select...",
    gcc: "GCC", us: "US / American", japan: "Japan", european: "European",
    dubai: "Dubai", abuDhabi: "Abu Dhabi", sharjah: "Sharjah",
    riyadh: "Riyadh", jeddah: "Jeddah", dammam: "Dammam",
    kuwaitCity: "Kuwait City", doha: "Doha", muscat: "Muscat",
    uae: "UAE", saudi: "Saudi Arabia", kuwait: "Kuwait", qatar: "Qatar", bahrain: "Bahrain", oman: "Oman",
    manualTab: "Enter Details Manually", urlTab: "Paste Listing URL",
    urlTitle: "Paste the listing URL",
    urlWorks: "Works with Dubizzle, YallaMotor, Haraj, CarSwitch, OpenSooq, and more",
    urlFetch: "We'll fetch the page, extract car details, and tell you if it's a good deal",
    urlPriceLabel: "Asking Price (if different from listing)",
    urlPriceOpt: "Optional — leave empty to use the price from the listing",
    analyzingDeal: "Analyzing this deal...",
    fairRange: "Fair market range",
    confidence: "CONFIDENCE",
    comparables: "Comparables",
    segmentMedian: "Segment Median",
    confRange: "80% Conf. Range",
    howWeGot: "How We Got This Price",
    similarCars: "Similar Cars in the Market",
    noComps: "No comparable listings found",
    whatKnow: "What You Should Know",
    knownIssues: "KNOWN ISSUES",
    plainEnglish: "In Plain English",
    goodDeal: "GOOD DEAL", overpriced: "OVERPRICED",
    vsMarket: "vs fair market value",
    youFound: "You Found", marketValue: "Market Value",
    moEstimate: "Estimated 5-year financing at 3.5% — for comparison only",
    betterDeals: "Better Deals Currently Online",
    betterDealsSub: "These similar cars are listed right now at lower prices.",
    save: "SAVE", aed: "AED",
    overpricedMsg: "This car is overpriced. Check the alternatives below for better value.",
    fairMsg: "This looks like a fair price. Still worth checking alternatives to be sure.",
    foundOnline: "Found on public marketplaces · Active right now",
    browseTitle: "Browse Models",
    browseSub: "Explore every make and model with real-time listing counts.",
    filterCountry: "Country", allGCC: "All GCC",
    back: "Back", models_: "models", listings: "listings",
    marketTitle: "Market Trends",
    marketSub: "Real-time overview of the Gulf used car market.",
    totalListings: "Total Listings", active: "Active",
    valuations7d: "Valuations (7d)", allTime: "All-Time",
    popularMakes: "Most Popular Makes",
    byCountry: "Listings by Country",
    dataRefreshed: "Data refreshed weekly\\nfrom Gulf marketplaces",
    basedOn: "Based on",
    totalListingsAll: "total listings across all GCC countries",
    makeLabel: "Make", modelLabel: "Model",
    specGCC: "GCC", specUS: "US / American", specJapan: "Japan", specEuropean: "European",
    selectMake: "Select make...", selectModel: "Select model...", selectYear: "Select year...",
    mileagePlaceholder: "e.g. 80,000",
    anySpec: "Any", anyCity: "Any", anyCountry: "Any",
    months: "AED/mo*",
    found: "Found on",
    standards: "Standard",
  },
  ar: {
    home: "الرئيسية", selling: "أنا أبيع", buying: "أنا أشتري",
    browse: "تصفح", market: "السوق",
    carValuator: "مقيّم السيارات",
    tagline: "اعرف قيمتها الحقيقية",
    whatDo: "ماذا تريد أن تفعل؟",
    choosePath: "اختر مسارك وسنرشدك خلاله.",
    sellTitle: "أنا أبيع سيارتي",
    sellSub: "أخبرنا عن سيارتك وسنخبرك بقيمتها في السوق.",
    myCar: "سيارتي",
    getValue: "احصل على القيمة السوقية",
    analyzing: "جارٍ تحليل بيانات السوق...",
    buyTitle: "أنا أشتري سيارة",
    buySub: "أدخل تفاصيل السيارة والسعر المطلوب. سنخبرك إذا كانت صفقة جيدة — ونعرض لك خيارات أفضل.",
    carConsidering: "السيارة التي أفكر فيها",
    analyzeDeal: "حلل هذه الصفقة",
    searchingDeals: "جارٍ البحث عن صفقات أفضل...",
    askingPriceQ: "ما هو السعر المطلوب؟",
    enterPrice: "أدخل السعر الذي رأيته",
    enterPriceHint: "أدخل السعر الذي يطلبه البائع — سنخبرك إذا كان عادلاً ونعرض لك بدائل أفضل",
    carDetails: "تفاصيل السيارة",
    make: "الصانع", model: "الطراز", year: "السنة",
    mileage: "المسافة (كم)", spec: "المواصفات", city: "المدينة", country: "الدولة",
    any: "أي", select_: "اختر...",
    gcc: "خليجي", us: "أمريكي", japan: "ياباني", european: "أوروبي",
    dubai: "دبي", abuDhabi: "أبوظبي", sharjah: "الشارقة",
    riyadh: "الرياض", jeddah: "جدة", dammam: "الدمام",
    kuwaitCity: "مدينة الكويت", doha: "الدوحة", muscat: "مسقط",
    uae: "الإمارات", saudi: "السعودية", kuwait: "الكويت", qatar: "قطر", bahrain: "البحرين", oman: "عُمان",
    manualTab: "إدخال التفاصيل يدوياً", urlTab: "لصق رابط الإعلان",
    urlTitle: "ألصق رابط الإعلان",
    urlWorks: "يعمل مع دوبيزل، يلا موتور، حراج، كار سويتش، السوق المفتوح، وغيرها",
    urlFetch: "سنجلب الصفحة ونستخرج تفاصيل السيارة ونخبرك إذا كانت صفقة جيدة",
    urlPriceLabel: "السعر المطلوب (إذا كان مختلفاً عن الإعلان)",
    urlPriceOpt: "اختياري — اتركه فارغاً لاستخدام السعر من الإعلان",
    analyzingDeal: "جارٍ تحليل هذه الصفقة...",
    fairRange: "نطاق السعر العادل",
    confidence: "مستوى الثقة",
    comparables: "سيارات مقارنة",
    segmentMedian: "متوسط الفئة",
    confRange: "نطاق ثقة ٨٠٪",
    howWeGot: "كيف حسبنا هذا السعر",
    similarCars: "سيارات مشابهة في السوق",
    noComps: "لا توجد سيارات مشابهة",
    whatKnow: "ما يجب أن تعرفه",
    knownIssues: "مشاكل معروفة",
    plainEnglish: "باختصار",
    goodDeal: "صفقة جيدة", overpriced: "سعر مبالغ فيه",
    vsMarket: "مقابل القيمة السوقية العادلة",
    youFound: "ما وجدته", marketValue: "القيمة السوقية",
    moEstimate: "تمويل تقديري لـ ٥ سنوات بنسبة ٣.٥٪ — للمقارنة فقط",
    betterDeals: "صفقات أفضل متاحة الآن",
    betterDealsSub: "هذه السيارات المشابهة معروضة بأسعار أقل حالياً.",
    save: "وفر", aed: "درهم",
    overpricedMsg: "هذه السيارة سعرها مبالغ فيه. شاهد البدائل أدناه لقيمة أفضل.",
    fairMsg: "يبدو هذا سعراً عادلاً. يستحق التحقق من البدائل للتأكد.",
    foundOnline: "موجودة في الأسواق العامة · نشطة الآن",
    browseTitle: "تصفح الموديلات",
    browseSub: "استعرض جميع الصانعين والموديلات مع عدد الإعلانات المباشرة.",
    filterCountry: "الدولة", allGCC: "كل الخليج",
    back: "رجوع", models_: "موديل", listings: "إعلان",
    marketTitle: "اتجاهات السوق",
    marketSub: "نظرة عامة مباشرة على سوق السيارات المستعملة في الخليج.",
    totalListings: "إجمالي الإعلانات", active: "نشط",
    valuations7d: "التقييمات (٧ أيام)", allTime: "الإجمالي",
    popularMakes: "أشهر الصانعين",
    byCountry: "الإعلانات حسب الدولة",
    dataRefreshed: "يتم تحديث البيانات أسبوعياً\\nمن أسواق الخليج",
    basedOn: "بناءً على",
    totalListingsAll: "إعلان في جميع دول الخليج",
    makeLabel: "الصانع", modelLabel: "الطراز",
    specGCC: "خليجي", specUS: "أمريكي", specJapan: "ياباني", specEuropean: "أوروبي",
    selectMake: "اختر الصانع...", selectModel: "اختر الطراز...", selectYear: "اختر السنة...",
    mileagePlaceholder: "مثال: ٨٠,٠٠٠",
    anySpec: "أي", anyCity: "أي", anyCountry: "أي",
    months: "درهم/شهر*",
    found: "موجود على",
    standards: "قياسي",
  }
};

let currentLang = localStorage.getItem('gccv-lang') || 'en';

function t(key) {
  return I18N[currentLang]?.[key] || I18N.en[key] || key;
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('gccv-lang', lang);
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.lang = lang;
  document.getElementById('lang-el').textContent = lang === 'ar' ? 'AR | EN' : 'EN | عربي';
  updateAllTexts();
}

function updateAllTexts() {
  // Sidebar
  document.querySelectorAll('.sidebar-nav a').forEach((a, i) => {
    const keys = ['home', 'selling', 'buying', 'browse', 'market'];
    if (keys[i]) a.childNodes[a.childNodes.length-1].textContent = ' ' + t(keys[i]);
  });
  document.querySelector('.sidebar-footer').innerHTML = t('dataRefreshed').replace('\\n', '<br>');
  document.querySelector('.header-brand h1').textContent = t('carValuator');
  document.querySelector('.sidebar-brand .tagline').textContent = t('tagline');

  // Home
  const homeH2 = document.querySelector('#page-home .landing-hero h2');
  if (homeH2) homeH2.textContent = t('whatDo');
  const homeP = document.querySelector('#page-home .landing-hero .sub');
  if (homeP) homeP.textContent = t('choosePath');
  const sellCard = document.querySelector('.choice-card.sell h3');
  if (sellCard) sellCard.textContent = t('selling');
  const buyCard = document.querySelector('.choice-card.buy h3');
  if (buyCard) buyCard.textContent = t('buying');

  // Selling
  const sellTitle = document.querySelector('#page-sell .page-title');
  if (sellTitle) sellTitle.textContent = t('sellTitle');
  const sellSub = document.querySelector('#page-sell .page-sub');
  if (sellSub) sellSub.textContent = t('sellSub');
  const sellBtn = document.getElementById('sell-btn');
  if (sellBtn) sellBtn.textContent = t('getValue');

  // Buying
  const buyTitle = document.querySelector('#page-buy .page-title');
  if (buyTitle) buyTitle.textContent = t('buyTitle');
  const buySub = document.querySelector('#page-buy .page-sub');
  if (buySub) buySub.textContent = t('buySub');
  const buyBtn = document.getElementById('buy-btn');
  if (buyBtn) { buyBtn.textContent = t('analyzeDeal'); }

  // Browse
  const browseTitle = document.querySelector('#page-browse .page-title');
  if (browseTitle) browseTitle.textContent = t('browseTitle');
  const browseSub = document.querySelector('#page-browse .page-sub');
  if (browseSub) browseSub.textContent = t('browseSub');

  // Market
  const marketTitle = document.querySelector('#page-market .page-title');
  if (marketTitle) marketTitle.textContent = t('marketTitle');
  const marketSub = document.querySelector('#page-market .page-sub');
  if (marketSub) marketSub.textContent = t('marketSub');

  // Update page label
  document.getElementById('page-label').textContent = t(currentPage);

  // Reload form content to update labels
  if (currentPage === 'sell' || currentPage === 'buy') {
    document.getElementById('sell-form').innerHTML = SELL_FORM;
    document.getElementById('buy-form').innerHTML = '';
    initForms();
  }
}

// Init lang on load
document.addEventListener('DOMContentLoaded', () => {
  setLanguage(currentLang);
});
'''

# Insert before </script>
c = c.replace('</script>\n</body>', i18n_js + '\n</script>\n</body>')

# Update EN | عربي link to call setLanguage
c = c.replace(
    '<span class="lang">EN | عربي</span>',
    '<span class="lang" id="lang-el" onclick="setLanguage(currentLang===\'ar\'?\'en\':\'ar\')" style="cursor:pointer">EN | عربي</span>'
)

# Make sidebar text use t()
c = c.replace("> Home</a>", ">" + " Home</a>")
c = c.replace("> I'm Selling</a>", "> I'm Selling</a>")
c = c.replace("> I'm Buying</a>", "> I'm Buying</a>")
c = c.replace("> Browse</a>", "> Browse</a>")
c = c.replace("> Market</a>", "> Market</a>")

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("i18n injected!")
