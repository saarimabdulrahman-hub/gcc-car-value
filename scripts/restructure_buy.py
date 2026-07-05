"""Move URL option to a button below the manual form"""
with open('ui/index.html', 'rb') as f:
    t = f.read()

# Remove the tab-row
idx = t.find(b'<div class=\"tab-row\"')
if idx >= 0:
    end = t.find(b'<div id=\"buy-manual-section\">', idx)
    if end >= 0:
        t = t[:idx] + t[end:]

# Add URL toggle button after the Analyze button
idx2 = t.find(b'<button class=\"btn\" onclick=\"doValuation')
if idx2 >= 0:
    end2 = t.find(b'<div id=\"buy-url-section\"', idx2)
    if end2 >= 0:
        insert = (
            b'</div>\r\n'
            b'<div style=\"text-align:center;margin-top:16px;padding-top:16px;border-top:1px solid var(--sand)\">\r\n'
            b'<button onclick=\"toggleUrlSection()\" style=\"background:none;border:2px dashed var(--border);padding:12px 24px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:0.85rem;color:var(--muted);transition:all 0.15s\" onmouseover=\"this.style.borderColor=' + b\"'var(--gold)';this.style.color=\" + b\"'var(--gold-dark)'\" + b'\" onmouseout=\"this.style.borderColor=' + b\"'var(--border)';this.style.color=\" + b\"'var(--muted)'\" + b'\">&#128279; Or paste a listing URL instead</button>\r\n'
            b'</div>\r\n'
            b'</div>\r\n\r\n</div>\r\n'
        )
        t = t[:end2] + insert + t[end2:]

# Add toggleUrlSection function
t = t.replace(
    b'function switchBuyTab(mode){',
    b'function toggleUrlSection(){var el=document.getElementById("buy-url-section");if(el.style.display==="none"||!el.style.display){el.style.display="block";}else{el.style.display="none";}}\nfunction switchBuyTab(mode){'
)

with open('ui/index.html', 'wb') as f:
    f.write(t)
print('Done. Braces:', t.count(b'{')-t.count(b'}'))
print('Has toggleUrlSection:', b'toggleUrlSection' in t)
