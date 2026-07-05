"""Final fix: replace remaining selects with typeable inputs."""
with open('ui/index.html', 'rb') as f:
    t = f.read()

# Static HTML selects
t = t.replace(
    b'<select id="syear"><option>2018</option><option>2019</option><option>2020</option></select>',
    b'<input type="number" id="syear" class="fm-year" placeholder="Year" min="1990" max="2026" value="2018">'
)
t = t.replace(
    b'<select id="byear"><option>2018</option></select>',
    b'<input type="number" id="byear" class="fm-year" placeholder="Year" min="1990" max="2026" value="2018">'
)

# JS makeForm selects (need to match the escaped-quote strings)
# Use simpler byte searches
patterns = [
    (b'<select class="fm-spec"><option value="">Any</option><option value="GCC">GCC</option><option value="US">US</option><option value="Japan">Japan</option><option value="European">European</option></select>',
     b'<input type="text" class="fm-spec" placeholder="GCC, US, Japan..." list="specs" autocomplete="off">'),
    (b'<select class="fm-city"><option value="">Any</option><option>Dubai</option><option>Abu Dhabi</option><option>Sharjah</option><option>Riyadh</option><option>Jeddah</option><option>Dammam</option><option>Kuwait City</option><option>Doha</option><option>Muscat</option></select>',
     b'<input type="text" class="fm-city" placeholder="Dubai, Riyadh..." list="cities" autocomplete="off">'),
    (b'<select class="fm-country"><option value="">Any</option><option value="AE">UAE</option><option value="SA">Saudi Arabia</option><option value="KW">Kuwait</option><option value="QA">Qatar</option><option value="BH">Bahrain</option><option value="OM">Oman</option></select>',
     b'<input type="text" class="fm-country" placeholder="UAE, Saudi Arabia..." list="countries" autocomplete="off">'),
    (b'<select class="fm-year" disabled><option>Select year</option></select>',
     b'<input type="number" class="fm-year" placeholder="Year" min="1990" max="2026" disabled>'),
]

for old, new in patterns:
    if old in t:
        t = t.replace(old, new)
        print(f'Replaced: {old[:50]}')
    else:
        print(f'NOT FOUND: {old[:50]}')

remaining = t.count(b'<select')
print(f'Selects remaining: {remaining}')
print(f'Braces: {t.count(b"{")-t.count(b"}")}')

with open('ui/index.html', 'wb') as f:
    f.write(t)
