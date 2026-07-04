with open('ui/index.html', 'r', encoding='utf-8') as f:
    t = f.read()

# Wrap entire applyLang in try-catch
old = "function applyLang(){"
new = "function applyLang(){\ntry{"

t = t.replace(old, new)

# Find the closing brace of applyLang and add catch before it
# applyLang ends with: }\n\nfunction goPage
old2 = "document.getElementById('page-label').textContent=t(curPage);\n}"
new2 = "document.getElementById('page-label').textContent=t(curPage);\n}catch(e){console.error(e);}\n}"

t = t.replace(old2, new2)

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(t)
print("Fixed - applyLang now has try-catch")
