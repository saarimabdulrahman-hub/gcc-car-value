"""Add toast notifications to index.html"""
with open('ui/index.html', 'rb') as f:
    t = f.read()

# Add toast CSS
toast_css = b'''
.toast-container{position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px}
.toast{padding:14px 20px;border-radius:10px;color:#fff;font-weight:600;font-size:0.9rem;max-width:400px;box-shadow:0 4px 20px rgba(0,0,0,0.3);animation:slideIn 0.3s ease,slideOut 0.3s ease 9.7s forwards;cursor:pointer}
.toast-error{background:linear-gradient(135deg,#E74C3C,#C0392B)}
.toast-warning{background:linear-gradient(135deg,#F39C12,#E67E22)}
.toast-success{background:linear-gradient(135deg,#2ECC71,#27AE60)}
@keyframes slideIn{from{transform:translateX(400px);opacity:0}to{transform:translateX(0);opacity:1}}
@keyframes slideOut{from{transform:translateX(0);opacity:1}to{transform:translateX(400px);opacity:0}}
'''
t = t.replace(b'</style>', toast_css + b'</style>')

# Add toast JS
toast_js = b'''
var TOAST_COUNT=0;
function showToast(msg,type,duration){
  type=type||"error";duration=duration||10000;
  var container=document.querySelector(".toast-container");
  if(!container){container=document.createElement("div");container.className="toast-container";document.body.appendChild(container);}
  var toast=document.createElement("div");
  toast.className="toast toast-"+type;
  toast.textContent=msg;
  toast.onclick=function(){toast.remove();};
  container.appendChild(toast);
  setTimeout(function(){if(toast.parentNode)toast.remove();},duration);
}
function showError(msg){showToast(msg,"error",10000);}
function showWarning(msg){showToast(msg,"warning",8000);}
function showSuccess(msg){showToast(msg,"success",5000);}
'''
t = t.replace(b'</script>', toast_js + b'</script>')

# Replace all alert() with toast
t = t.replace(b"alert('Error: '+e.message)", b"showError(e.message)")
t = t.replace(b"alert('Please fill in make, model, and year')", b"showWarning('Please fill in make, model, and year')")
t = t.replace(b"alert('Please enter the asking price to analyze the deal')", b"showWarning('Please enter the asking price')")
t = t.replace(b"return alert('Please paste a listing URL first');", b"showWarning('Please paste a listing URL first');return;")
t = t.replace(b"alert('Please paste a listing URL')", b"showWarning('Please paste a listing URL first')")
t = t.replace(b"alert('Please enter the asking price');", b"showWarning('Please enter the asking price');")

# Update error display in doUrlValuation to detect Dubizzle blocking
t = t.replace(
    b"if(er){er.classList.remove('hidden');er.innerHTML='<div class=\"error-msg\">'+e.message+'</div>';}",
    b"var msg=e.message||'Failed';if(msg.indexOf('Blocked')>-1||msg.indexOf('Pardon')>-1)msg='Dubizzle is blocking automated access. Please use the manual form instead.';showError(msg);"
)

# Update fetch error handling for URL valuation
t = t.replace(
    b"if(!r.ok){var e=await r.json();throw new Error(e.detail||'Failed');}",
    b"if(!r.ok){var errData;try{errData=await r.json();}catch(ex){errData={detail:'Site blocked access'};}var errMsg=errData.detail||'Failed';if(errMsg.indexOf('Pardon')>-1||errMsg.indexOf('Interruption')>-1)errMsg='Dubizzle is blocking automated access. Paste links from OpenSooq, Haraj, or YallaMotor instead.';throw new Error(errMsg);}"
)

with open('ui/index.html', 'wb') as f:
    f.write(t)
print('Done. Braces:', t.count(b'{')-t.count(b'}'))
print('Has showToast:', b'showToast' in t)
