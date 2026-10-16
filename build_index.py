# -*- coding: utf-8 -*-
"""
Generate a LinkedIn-style, modular, searchable index.html for the
yingmingbao.github.io knowledge base.

Key design:
  * Module cards + document links are rendered as STATIC HTML (always
    visible/clickable even if JS is disabled or sandboxed).
  * JavaScript is only an enhancement: live full-text search + category filter.

Run:  python build_index.py
It overwrites index.html in the same directory.
"""
import os, re, json, html as html_lib
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---- Module / category definitions ---------------------------------------
MODULES = {
    "management": {
        "name": "管理学习",
        "desc": "企业战略、组织协同与管理系统搭建的读书与实践笔记。",
        "color": "#0a66c2",
        "icon": "📊",
        "folder": "learn-management",
    },
    "tech": {
        "name": "技术框架",
        "desc": "Spring AI Alibaba 与 ReactAgent 等 AI 应用框架的研习笔记。",
        "color": "#057642",
        "icon": "⚙️",
        "folder": "learn-spring-ai-alibaba-framework",
    },
    "bdl": {
        "name": "业务描述语言",
        "desc": "Business Description Language：用结构化语言描述商业系统的要素与架构。",
        "color": "#915907",
        "icon": "📐",
        "folder": "bdl",
    },
    "industry": {
        "name": "行业研究",
        "desc": "PC、操作系统、互联网、AI、通信等信息技术产业的发展研究总报告。",
        "color": "#6b1b7a",
        "icon": "🏭",
        "folder": "industry",
    },
    "data": {
        "name": "数据处理",
        "desc": "数据仓库理论与实务等数据工程学习资料。",
        "color": "#0b6e8f",
        "icon": "🗄️",
        "folder": "learn-data-process",
    },
    "programming": {
        "name": "编程本质",
        "desc": "关于编程范式、本质与思维方式的系统性研究。",
        "color": "#b24020",
        "icon": "💻",
        "folder": "programming",
    },
    "english": {
        "name": "英语学习",
        "desc": "每日英语核心词等语言学习资料。",
        "color": "#0a8754",
        "icon": "🔤",
        "folder": "learn-english",
    },
}
MODULE_ORDER = ["management", "tech", "bdl", "industry", "data", "programming", "english"]

CONTENT_CAP = 80000  # max characters indexed per file (for search)

# ---- Text extraction helpers ---------------------------------------------
def strip_html(text):
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    # remove any leftover tag fragments (incl. <script ... > with attributes)
    text = re.sub(r"<[^>]*>", " ", text)
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def strip_md(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)          # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)        # links -> text
    text = re.sub(r"<[^>]*>", " ", text)                        # inline html
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)          # heading marks
    text = re.sub(r"[*_]{1,3}", "", text)                       # bold/italic
    text = re.sub(r"`", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def friendly_name(fname):
    return re.sub(r"\.(md|html?)$", "", fname, flags=re.I).replace("_", " ")

# Polished display titles for files whose raw first line is awkward.
MANUAL_TITLES = {
    "learn-spring-ai-alibaba-framework/react-agent.md": "ReactAgent 实例详解：逻辑身份与内存状态",
    "learn-spring-ai-alibaba-framework/spring-ai-alibaba-framework.md": "Spring AI Alibaba：ChatClient 与 ReactAgent",
    "learn-management/企业组织协调机制的历史.md": "企业组织协调机制的历史研究：从相互调适到算法协同",
    "learn-data-process/datawarehouse.html": "数据仓库：理论与实务",
    "learn-management/CORPORATE_STRATEGY_Ansoff.md": "《公司战略》Corporate Strategy · Ansoff, 1965",
}

def first_title_md(text, basename):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return None
    first = lines[0]
    if first.startswith("#"):
        first = first.lstrip("#").strip()
    if not first or "<" in first:
        return friendly_name(basename)
    return first

def extract(path, rel):
    basename = os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    if ext in (".html", ".htm"):
        tm = re.search(r"<title>(.*?)</title>", raw, flags=re.S | re.I)
        title = html_lib.unescape(tm.group(1).strip()) if tm else None
        content = strip_html(raw)
        ftype = "html"
        if not title:
            title = content[:50].strip() or friendly_name(basename)
    else:
        title = first_title_md(raw, basename)
        content = strip_md(raw)
        ftype = "md"
    if not title:
        title = friendly_name(basename)
    if rel in MANUAL_TITLES:
        title = MANUAL_TITLES[rel]
    content = content[:CONTENT_CAP]
    desc = content[:160].strip() if content else "（图文 / 图表内容，点击打开查看原文档）"
    return title, content, desc, ftype

# ---- Build entries --------------------------------------------------------
ENTRIES = []
for key in MODULE_ORDER:
    folder = MODULES[key]["folder"]
    fdir = os.path.join(ROOT, folder)
    if not os.path.isdir(fdir):
        continue
    for fname in sorted(os.listdir(fdir)):
        if fname.startswith("."):
            continue
        if not fname.lower().endswith((".md", ".html", ".htm")):
            continue
        fpath = os.path.join(fdir, fname)
        if not os.path.isfile(fpath):
            continue
        rel = folder + "/" + fname
        title, content, desc, ftype = extract(fpath, rel)
        ENTRIES.append({
            "id": len(ENTRIES),
            "title": title,
            "path": rel,
            "href": quote(rel),
            "module": key,
            "type": ftype,
            "desc": desc,
            "content": content,
        })

total_words = sum(len(e["content"]) for e in ENTRIES)

# ---- HTML escaping (Python, for static markup) ----------------------------
def pescapes(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))

# ---- Build STATIC HTML (visible without JS) ------------------------------
def doc_item_html(e):
    badge = "t-html" if e["type"] == "html" else "t-md"
    return (
        '<a class="doc-item" href="' + e["href"] + '" target="_blank" rel="noopener" '
        'data-id="' + str(e["id"]) + '" data-module="' + e["module"] + '">'
        '<span class="type-badge ' + badge + '">' + e["type"].upper() + '</span>'
        '<div class="doc-main"><div class="doc-title">' + pescapes(e["title"]) + '</div>'
        '<div class="doc-desc">' + pescapes(e["desc"]) + '</div></div>'
        '<span class="open-link">打开 ↗</span></a>'
    )

def module_card_html(key):
    mod = MODULES[key]
    items = [e for e in ENTRIES if e["module"] == key]
    if not items:
        return ""
    inner = "".join(doc_item_html(e) for e in items)
    return (
        '<section class="card module-card" id="mod-' + key + '" data-module="' + key + '">'
        '<div class="module-head"><div class="mod-icon" style="background:' + mod["color"] + '">'
        + mod["icon"] + '</div>'
        '<div class="mod-titles"><h2>' + pescapes(mod["name"]) + '</h2><p>' + pescapes(mod["desc"]) + '</p></div>'
        '<span class="count-badge">' + str(len(items)) + ' 篇</span></div>'
        '<div class="doc-list">' + inner + '</div></section>'
    )

STATIC_FEED = "".join(module_card_html(k) for k in MODULE_ORDER)

def pills_html():
    h = '<a class="pill active" href="#top" data-cat="all">全部</a>'
    for k in MODULE_ORDER:
        if not any(e["module"] == k for e in ENTRIES):
            continue
        m = MODULES[k]
        h += ('<a class="pill" href="#mod-' + k + '" data-cat="' + k + '">'
              + m["icon"] + " " + pescapes(m["name"]) + '</a>')
    return h

def sidebar_html():
    h = ""
    for k in MODULE_ORDER:
        n = sum(1 for e in ENTRIES if e["module"] == k)
        if not n:
            continue
        m = MODULES[k]
        h += ('<a class="side-link" href="#mod-' + k + '" data-cat="' + k + '">'
              '<span class="dot" style="background:' + m["color"] + '"></span>'
              + pescapes(m["name"]) + '<span class="cnt">' + str(n) + '</span></a>')
    return h

# ---- JSON for JS search (escape </ to avoid breaking <script>) ------------
def js_str(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

# ---- CSS ------------------------------------------------------------------
STYLE = """<style>
:root{--li-blue:#0a66c2;--li-blue-d:#004182;--bg:#f3f2ef;--card:#fff;--border:#e8e8e8;--text:#1d2226;--sec:#5e5e5e;}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);line-height:1.5;}
a{text-decoration:none;}
.nav{position:sticky;top:0;z-index:50;background:#fff;border-bottom:1px solid var(--border);box-shadow:0 0 0 1px rgba(0,0,0,.02);}
.nav-inner{max-width:1128px;margin:0 auto;height:54px;display:flex;align-items:center;gap:14px;padding:0 16px;}
.logo{display:flex;align-items:center;gap:8px;font-weight:800;color:var(--li-blue);font-size:20px;white-space:nowrap;}
.logo .mark{width:34px;height:34px;border-radius:6px;background:var(--li-blue);color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;}
.search{position:relative;flex:1;max-width:560px;}
.search input{width:100%;height:38px;border:1px solid transparent;border-radius:8px;background:#edf3f8;padding:0 14px 0 40px;font-size:14px;outline:none;transition:.15s;}
.search input:focus{background:#fff;border-color:var(--li-blue);box-shadow:0 0 0 1px var(--li-blue);}
.search .ico{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:#5e5e5e;font-size:15px;}
.container{max-width:1128px;margin:22px auto;padding:0 16px;}
.hero{background:linear-gradient(135deg,#0a66c2,#378fe9);border-radius:12px;color:#fff;padding:26px 28px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.12);}
.hero h1{margin:0 0 6px;font-size:26px;}
.hero p{margin:0;opacity:.93;font-size:15px;}
.hero .stats{margin-top:16px;display:flex;gap:30px;flex-wrap:wrap;}
.hero .stat b{font-size:23px;display:block;line-height:1.1;}
.hero .stat span{font-size:13px;opacity:.92;}
.pills{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px;}
.pill{border:1px solid var(--border);background:#fff;border-radius:999px;padding:8px 16px;font-size:14px;cursor:pointer;color:var(--text);transition:.15s;}
.pill:hover{background:#f3f2ef;}
.pill.active{background:var(--li-blue);border-color:var(--li-blue);color:#fff;font-weight:600;}
.layout{display:flex;gap:22px;align-items:flex-start;}
.feed{flex:1;min-width:0;}
.sidebar{width:300px;flex-shrink:0;}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:18px;box-shadow:0 1px 2px rgba(0,0,0,.04);}
.module-head{display:flex;align-items:center;gap:14px;margin-bottom:6px;}
.mod-icon{width:46px;height:46px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:22px;color:#fff;flex-shrink:0;}
.mod-titles{flex:1;min-width:0;}
.mod-titles h2{margin:0;font-size:19px;}
.mod-titles p{margin:3px 0 0;color:var(--sec);font-size:13px;}
.count-badge{background:#eef3f8;color:var(--li-blue);border-radius:999px;padding:5px 12px;font-size:13px;font-weight:600;white-space:nowrap;}
.doc-list{margin-top:4px;}
.doc-item{display:flex;align-items:center;gap:12px;padding:12px 10px;border-radius:10px;border:1px solid transparent;}
.doc-item:hover{background:#f3f2ef;border-color:var(--border);}
.type-badge{font-size:11px;font-weight:700;border-radius:6px;padding:4px 8px;flex-shrink:0;width:54px;text-align:center;}
.t-md{background:#f0e9fb;color:#7c3aed;}
.t-html{background:#fdeede;color:#c2630a;}
.doc-main{flex:1;min-width:0;}
.doc-title{font-size:15px;font-weight:600;color:#1d2226;}
.doc-item:hover .doc-title{color:var(--li-blue);}
.doc-desc{font-size:13px;color:var(--sec);margin-top:3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.open-link{font-size:13px;color:var(--li-blue);white-space:nowrap;}
.side-card{position:sticky;top:74px;}
.side-card h3{margin:0 0 10px;font-size:15px;}
.side-link{display:flex;align-items:center;gap:10px;padding:9px 8px;border-radius:8px;cursor:pointer;color:var(--text);font-size:14px;}
.side-link:hover{background:#f3f2ef;}
.side-link .dot{width:10px;height:10px;border-radius:3px;flex-shrink:0;}
.side-link .cnt{margin-left:auto;color:var(--sec);font-size:12px;}
.result-head{display:flex;align-items:center;gap:14px;margin-bottom:14px;}
.result-head b{color:var(--li-blue);}
.clear-btn{border:1px solid var(--li-blue);color:var(--li-blue);background:#fff;border-radius:999px;padding:6px 14px;cursor:pointer;font-size:13px;}
.clear-btn:hover{background:#eef3f8;}
.result-list{display:flex;flex-direction:column;gap:12px;}
.result-item{display:block;background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 16px;color:inherit;}
.result-item:hover{border-color:var(--li-blue);box-shadow:0 1px 5px rgba(10,102,194,.15);}
.ri-top{display:flex;align-items:center;gap:10px;margin-bottom:6px;}
.ri-module{font-size:12px;color:var(--sec);}
.ri-title{font-size:16px;font-weight:600;color:#1d2226;}
.result-item:hover .ri-title{color:var(--li-blue);}
.ri-snippet{font-size:13px;color:#3a3a3a;margin-top:6px;line-height:1.6;}
.ri-meta{font-size:12px;color:var(--sec);margin-top:8px;}
mark{background:#ffe39a;border-radius:3px;padding:0 1px;}
.empty{background:#fff;border:1px solid var(--border);border-radius:12px;padding:34px;text-align:center;color:var(--sec);}
.foot{text-align:center;color:var(--sec);font-size:12px;padding:10px 0 30px;}
@media(max-width:860px){.layout{flex-direction:column;}.sidebar{width:100%;}.side-card{position:static;}}
</style>
"""

BODY = """</head>
<body>
<header class="nav"><div class="nav-inner">
  <div class="logo"><span class="mark">知</span><span>知识库</span></div>
  <div class="search"><span class="ico">🔍</span><input id="search" type="text" placeholder="搜索文档标题与内容…（支持多个关键词，空格分隔）" autocomplete="off"></div>
</div></header>
<main class="container" id="top">
  <section class="hero" id="top-hero">
    <h1>个人知识库 · Knowledge Hub</h1>
    <p>管理学习 · 技术框架 · 业务描述语言 · 行业研究 · 数据处理 · 编程本质 · 英语学习 — 模块化整理，一键互联检索</p>
    <div class="stats">
      <div class="stat"><b>__STAT_DOCS__</b><span>篇文档</span></div>
      <div class="stat"><b>__STAT_MODS__</b><span>个模块</span></div>
      <div class="stat"><b>__STAT_WORDS__</b><span>可检索字符</span></div>
    </div>
  </section>
  <div class="pills" id="pills">__PILLS__</div>
  <div class="layout">
    <div class="feed" id="feed">__FEED__</div>
    <aside class="sidebar"><div class="card side-card">
      <h3>模块导航</h3>
      <div id="side-nav">__SIDEBAR__</div>
    </div></aside>
  </div>
  <div class="foot">由本地静态生成 · 点击任意文档可在新标签页打开原文</div>
</main>
"""

SCRIPT = r"""
// Static HTML is already in #feed. JS only enhances with search + filtering.
const MODULE_ORDER = __MODULE_ORDER__;
const MODULES = __MODULES__;
const ENTRIES = __ENTRIES__;
const STATIC_FEED = __STATIC_FEED__;

const feed = document.getElementById('feed');
const state = { q: "", cat: "all" };
feed.innerHTML = STATIC_FEED;

function esc(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function tokenize(q){ return q.toLowerCase().split(/\s+/).filter(Boolean); }
function reEsc(t){ return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function matchInfo(e, tokens){
  if(!tokens.length) return { hit:true, count:0 };
  const hay = (e.title + " " + e.content).toLowerCase();
  for(const t of tokens){ if(!hay.includes(t)) return { hit:false, count:0 }; }
  let count = 0;
  for(const t of tokens){ let i = 0; while((i = hay.indexOf(t, i)) >= 0){ count++; i += t.length; } }
  return { hit:true, count };
}
function highlight(s, tokens){
  s = esc(s);
  if(!tokens.length) return s;
  const re = new RegExp('(' + tokens.map(reEsc).join('|') + ')', 'gi');
  return s.replace(re, '<mark>$1</mark>');
}
function snippet(e, tokens){
  if(!tokens.length) return '';
  const hay = (e.title + " " + e.content).toLowerCase();
  let pos = -1;
  for(const t of tokens){ const p = hay.indexOf(t); if(p >= 0 && (pos < 0 || p < pos)) pos = p; }
  if(pos < 0) return '';
  const cpos = Math.max(0, pos - e.title.length - 1);
  const start = Math.max(0, cpos - 50);
  const slice = e.content.slice(start, start + 200);
  return (start > 0 ? '…' : '') + slice + (start + 200 < e.content.length ? '…' : '');
}

function applyCategory(){
  document.querySelectorAll('.module-card').forEach(c=>{
    c.style.display = (state.cat === 'all' || c.dataset.module === state.cat) ? '' : 'none';
  });
}

function renderSearch(){
  const tokens = tokenize(state.q);
  const searching = state.q.trim().length > 0;
  if(!searching){ feed.innerHTML = STATIC_FEED; applyCategory(); return; }
  let results = ENTRIES
    .filter(e => state.cat === 'all' || e.module === state.cat)
    .map(e => ({ e, m: matchInfo(e, tokens) }))
    .filter(x => x.m.hit);
  results.sort((a, b) => b.m.count - a.m.count);
  let html = '<div class="result-head">找到 <b>' + results.length +
    '</b> 个相关文档<button class="clear-btn" onclick="clearSearch()">清除搜索</button></div>';
  if(results.length === 0){
    html += '<div class="empty">没有找到匹配的内容，换个关键词试试。</div>';
  } else {
    html += '<div class="result-list">';
    for(const { e, m } of results){
      const sn = snippet(e, tokens);
      html += '<a class="result-item" href="' + e.href + '" target="_blank" rel="noopener">' +
        '<div class="ri-top"><span class="type-badge ' + (e.type === 'html' ? 't-html' : 't-md') + '">' +
        e.type.toUpperCase() + '</span><span class="ri-module">' + esc(MODULES[e.module].name) + '</span></div>' +
        '<div class="ri-title">' + highlight(e.title, tokens) + '</div>' +
        (sn ? '<div class="ri-snippet">' + highlight(sn, tokens) + '</div>' : '') +
        '<div class="ri-meta">匹配 ' + m.count + ' 处 · 打开查看 ↗</div></a>';
    }
    html += '</div>';
  }
  feed.innerHTML = html;
}
function clearSearch(){ document.getElementById('search').value = ''; state.q = ''; renderSearch(); }

document.getElementById('search').addEventListener('input', function(){ state.q = this.value; renderSearch(); });

document.querySelectorAll('[data-cat]').forEach(el => {
  el.addEventListener('click', function(ev){
    ev.preventDefault();
    state.cat = el.dataset.cat;
    document.querySelectorAll('[data-cat]').forEach(x => x.classList.toggle('active', x.dataset.cat === state.cat));
    if(state.q.trim()){ renderSearch(); }
    else { applyCategory(); }
    if(state.cat !== 'all'){
      const m = document.getElementById('mod-' + state.cat);
      if(m) m.scrollIntoView({ behavior:'smooth', block:'start' });
    } else {
      window.scrollTo({ top:0, behavior:'smooth' });
    }
  });
});

// init stats
document.getElementById('stat-docs').textContent = ENTRIES.length;
document.getElementById('stat-mods').textContent = MODULE_ORDER.filter(k => ENTRIES.some(e => e.module === k)).length;
document.getElementById('stat-words').textContent = (__TOTAL_WORDS__).toLocaleString('en-US');
"""

# Assemble
stat_docs = len(ENTRIES)
stat_mods = sum(1 for k in MODULE_ORDER if any(e["module"] == k for e in ENTRIES))

body = (BODY
        .replace("__STAT_DOCS__", str(stat_docs))
        .replace("__STAT_MODS__", str(stat_mods))
        .replace("__STAT_WORDS__", "{:,}".format(total_words))
        .replace("__PILLS__", pills_html())
        .replace("__FEED__", STATIC_FEED)
        .replace("__SIDEBAR__", sidebar_html()))

script = (SCRIPT
          .replace("__MODULE_ORDER__", js_str(MODULE_ORDER))
          .replace("__MODULES__", js_str(MODULES))
          .replace("__ENTRIES__", js_str(ENTRIES))
          .replace("__STATIC_FEED__", js_str(STATIC_FEED))
          .replace("__TOTAL_WORDS__", str(total_words)))

out = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<title>知识库 · Knowledge Hub</title>\n' + STYLE
       + body + '<script>\n' + script + '\n</script>\n</body>\n</html>\n')

with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(out)

print("Generated index.html")
print("  modules:", stat_mods, " docs:", stat_docs, " indexed chars:", total_words)
for e in ENTRIES:
    print("   -", e["module"], "|", e["type"], "|", e["title"][:38])
