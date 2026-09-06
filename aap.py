#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""مدیریت بوکمارک‌ها — نسخه پایتون (Flask) — اجرا در Termux/Pydroid اندروید بدون روت"""
import json, os, time, random
from flask import Flask, request, jsonify, render_template_string, Response

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.json")
app = Flask(__name__)

# ================= دیتابیس (JSON) =================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"bookmarks": []}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def new_id():
    return f"{int(time.time()*1000)}-{random.randint(1000,9999)}"

PRIO_ORDER = {"high": 0, "medium": 1, "low": 2}

# ================= صفحه وب =================
PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مدیریت بوکمارک‌ها</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,'Vazirmatn',sans-serif}
body{background:#0f172a;color:#e2e8f0;min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:1.3rem;text-align:center;padding:12px;color:#38bdf8}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.tabs button{flex:1;min-width:90px;padding:10px 6px;border:none;border-radius:10px;background:#1e293b;color:#94a3b8;font-size:.85rem;cursor:pointer}
.tabs button.active{background:#0284c7;color:#fff}
.card{background:#1e293b;border-radius:14px;padding:16px;margin-bottom:14px}
label{display:block;font-size:.8rem;color:#94a3b8;margin:8px 0 4px}
input,select,textarea{width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:.95rem}
textarea{min-height:70px;resize:vertical}
.btn{padding:10px 18px;border:none;border-radius:8px;cursor:pointer;font-size:.9rem;margin-top:10px}
.btn-primary{background:#0284c7;color:#fff;width:100%}
.btn-sm{padding:6px 10px;font-size:.78rem;margin:0}
.btn-edit{background:#334155;color:#7dd3fc}
.btn-del{background:#7f1d1d;color:#fca5a5}
.btn-visit{background:#065f46;color:#6ee7b7}
.row{display:flex;gap:8px}.row>*{flex:1}
.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
@media(min-width:600px){.stats-grid{grid-template-columns:repeat(4,1fr)}}
.stat{background:#0f172a;border-radius:12px;padding:14px;text-align:center}
.stat .num{font-size:1.5rem;font-weight:bold;color:#38bdf8}
.stat .lbl{font-size:.75rem;color:#94a3b8;margin-top:4px}
.bm-item{background:#0f172a;border-radius:10px;padding:12px;margin-bottom:10px;border-right:4px solid #334155}
.bm-item.p-high{border-color:#ef4444}.bm-item.p-medium{border-color:#f59e0b}.bm-item.p-low{border-color:#22c55e}
.bm-title{font-weight:bold;color:#7dd3fc;word-break:break-all}
.bm-meta{font-size:.75rem;color:#64748b;margin:4px 0}
.badge{display:inline-block;background:#334155;border-radius:6px;padding:2px 8px;font-size:.7rem;margin:2px 2px 0 0}
.bm-notes{font-size:.8rem;color:#94a3b8;margin-top:6px;white-space:pre-wrap}
.bm-actions{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.hidden{display:none}
.empty{text-align:center;color:#475569;padding:30px}
h2{font-size:1rem;color:#38bdf8;margin-bottom:10px}
.cat-row{display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #334155;font-size:.85rem}
.bar{height:8px;background:#334155;border-radius:4px;overflow:hidden;margin-top:4px}
.bar div{height:100%;background:#0284c7}
</style>
</head>
<body>
<div class="container">
<h1>📚 مدیریت بوکمارک‌ها</h1>
<div class="tabs">
<button class="active" onclick="showTab('dashboard',this)">📊 داشبورد</button>
<button onclick="showTab('list',this)">🔗 بوکمارک‌ها</button>
<button onclick="showTab('add',this)">➕ افزودن</button>
<button onclick="showTab('search',this)">🔍 جستجو</button>
<button onclick="showTab('backup',this)">💾 پشتیبان</button>
</div>

<div id="tab-dashboard">
<div class="card"><div class="stats-grid" id="statsGrid"></div></div>
<div class="card"><h2>📈 آمار دسته‌بندی‌ها</h2><div id="catStats"></div></div>
<div class="card"><h2>🏆 پربازدیدترین</h2><div id="topVisited"></div></div>
</div>

<div id="tab-list" class="hidden">
<div class="card">
<div class="row">
<select id="filterCat" onchange="renderList()"></select>
<select id="filterPriority" onchange="renderList()">
<option value="">همه اولویت‌ها</option><option value="high">بالا</option>
<option value="medium">متوسط</option><option value="low">کم</option></select>
</div>
<div class="row">
<select id="sortBy" onchange="renderList()">
<option value="created">جدیدترین</option><option value="visits">بیشترین بازدید</option>
<option value="priority">اولویت</option><option value="title">حروف الفبا</option></select>
</div>
</div>
<div id="bmList"></div>
</div>

<div id="tab-add" class="hidden">
<div class="card">
<h2 id="formTitle">افزودن بوکمارک جدید</h2>
<input type="hidden" id="editId">
<label>عنوان *</label><input id="fTitle" placeholder="مثلاً: آموزش پایتون">
<label>آدرس (URL) *</label><input id="fUrl" dir="ltr" placeholder="https://...">
<label>دسته‌بندی</label><input id="fCat" list="catList" placeholder="مثلاً: آموزش"><datalist id="catList"></datalist>
<label>برچسب‌ها (با کاما جدا کن)</label><input id="fTags" placeholder="برنامه‌نویسی, پایتون">
<label>اولویت</label>
<select id="fPriority"><option value="low">کم</option><option value="medium" selected>متوسط</option><option value="high">بالا</option></select>
<label>یادداشت</label><textarea id="fNotes" placeholder="نکات درباره این لینک..."></textarea>
<button class="btn btn-primary" onclick="saveBookmark()">💾 ذخیره</button>
<button class="btn btn-sm btn-edit hidden" id="cancelEdit" onclick="cancelEdit()" style="width:100%">انصراف از ویرایش</button>
</div>
</div>

<div id="tab-search" class="hidden">
<div class="card">
<h2>🔍 جستجوی پیشرفته</h2>
<label>متن (عنوان/آدرس/یادداشت)</label><input id="sText" oninput="doSearch()" placeholder="جستجو...">
<div class="row">
<label style="width:100%">دسته</label>
<select id="sCat" onchange="doSearch()"></select>
<select id="sPriority" onchange="doSearch()"><option value="">هر اولویت</option>
<option value="high">بالا</option><option value="medium">متوسط</option><option value="low">کم</option></select>
</div>
<label>برچسب</label><input id="sTag" oninput="doSearch()" placeholder="نام برچسب">
<div class="row">
<div><label>بازدید از</label><input type="number" id="sMinVisits" oninput="doSearch()" placeholder="0"></div>
<div><label>وضعیت بازدید</label>
<select id="sVisited" onchange="doSearch()"><option value="">همه</option>
<option value="yes">فقط بازدیدشده</option><option value="no">فقط بازدیدنشده</option></select></div>
</div>
</div>
<div id="searchResults"></div>
</div>

<div id="tab-backup" class="hidden">
<div class="card">
<h2>💾 خروجی / ورودی دیتابیس</h2>
<p style="font-size:.8rem;color:#94a3b8">دیتابیس در فایل bookmarks.json کنار برنامه ذخیره می‌شود.</p>
<button class="btn btn-primary" onclick="location.href='/export'">⬇️ خروجی (دانلود JSON)</button>
<label>ورودی: فایل JSON را انتخاب کن</label>
<input type="file" id="importFile" accept=".json" onchange="importJSON(event)">
<div class="row" style="margin-top:16px">
<button class="btn btn-sm btn-del" onclick="clearAll()" style="width:100%">🗑 پاک کردن کل دیتابیس</button>
</div>
</div>
</div>
</div>

<script>
const $=id=>document.getElementById(id);
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const PRIO={high:'بالا',medium:'متوسط',low:'کم'};
const PRIO_EMOJI={high:'🔴',medium:'🟡',low:'🟢'};

function showTab(name,btn){
['dashboard','list','add','search','backup'].forEach(t=>$('tab-'+t).classList.add('hidden'));
$('tab-'+name).classList.remove('hidden');
document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('active'));
if(btn)btn.classList.add('active');
if(name==='dashboard')renderStats();
if(name==='list')renderList();
if(name==='search')doSearch();
}

async function api(path,opts){const r=await fetch(path,opts);if(!r.ok)throw new Error('خطای سرور');return r.json();}

function bmHTML(b){
const d=new Date(b.created*1000).toLocaleDateString('fa-IR');
const lv=b.lastVisit?new Date(b.lastVisit*1000).toLocaleDateString('fa-IR'):'—';
return `<div class="bm-item p-${b.priority}">
<div class="bm-title">${esc(b.title)}</div>
<div class="bm-meta" dir="ltr" style="text-align:left">${esc(b.url)}</div>
<div class="bm-meta">
<span class="badge">📂 ${esc(b.cat)}</span>
<span class="badge">${PRIO_EMOJI[b.priority]} ${PRIO[b.priority]}</span>
<span class="badge">👁 ${b.visits} بازدید</span>
<span class="badge">🕒 آخرین: ${lv}</span>
<span class="badge">📅 ${d}</span>
${b.tags.map(t=>`<span class="badge" style="background:#164e63">#${esc(t)}</span>`).join('')}
</div>
${b.notes?`<div class="bm-notes">📝 ${esc(b.notes)}</div>`:''}
<div class="bm-actions">
<a class="btn btn-sm btn-visit" style="text-decoration:none" href="/visit/${b.id}" target="_blank">🚀 باز کردن</a>
<button class="btn btn-sm btn-edit" onclick="editBookmark('${b.id}')">✏️ ویرایش</button>
<button class="btn btn-sm btn-del" onclick="deleteBookmark('${b.id}')">🗑 حذف</button>
<button class="btn btn-sm btn-edit" onclick="copyUrl('${b.id}')">📋 کپی</button>
</div></div>`;
}

async function renderList(){
const p=new URLSearchParams({cat:$('filterCat').value,priority:$('filterPriority').value,sort:$('sortBy').value});
const items=await api('/api/list?'+p);
$('bmList').innerHTML=items.length?items.map(bmHTML).join(''):'<div class="empty">هنوز بوکمارکی نیست 📭</div>';
}

async function renderStats(){
const s=await api('/api/stats');
$('statsGrid').innerHTML=`
<div class="stat"><div class="num">${s.total}</div><div class="lbl">کل بوکمارک‌ها</div></div>
<div class="stat"><div class="num">${s.active}</div><div class="lbl">فعال (۳۰ روز اخیر)</div></div>
<div class="stat"><div class="num">${s.totalVisits}</div><div class="lbl">مجموع بازدیدها</div></div>
<div class="stat"><div class="num">${s.avgVisits}</div><div class="lbl">میانگین بازدید</div></div>`;
const max=Math.max(1,...s.categories.map(c=>c.count));
$('catStats').innerHTML=s.categories.map(c=>
`<div class="cat-row"><span>📂 ${esc(c.name)}</span><span style="color:#94a3b8">${c.count} لینک | ${c.visits} بازدید</span></div>
<div class="bar"><div style="width:${c.count/max*100}%"></div></div>`).join('')||'<div class="empty">—</div>';
$('topVisited').innerHTML=s.top.length?s.top.map((b,i)=>
`<div class="cat-row"><span>${['🥇','🥈','🥉','4️⃣','5️⃣'][i]} ${esc(b.title)}</span>
<span style="color:#6ee7b7">👁 ${b.visits}</span></div>`).join(''):'<div class="empty">هنوز بازدیدی ثبت نشده</div>';
}

async function doSearch(){
const p=new URLSearchParams({q:$('sText').value,cat:$('sCat').value,priority:$('sPriority').value,
tag:$('sTag').value,minVisits:$('sMinVisits').value,visited:$('sVisited').value});
const res=await api('/api/search?'+p);
$('searchResults').innerHTML=res.length?res.map(bmHTML).join(''):'<div class="empty">نتیجه‌ای پیدا نشد 🔎</div>';
}

async function saveBookmark(){
const title=$('fTitle').value.trim(),url=$('fUrl').value.trim();
if(!title||!url){alert('عنوان و آدرس الزامی است');return;}
const body={id:$('editId').value,title,url,cat:$('fCat').value.trim(),
tags:$('fTags').value.split(',').map(t=>t.trim()).filter(Boolean),
priority:$('fPriority').value,notes:$('fNotes').value.trim()};
await api('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
cancelEdit();showTab('list',document.querySelectorAll('.tabs button')[1]);
}

async function editBookmark(id){
const b=await api('/api/get?id='+id);
showTab('add',document.querySelectorAll('.tabs button')[2]);
$('formTitle').textContent='ویرایش: '+b.title;
$('editId').value=b.id;$('fTitle').value=b.title;$('fUrl').value=b.url;
$('fCat').value=b.cat;$('fTags').value=b.tags.join(', ');
$('fPriority').value=b.priority;$('fNotes').value=b.notes;
$('cancelEdit').classList.remove('hidden');
}
function cancelEdit(){
$('editId').value='';$('fTitle').value='';$('fUrl').value='';$('fCat').value='';
$('fTags').value='';$('fPriority').value='medium';$('fNotes').value='';
$('formTitle').textContent='افزودن بوکمارک جدید';$('cancelEdit').classList.add('hidden');
}
async function deleteBookmark(id){
const b=await api('/api/get?id='+id);
if(confirm('حذف «'+b.title+'»؟')){
await api('/api/delete?id='+id);renderList();renderStats();}
}
async function copyUrl(id){
const b=await api('/api/get?id='+id);
try{await navigator.clipboard.writeText(b.url);alert('آدرس کپی شد ✅');}
catch(e){prompt('آدرس:',b.url);}
}

async function importJSON(e){
const f=e.target.files[0];if(!f)return;
const text=await f.text();
const r=await fetch('/import',{method:'POST',headers:{'Content-Type':'application/json'},body:text});
const j=await r.json();
alert(j.added+' بوکمارک اضافه شد ✅');e.target.value='';
}
async function clearAll(){
if(confirm('کل دیتابیس پاک شود؟ قابل بازگشت نیست!')&&confirm('مطمئنی؟ اول خروجی بگیر!')){
await api('/api/clear',{method:'POST'});renderStats();alert('پاک شد');}
}

(async function init(){
const cats=await api('/api/cats');
const opts=c=>`<option value="${esc(c)}">${esc(c)}</option>`;
$('filterCat').innerHTML='<option value="">همه دسته‌ها</option>'+cats.map(opts).join('');
$('sCat').innerHTML='<option value="">همه</option>'+cats.map(opts).join('');
$('catList').innerHTML=cats.map(c=>`<option value="${esc(c)}">`).join('');
renderStats();
})();
</script>
</body>
</html>"""

# ================= روت‌های API =================
@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/api/list")
def api_list():
    db = load_db()
    items = db["bookmarks"]
    cat = request.args.get("cat", "")
    prio = request.args.get("priority", "")
    sort = request.args.get("sort", "created")
    if cat:
        items = [b for b in items if b["cat"] == cat]
    if prio:
        items = [b for b in items if b["priority"] == prio]
    return jsonify(sorted(items, key=lambda b: (-b.get("created", 0)) if sort == "created"
        else (-b.get("visits", 0)) if sort == "visits"
        else (PRIO_ORDER.get(b["priority"], 1), b["title"]) if sort == "priority"
        else b["title"] if sort == "title"
        else -b.get("created", 0)))

@app.route("/api/stats")
def api_stats():
    db = load_db()
    bs = db["bookmarks"]
    now = time.time()
    active = sum(1 for b in bs if b.get("lastVisit") and now - b["lastVisit"] < 30 * 86400)
    total_visits = sum(b.get("visits", 0) for b in bs)
    cats = {}
    for b in bs:
        c = cats.setdefault(b["cat"], {"name": b["cat"], "count": 0, "visits": 0})
        c["count"] += 1
        c["visits"] += b.get("visits", 0)
    top = sorted([b for b in bs if b.get("visits", 0) > 0], key=lambda b: -b["visits"])[:5]
    return jsonify({
        "total": len(bs), "active": active, "totalVisits": total_visits,
        "avgVisits": round(total_visits / len(bs), 1) if bs else 0,
        "categories": sorted(cats.values(), key=lambda c: -c["count"]),
        "top": [{"title": b["title"], "visits": b["visits"]} for b in top]})

@app.route("/api/search")
def api_search():
    db = load_db()
    q = request.args.get("q", "").lower().strip()
    cat = request.args.get("cat", "")
    prio = request.args.get("priority", "")
    tag = request.args.get("tag", "").lower().strip()
    min_visits = int(request.args.get("minVisits") or 0)
    visited = request.args.get("visited", "")
    res = []
    for b in db["bookmarks"]:
        if q and q not in (b["title"] + b["url"] + b.get("notes", "") + "".join(b.get("tags", []))).lower():
            continue
        if cat and b["cat"] != cat: continue
        if prio and b["priority"] != prio: continue
        if tag and not any(tag in t.lower() for t in b.get("tags", [])): continue
        if min_visits and b.get("visits", 0) < min_visits: continue
        if visited == "yes" and not b.get("lastVisit"): continue
        if visited == "no" and b.get("lastVisit"): continue
        res.append(b)
    return jsonify(res)

@app.route("/api/save", methods=["POST"])
def api_save():
    d = request.get_json(force=True)
    db = load_db()
    tags = [str(t).strip() for t in d.get("tags", []) if str(t).strip()]
    data = {"title": str(d["title"]).strip(), "url": str(d["url"]).strip(),
            "cat": str(d.get("cat", "")).strip() or "بدون دسته", "tags": tags,
            "priority": d.get("priority", "medium") if d.get("priority") in PRIO_ORDER else "medium",
            "notes": str(d.get("notes", "")).strip(), "updated": time.time()}
    if d.get("id"):
        for b in db["bookmarks"]:
            if b["id"] == d["id"]:
                b.update(data)
                break
    else:
        data.update({"id": new_id(), "visits": 0, "lastVisit": None, "created": time.time()})
        db["bookmarks"].append(data)
    save_db(db)
    return jsonify({"ok": True})

@app.route("/api/get")
def api_get():
    db = load_db()
    for b in db["bookmarks"]:
        if b["id"] == request.args.get("id"):
            return jsonify(b)
    return jsonify({"error": "not found"}), 404

@app.route("/api/delete")
def api_delete():
    db = load_db()
    i = request.args.get("id")
    db["bookmarks"] = [b for b in db["bookmarks"] if b["id"] != i]
    save_db(db)
    return jsonify({"ok": True})

@app.route("/visit/<bid>")
def visit(bid):
    db = load_db()
    for b in db["bookmarks"]:
        if b["id"] == bid:
            b["visits"] = b.get("visits", 0) + 1
            b["lastVisit"] = time.time()
            save_db(db)
            return f'<script>location.replace({json.dumps(b["url"])})</script>'
    return "پیدا نشد", 404

@app.route("/api/cats")
def api_cats():
    db = load_db()
    return jsonify(sorted({b["cat"] for b in db["bookmarks"]}))

@app.route("/api/clear", methods=["POST"])
def api_clear():
    save_db({"bookmarks": []})
    return jsonify({"ok": True})

@app.route("/export")
def export():
    fname = f"bookmarks-{time.strftime('%Y-%m-%d')}.json"
    return Response(json.dumps(load_db(), ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={fname}"})

@app.route("/import", methods=["POST"])
def import_():
    try:
        data = json.loads(request.get_data(as_text=True))
        items = data if isinstance(data, list) else data.get("bookmarks", [])
        db = load_db()
        added = 0
        for b in items:
            if isinstance(b, dict) and b.get("title") and b.get("url"):
                db["bookmarks"].append({
                    "id": new_id(), "title": str(b["title"]), "url": str(b["url"]),
                    "cat": str(b.get("cat", "")) or "بدون دسته",
                    "tags": [str(t) for t in b.get("tags", []) if str(t).strip()],
                    "priority": b.get("priority") if b.get("priority") in PRIO_ORDER else "medium",
                    "notes": str(b.get("notes", "")), "visits": int(b.get("visits", 0)),
                    "lastVisit": b.get("lastVisit"), "created": b.get("created", time.time()),
                    "updated": time.time()})
                added += 1
        save_db(db)
        return jsonify({"added": added})
    except Exception:
        return jsonify({"added": 0, "error": "فایل نامعتبر"}), 400

if __name__ == "__main__":
    print("✅ اپ اجرا شد → در مرورگر گوشی باز کن: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
