# -*- coding: utf-8 -*-
"""Generate self-contained bilingual DSH plugin directory site (705 plugins).
Pages: index.html (zh-CN) + en.html (en). Feature parity with upstream aggregator
plus our own SEO/AEO extras. No references to the source aggregator site.
"""
import json, html, io, os, shutil, argparse

_parser = argparse.ArgumentParser(description="Generate the DeepSeek Whale static site")
_parser.add_argument("--out", required=True, help="Output directory (site root)")
_parser.add_argument("--catalog", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalog", "plugins.json"))
_parser.add_argument("--site", default="https://dsh-plugins.app.workbuddy.host/", help="Canonical site base URL (with trailing slash)")
_args = _parser.parse_args()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = _args.out
SITE = _args.site
os.makedirs(OUTDIR, exist_ok=True)

d = json.load(open(_args.catalog, encoding="utf-8"))
gen_at = d.get("generatedAt", "")[:10]

plugins = []
for p in d["plugins"]:
    repo = p.get("repository") or ""
    if "/" not in repo or p.get("archived") or p.get("disabled"):
        continue
    owner, name = repo.split("/", 1)
    pkg = p.get("package") or {}
    inst = (p.get("install") or {}).get("command") or f"dsh plugin --profile web add github:{repo}"
    desc = (p.get("description") or "").strip() or ""
    plugins.append({
        "r": repo, "o": owner, "n": name or repo, "d": desc,
        "l": p.get("language") or "其他", "li": p.get("license") or "NOASSERTION",
        "s": p.get("stars") or 0, "v": pkg.get("version") or "",
        "c": inst, "u": (p.get("pushedAt") or p.get("updatedAt") or "")[:10],
    })
plugins.sort(key=lambda x: (-x["s"], x["r"]))
langs = sorted({p["l"] for p in plugins if p["l"] != "其他"})
lics = sorted({p["li"] for p in plugins})
total = len(plugins)
print("plugins:", total, "langs:", len(langs))

def esc(s):
    return html.escape(s, quote=True)

data_json = json.dumps(plugins, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

def stars_fmt(n):
    return f"{n:,}"

def fill(t, o):
    o = {"m": "", "s": "", "t": "", **o}
    return t.replace("{n}", str(o["n"])).replace("{m}", str(o["m"])).replace("{s}", str(o["s"])).replace("{t}", str(o["t"]))

# ---------------- i18n strings ----------------
S = {
"zh": {
"html_lang":"zh-CN","locale":"zh-CN",
"title":f"DSH Plugins 插件目录 · {total} 个 DeepSeek Harness 插件搜索与安装指南",
"meta_desc":f"收录 {total} 个 DeepSeek Harness（DSH）社区插件，支持按名称、功能、语言和许可证搜索，一键复制跟随上游最新版本的插件安装命令。星标排行、筛选排序、安装指南与常见问题。",
"keywords":"DSH 插件, DeepSeek Harness 插件, dsh plugin, DSH 插件市场, DeepSeek 插件推荐, dsh-web, dsh-market, modsearch, dsh-context, AI 编程插件",
"og_title":f"DSH Plugins 插件目录 · {total} 个 DeepSeek Harness 插件",
"og_desc":f"搜索并安装 {total} 个 DeepSeek Harness 社区插件，一键复制最新版本安装命令。",
"tw_title":"DSH Plugins 插件目录 · DeepSeek Harness 插件搜索与安装指南",
"tw_desc":f"收录 {total} 个 DeepSeek Harness 社区插件，支持搜索、筛选与一键复制安装命令。",
"nav_catalog":"插件目录","nav_guide":"安装指南","nav_faq":"常见问题","nav_lang":"English",
"btn_to_light":"☀️ 明亮","btn_to_dark":"🌙 深海",
"h1_pre":"探索 ","h1_em":f"{total} 个 DSH 插件",
"sub":f"DeepSeek Harness（DSH）社区插件全量目录：搜索、筛选并一键安装。所有数据汇总自各插件的上游公开 GitHub 仓库，安装命令跟随上游默认分支最新版本。",
"st_total":"已收录插件","st_lang":"开发语言","st_lic":"开源许可证类型","st_snap":"数据快照日期",
"search_ph":"🔍 搜索插件名称、功能关键词、包名或作者…","aria_search":"搜索插件",
"lang_all":"全部语言","lic_all":"全部许可证","lic_unknown":"许可证未识别",
"sort_stars":"最多星标","sort_updated":"最近更新","sort_name":"名称","aria_sort":"排序方式","aria_lang":"语言筛选","aria_lic":"许可证筛选","aria_clear":"清除筛选",
"clear":"清除筛选","copy":"复制","copied":"已复制","kbd_hint":"聚焦搜索框",
"view_cards":"卡片","view_rows":"横条","aria_view":"切换目录视图",
"rsum_total":"共 {n} 个插件","rsum_note":"安装前请检查上游源码、权限和许可证",
"found":"找到 {n} 个匹配插件（共 {m} 个）","more":"再显示 {n} 个（已显示 {s}/{t}）",
"empty":"⌕ 没有找到匹配的插件，试试更短的关键词或清除筛选",
"default_desc":"该插件暂未填写介绍，详见上游仓库。",
"guide_h2":"如何安装 DSH 插件",
"guide":["搜索插件：输入名称、功能关键词或作者名，也可按开发语言与许可证缩小范围。",
"核对信息：查看仓库地址、包版本、许可证与最近更新时间，确认符合你的需求。",
"复制并运行：点击「复制」获取安装命令，在 DeepSeek Harness 所在终端执行，例如 "],
"guide_code":"dsh plugin --profile web add github:作者/仓库",
"guide_tail":"，安装后按上游文档完成配置。",
"faq_h2":"常见问题",
"faqs":[("DSH 插件是什么？","DSH 插件是安装到 DeepSeek Harness 的扩展包，可以为智能体增加工具、界面、模型接入、记忆、浏览器自动化等能力，每个插件由其上游 GitHub 仓库维护。"),
("如何安装 DSH 插件？","复制插件卡片上的安装命令，在终端执行 dsh plugin --profile web add github:作者/仓库名 即可。命令不含固定版本号，安装时会获取上游默认分支的最新版本。"),
("哪些 DSH 插件最受欢迎？","按社区星标排名，dsh-web（插件聚合生态）、dsh-market（可视化插件市场）、DSH-better-sidebar（开放侧边栏）、dsh-TUI（终端增强）、dsh-context（上下文可视化）等位居前列。支持一键按星标排序查看完整榜单。"),
("这些插件经过安全审计吗？","没有。本站只汇总公开仓库元数据（星标、语言、许可证、版本），收录不代表安全审计或官方背书，安装前请自行阅读上游源码、权限与许可证。"),
("DSH 插件免费吗？","收录插件均为开源项目，多数采用 MIT、Apache-2.0 等许可证，可自由安装、使用与二次开发。")],
"faq_open_first":True,
"footer_l":"🐋 DSH Plugins 插件目录 · DeepSeek Harness 社区插件导航",
"footer_r":"数据汇总自各插件上游公开 GitHub 仓库 · 社区维护，非官方站点",
"canonical":SITE,
},
"en": {
"html_lang":"en","locale":"en-US",
"title":f"DSH Plugins Directory · Search & Install {total} DeepSeek Harness Plugins",
"meta_desc":f"Browse {total} DeepSeek Harness (DSH) community plugins. Search by name, feature, language or license, and copy the install command that tracks the upstream default branch. Star rankings, filters, install guide and FAQ.",
"keywords":"DSH plugins, DeepSeek Harness plugins, dsh plugin, dsh-market, dsh-web, modsearch, dsh-context, AI coding plugins",
"og_title":f"DSH Plugins Directory · {total} DeepSeek Harness Plugins",
"og_desc":f"Search and install {total} DeepSeek Harness community plugins with one-click copy install commands.",
"tw_title":"DSH Plugins Directory · DeepSeek Harness Plugin Search & Install Guide",
"tw_desc":f"{total} DeepSeek Harness community plugins with search, filters and one-click install commands.",
"nav_catalog":"Plugins","nav_guide":"Install Guide","nav_faq":"FAQ","nav_lang":"中文",
"btn_to_light":"☀️ Light","btn_to_dark":"🌙 Deep Sea",
"h1_pre":"Explore ","h1_em":f"{total} DSH Plugins",
"sub":f"The complete directory of DeepSeek Harness (DSH) community plugins: search, filter and install in one click. All data is aggregated from each plugin's public upstream GitHub repository; install commands track the upstream default branch.",
"st_total":"Plugins indexed","st_lang":"Languages","st_lic":"Open-source licenses","st_snap":"Data snapshot",
"search_ph":"🔍 Search plugins by name, feature, package or author…","aria_search":"Search plugins",
"lang_all":"All languages","lic_all":"All licenses","lic_unknown":"License unknown",
"sort_stars":"Most stars","sort_updated":"Recently updated","sort_name":"Name","aria_sort":"Sort by","aria_lang":"Language filter","aria_lic":"License filter","aria_clear":"Clear filters",
"clear":"Clear filters","copy":"Copy","copied":"Copied","kbd_hint":"to focus search",
"view_cards":"Cards","view_rows":"Rows","aria_view":"Switch directory view",
"rsum_total":"{n} plugins in total","rsum_note":"Review upstream source, permissions and license before installing",
"found":"{n} matching plugins ({m} in total)","more":"Show {n} more ({s}/{t} shown)",
"empty":"⌕ No matching plugins. Try a shorter keyword or clear the filters.",
"default_desc":"The upstream repository has not provided a description yet.",
"guide_h2":"How to Install DSH Plugins",
"guide":["Search: type a name, feature keyword or author; narrow down by language and license.",
"Verify: check the repository, package version, license and last-updated date.",
"Copy & run: click \"Copy\" and run the command in the DeepSeek Harness terminal, e.g. "],
"guide_code":"dsh plugin --profile web add github:author/repo",
"guide_tail":", then follow the upstream docs to configure.",
"faq_h2":"Frequently Asked Questions",
"faqs":[("What are DSH plugins?","DSH plugins are extension packages installed into DeepSeek Harness. They add tools, UI, model access, memory, browser automation and more. Each plugin is maintained by its upstream GitHub repository."),
("How do I install a DSH plugin?","Copy the install command from a plugin card and run it in your terminal: dsh plugin --profile web add github:author/repo. Commands carry no pinned version — the latest version from the upstream default branch is fetched at install time."),
("Which DSH plugins are most popular?","By community stars, dsh-web (plugin aggregation ecosystem), dsh-market (visual plugin market), DSH-better-sidebar (open sidebar), dsh-TUI (terminal enhancement) and dsh-context (context visualization) lead the board. Sort by stars to see the full ranking."),
("Are these plugins security audited?","No. This site only aggregates public repository metadata (stars, language, license, version). Inclusion is not a security audit or official endorsement — review upstream source, permissions and license before installing."),
("Are DSH plugins free?","All indexed plugins are open source, mostly under MIT or Apache-2.0 licenses, free to install, use and modify.")],
"faq_open_first":True,
"footer_l":"🐋 DSH Plugins Directory · DeepSeek Harness community plugin navigation",
"footer_r":"Data aggregated from each plugin's public upstream GitHub repository · community-maintained, not official",
"canonical":SITE+"en.html",
}}

def lang_opts(L):
    return "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in langs)

def lic_opts(L):
    return "".join(f'<option value="{esc(x)}">{L["lic_unknown"] if x=="NOASSERTION" else esc(x)}</option>' for x in lics)

def cards_html(L):
    out = []
    for i, p in enumerate(plugins[:24], 1):
        ver = f' · v{esc(p["v"])}' if p["v"] else ""
        desc = esc(p["d"]) if p["d"] else L["default_desc"]
        out.append(f'''<li class="card" data-r="{esc(p["r"])}">
  <div class="chead"><span class="rank">#{i}</span><h3><a href="https://github.com/{esc(p["r"])}" target="_blank" rel="noopener">{esc(p["n"])}</a></h3><span class="stars">★ {stars_fmt(p["s"])}</span></div>
  <p class="meta">@{esc(p["o"])} · {esc(p["l"])} · {esc(p["li"])}{ver}</p>
  <p class="desc">{desc}</p>
  <div class="cmd"><code>{esc(p["c"])}</code><button class="copy" type="button" data-cmd="{esc(p["c"])}">{L["copy"]}</button></div>
</li>''')
    return "\n".join(out)

def faq_html(L):
    parts = []
    for i, (q, a) in enumerate(L["faqs"]):
        op = " open" if i == 0 and L["faq_open_first"] else ""
        parts.append(f'<details{op}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>')
    return "\n".join(parts)

def guide_html(L):
    g = L["guide"]
    return (f'<ol><li><b>{esc(g[0])}</b></li><li><b>{esc(g[1])}</b></li>'
            f'<li><b>{esc(g[2])}</b><code>{esc(L["guide_code"])}</code>{esc(L["guide_tail"])}</li></ol>')

def ld_json(L):
    ld = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "WebSite", "@id": L["canonical"]+"#website", "url": L["canonical"],
         "name": L["og_title"], "alternateName": "DeepSeek Harness Plugin Directory",
         "description": L["meta_desc"], "inLanguage": L["html_lang"]},
        {"@type": "CollectionPage", "url": L["canonical"], "name": L["og_title"],
         "inLanguage": L["html_lang"],
         "mainEntity": {"@type": "ItemList", "numberOfItems": total,
            "itemListElement": [{"@type":"ListItem","position":i,"name":p["r"],
                "url":f"https://github.com/{p['r']}"} for i,p in enumerate(plugins[:24],1)]}},
        {"@type": "FAQPage", "mainEntity": [
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}
            for q,a in L["faqs"]]},
    ]}
    return json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

def msg_json(L):
    m = {"found":L["found"],"more":L["more"],"copy":L["copy"],"copied":L["copied"],
         "copyFail":L["copy"],"default_desc":L["default_desc"]}
    return json.dumps(m, ensure_ascii=False).replace("</", "<\\/")

TPL = '''<!DOCTYPE html>
<html lang="__HTML_LANG__" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="description" content="__META_DESC__">
<meta name="keywords" content="__KEYWORDS__">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="__CANON__">
<link rel="alternate" hreflang="zh-CN" href="__SITE__">
<link rel="alternate" hreflang="en" href="__SITE__en.html">
<link rel="alternate" hreflang="x-default" href="__SITE__">
<link rel="alternate" type="application/rss+xml" title="DSH Plugins 最新插件 / Latest Plugins" href="feed.xml">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DSH Plugins 插件目录">
<meta property="og:locale" content="__LOCALE__">
<meta property="og:url" content="__CANON__">
<meta property="og:title" content="__OG_TITLE__">
<meta property="og:description" content="__OG_DESC__">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="__TW_TITLE__">
<meta name="twitter:description" content="__TW_DESC__">
<script type="application/ld+json">__LD__</script>
<style>
:root{color-scheme:dark;--bg1:#071522;--bg2:#0d2436;--card:rgba(255,255,255,.045);--card-br:rgba(255,255,255,.09);--tx:#e8f1f8;--tx2:#9db4c4;--ac:#22d3ee;--ac2:#38bdf8;--star:#fbbf24;--code:rgba(34,211,238,.08)}
[data-theme="light"]{color-scheme:light;--bg1:#eef5fa;--bg2:#dcebf5;--card:#fff;--card-br:#d5e3ee;--tx:#12293b;--tx2:#54728a;--ac:#0891b2;--ac2:#0284c7;--star:#d97706;--code:rgba(8,145,178,.07)}
select option{background:#0d2436;color:#e8f1f8}
[data-theme="light"] select option{background:#fff;color:#12293b}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:linear-gradient(160deg,var(--bg1),var(--bg2));color:var(--tx);line-height:1.7;min-height:100vh}
a{color:var(--ac2);text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);background:rgba(7,21,34,.72);border-bottom:1px solid var(--card-br)}
[data-theme="light"] header{background:rgba(238,245,250,.8)}
.nav{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:18px;padding:14px 24px;flex-wrap:wrap}
.logo{font-size:20px;font-weight:800;display:flex;align-items:center;gap:8px;color:var(--tx)}
.logo span{background:linear-gradient(90deg,var(--ac),var(--ac2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
nav.links{display:flex;gap:16px;margin-left:auto;flex-wrap:wrap;align-items:center}
nav.links a{color:var(--tx2);font-size:14px}nav.links a:hover{color:var(--ac)}
nav.links a.lang{border:1px solid var(--card-br);border-radius:999px;padding:3px 12px}
#themeBtn,#clearBtn{border:1px solid var(--card-br);background:var(--card);color:var(--tx);border-radius:10px;padding:6px 12px;cursor:pointer;font-size:14px}
#clearBtn{display:none;border-radius:999px;font-size:13px}
#clearBtn.show{display:inline-block}
.seg{display:flex;border:1px solid var(--card-br);border-radius:12px;overflow:hidden}
.seg button{border:none;background:transparent;color:var(--tx2);padding:10px 14px;cursor:pointer;font-size:13px;white-space:nowrap}
.seg button.on{background:var(--ac);color:#04222c;font-weight:700}
.hero{max-width:1200px;margin:0 auto;padding:64px 24px 36px;text-align:center}
.hero h1{font-size:clamp(28px,5vw,46px);font-weight:900;letter-spacing:-.5px}
.hero h1 em{font-style:normal;background:linear-gradient(90deg,var(--ac),var(--ac2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.hero p.sub{max-width:780px;margin:16px auto 0;color:var(--tx2);font-size:17px}
.stats{display:flex;gap:28px;justify-content:center;margin-top:28px;flex-wrap:wrap}
.stats b{font-size:26px;display:block;background:linear-gradient(90deg,var(--ac),var(--ac2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.stats span{font-size:13px;color:var(--tx2)}
.controls{max-width:1200px;margin:0 auto;padding:16px 24px 0;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
#search{flex:1;min-width:220px;padding:11px 16px;border-radius:12px;border:1px solid var(--card-br);background:var(--card);color:var(--tx);font-size:15px;outline:none}
#search:focus{border-color:var(--ac)}
select{padding:11px 12px;border-radius:12px;border:1px solid var(--card-br);background:var(--card);color:var(--tx);font-size:14px;cursor:pointer;outline:none}
.kbd{color:var(--tx2);font-size:12px;white-space:nowrap}
.kbd b{border:1px solid var(--card-br);border-radius:6px;padding:1px 7px;font-family:ui-monospace,monospace;color:var(--ac);font-weight:700}
.rsum{max-width:1200px;margin:0 auto;padding:12px 24px 0;color:var(--tx2);font-size:13px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.grid{max-width:1200px;margin:0 auto;padding:14px 24px 12px;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;list-style:none}
.card{background:var(--card);border:1px solid var(--card-br);border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:8px;transition:transform .18s,border-color .18s}
.card:hover{transform:translateY(-3px);border-color:var(--ac)}
.chead{display:flex;align-items:baseline;gap:10px}
.rank{font-size:12px;font-weight:800;color:var(--ac);min-width:32px}
.chead h3{font-size:16px;flex:1;word-break:break-all}
.chead h3 a{color:var(--tx)}
.stars{color:var(--star);font-size:13px;font-weight:700;white-space:nowrap}
.meta{font-size:12px;color:var(--tx2)}
.desc{font-size:13.5px;color:var(--tx);opacity:.88;flex:1}
.cmd{display:flex;align-items:center;gap:10px;background:var(--code);border:1px solid var(--card-br);border-radius:12px;padding:10px 14px}
.cmd code{flex:1;font-family:ui-monospace,Consolas,monospace;font-size:12.5px;color:var(--ac);word-break:break-all}
.copy{border:none;background:var(--ac);color:#04222c;font-weight:700;border-radius:8px;padding:5px 12px;cursor:pointer;font-size:12px;white-space:nowrap}
.grid.rows{display:flex;flex-direction:column;gap:8px}
.grid.rows .card{flex-direction:row;flex-wrap:wrap;align-items:center;gap:2px 14px;padding:10px 16px;border-radius:12px}
.grid.rows .card:hover{transform:none}
.grid.rows .chead{flex:1 1 100%;gap:10px}
.grid.rows .chead h3{font-size:15px}
.grid.rows .meta{font-size:12px}
.grid.rows .desc{flex:1 1 200px;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px}
.grid.rows .cmd{flex:0 1 auto;min-width:0;padding:6px 10px}
.grid.rows .cmd code{font-size:12px}
#loadMore{display:block;margin:8px auto 36px;border:1px solid var(--ac);background:transparent;color:var(--ac);border-radius:999px;padding:10px 28px;cursor:pointer;font-size:14px;font-weight:700}
#loadMore.hidden{display:none}
#loadMore:hover{background:var(--ac);color:#04222c}
#empty{display:none;text-align:center;color:var(--tx2);padding:36px}
#copyStatus{position:fixed;left:-9999px}
section.block{max-width:1200px;margin:0 auto;padding:28px 24px}
section.block h2{font-size:26px;font-weight:800;margin-bottom:14px}
section.block h2::before{content:"🐋 ";font-size:20px}
section.block p,section.block li{color:var(--tx2);font-size:15px}
section.block ol{padding-left:22px;display:grid;gap:8px}
section.block code{background:var(--code);border-radius:6px;padding:1px 6px;font-size:13px;color:var(--ac)}
details{background:var(--card);border:1px solid var(--card-br);border-radius:14px;padding:15px 20px;margin-bottom:10px}
details summary{cursor:pointer;font-weight:700;font-size:15px;color:var(--tx)}
details p{margin-top:8px}
footer{border-top:1px solid var(--card-br);margin-top:36px}
footer .in{max-width:1200px;margin:0 auto;padding:26px 24px;color:var(--tx2);font-size:13px;display:flex;gap:16px;flex-wrap:wrap;justify-content:space-between}
@media(max-width:640px){.hero{padding:44px 18px 24px}.grid{grid-template-columns:1fr}.kbd{display:none}}
</style>
</head>
<body>
<header>
  <div class="nav">
    <div class="logo">🐋 <span>DSH Plugins</span> 插件目录</div>
    <nav class="links">
      <a href="#plugins">__NAV_CATALOG__</a>
      <a href="#guide">__NAV_GUIDE__</a>
      <a href="#faq">__NAV_FAQ__</a>
      <a class="lang" href="__LANG_HREF__" hreflang="__LANG_HREFLANG__">__NAV_LANG__</a>
      <button id="themeBtn" onclick="toggleTheme()">__BTN_LIGHT__</button>
    </nav>
  </div>
</header>

<main>
<section class="hero">
  <h1>__H1_PRE__<em>__H1_EM__</em></h1>
  <p class="sub">__SUB__</p>
  <div class="stats">
    <div><b>__TOTAL__</b><span>__ST_TOTAL__</span></div>
    <div><b>__NLANG__</b><span>__ST_LANG__</span></div>
    <div><b>__NLIC__</b><span>__ST_LIC__</span></div>
    <div><b>__SNAPSHOT__</b><span>__ST_SNAP__</span></div>
  </div>
</section>

<div class="controls" id="plugins">
  <input id="search" type="search" placeholder="__SEARCH_PH__" aria-label="__ARIA_SEARCH__" autocomplete="off">
  <select id="langSel" aria-label="__ARIA_LANG__"><option value="all">__LANG_ALL__</option>__LANGOPTS__</select>
  <select id="licSel" aria-label="__ARIA_LIC__"><option value="all">__LIC_ALL__</option>__LICOPTS__</select>
  <select id="sortSel" aria-label="__ARIA_SORT__">
    <option value="stars">__SORT_STARS__</option>
    <option value="updated">__SORT_UPDATED__</option>
    <option value="name">__SORT_NAME__</option>
  </select>
  <button id="clearBtn" type="button" aria-label="__ARIA_CLEAR__">✕ __CLEAR__</button>
  <div class="seg" role="group" aria-label="__ARIA_VIEW__">
    <button id="viewCards" class="on" type="button">▦ __VIEW_CARDS__</button>
    <button id="viewRows" type="button">☰ __VIEW_ROWS__</button>
  </div>
</div>
<div class="rsum"><span id="rsummary">__RSUM_TOTAL__</span><span class="kbd"><b>/</b> __KBD_HINT__</span><span>__RSUM_NOTE__</span></div>

<ul class="grid" id="grid">
__CARDS__
</ul>
<p id="empty">__EMPTY__</p>
<button id="loadMore" type="button">__MORE0__</button>
<p id="copyStatus" role="status" aria-live="polite"></p>

<section class="block" id="guide">
  <h2>__GUIDE_H2__</h2>
  __GUIDE__
</section>

<section class="block" id="faq">
  <h2>__FAQ_H2__</h2>
  __FAQ__
</section>
</main>

<footer>
  <div class="in">
    <div>__FOOTER_L__</div>
    <div>__FOOTER_R__</div>
  </div>
</footer>

<script id="plugin-data" type="application/json">__DATA__</script>
<script>
const MSG = __MSG__;
const DATA = JSON.parse(document.getElementById('plugin-data').textContent);
const PAGE = 24;
let cur = {q:'', lang:'all', lic:'all', sort:'stars'}, shown = PAGE;
const $ = id => document.getElementById(id);
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function fmt(n){return n.toLocaleString('en-US');}
function fill(t,o){return t.replace('{n}',o.n).replace('{m}',o.m).replace('{s}',o.s).replace('{t}',o.t);}
function cardHTML(p,i){
  const ver = p.v ? ' · v'+esc(p.v) : '';
  const d = p.d ? esc(p.d) : esc(MSG.default_desc);
  return '<li class="card"><div class="chead"><span class="rank">#'+(i+1)+'</span><h3><a href="https://github.com/'+esc(p.r)+'" target="_blank" rel="noopener">'+esc(p.n)+'</a></h3><span class="stars">★ '+fmt(p.s)+'</span></div>'
    +'<p class="meta">@'+esc(p.o)+' · '+esc(p.l)+' · '+esc(p.li)+ver+'</p>'
    +'<p class="desc">'+d+'</p>'
    +'<div class="cmd"><code>'+esc(p.c)+'</code><button class="copy" type="button" data-cmd="'+esc(p.c)+'">'+esc(MSG.copy)+'</button></div></li>';
}
function filtered(){
  let list = DATA.filter(p =>
    (cur.lang==='all'||p.l===cur.lang) && (cur.lic==='all'||p.li===cur.lic) &&
    (!cur.q || (p.r+' '+p.n+' '+p.d+' '+p.o).toLowerCase().includes(cur.q))
  );
  if(cur.sort==='stars') list.sort((a,b)=>b.s-a.s);
  else if(cur.sort==='updated') list.sort((a,b)=>(b.u||'').localeCompare(a.u||''));
  else list.sort((a,b)=>a.n.localeCompare(b.n));
  return list;
}
function syncUrl(){
  const u = new URL(location.href); const sp = u.searchParams;
  cur.q ? sp.set('q',cur.q) : sp.delete('q');
  cur.lang!=='all' ? sp.set('language',cur.lang) : sp.delete('language');
  cur.lic!=='all' ? sp.set('license',cur.lic) : sp.delete('license');
  cur.sort!=='stars' ? sp.set('sort',cur.sort) : sp.delete('sort');
  history.replaceState(null,'',u.pathname+(u.search?'?'+sp.toString():'')+location.hash);
}
function syncClearBtn(){
  const active = cur.q||cur.lang!=='all'||cur.lic!=='all'||cur.sort!=='stars';
  $('clearBtn').classList.toggle('show', !!active);
}
function readUrl(){
  const sp = new URLSearchParams(location.search);
  cur.q = (sp.get('q')||'').toLowerCase();
  cur.lang = sp.get('language')||'all';
  cur.lic = sp.get('license')||'all';
  cur.sort = sp.get('sort')||'stars';
  if(!['stars','updated','name'].includes(cur.sort)) cur.sort='stars';
  $('search').value = cur.q;
  $('langSel').value = cur.lang; $('licSel').value = cur.lic; $('sortSel').value = cur.sort;
}
function render(){
  const list = filtered();
  $('rsummary').textContent = fill(MSG.found,{n:list.length,m:DATA.length});
  const grid = $('grid');
  grid.innerHTML = list.slice(0,shown).map(cardHTML).join('');
  $('empty').style.display = list.length?'none':'block';
  const btn = $('loadMore');
  btn.classList.toggle('hidden', shown>=list.length);
  btn.textContent = fill(MSG.more,{n:Math.min(PAGE,list.length-shown),s:Math.min(shown,list.length),t:list.length});
  syncClearBtn();
}
function onFilter(){shown=PAGE;syncUrl();render();}
$('search').addEventListener('input',e=>{cur.q=e.target.value.trim().toLowerCase();onFilter();});
$('langSel').addEventListener('change',e=>{cur.lang=e.target.value;onFilter();});
$('licSel').addEventListener('change',e=>{cur.lic=e.target.value;onFilter();});
$('sortSel').addEventListener('change',e=>{cur.sort=e.target.value;onFilter();});
$('loadMore').addEventListener('click',()=>{shown+=PAGE;render();});
$('clearBtn').addEventListener('click',()=>{
  cur={q:'',lang:'all',lic:'all',sort:'stars'};shown=PAGE;
  $('search').value='';$('langSel').value='all';$('licSel').value='all';$('sortSel').value='stars';
  syncUrl();render();
});
function setView(v,save){
  $('grid').classList.toggle('rows', v==='rows');
  $('viewCards').classList.toggle('on', v!=='rows');
  $('viewRows').classList.toggle('on', v==='rows');
  if(save)localStorage.setItem('dsh-view',v);
}
$('viewCards').addEventListener('click',()=>setView('cards',true));
$('viewRows').addEventListener('click',()=>setView('rows',true));
setView(localStorage.getItem('dsh-view')||'cards',false);
document.addEventListener('keydown',e=>{
  if(e.key==='/' && !/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)){
    e.preventDefault();$('search').focus();
  }
});
document.addEventListener('click',e=>{
  const a=e.target.closest('a[href^="#"]');if(!a)return;
  const t=document.querySelector(a.getAttribute('href'));
  if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});history.replaceState(null,'',a.getAttribute('href'));}
});
document.addEventListener('click',e=>{
  const b=e.target.closest('.copy');if(!b)return;
  const done=()=>{b.textContent=MSG.copied;$('copyStatus').textContent=b.dataset.cmd+' ✓';
    setTimeout(()=>{b.textContent=MSG.copy;$('copyStatus').textContent='';},1200);};
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(b.dataset.cmd).then(done).catch(()=>fallback(b,done));
  }else{fallback(b,done);}
});
function fallback(b,done){
  const code=b.parentElement.querySelector('code');
  const r=document.createRange();r.selectNodeContents(code);
  const sel=getSelection();sel.removeAllRanges();sel.addRange(r);
  try{document.execCommand('copy');done();}catch(err){sel.removeAllRanges();}
}
function toggleTheme(){
  const h=document.documentElement,t=h.dataset.theme==='dark'?'light':'dark';
  h.dataset.theme=t;localStorage.setItem('dsh-theme',t);
  $('themeBtn').textContent=t==='dark'?'__BTN_LIGHT__':'__BTN_DARK__';
}
(function(){const t=localStorage.getItem('dsh-theme');if(t){document.documentElement.dataset.theme=t;document.getElementById('themeBtn').textContent=t==='dark'?'__BTN_LIGHT__':'__BTN_DARK__';}})();
readUrl();render();
</script>
</body>
</html>'''

def build(lang_key, other_page, other_hreflang):
    L = S[lang_key]
    page = TPL
    reps = {
        "__HTML_LANG__": L["html_lang"], "__LOCALE__": L["locale"],
        "__TITLE__": L["title"], "__META_DESC__": L["meta_desc"], "__KEYWORDS__": L["keywords"],
        "__CANON__": L["canonical"], "__SITE__": SITE,
        "__OG_TITLE__": L["og_title"], "__OG_DESC__": L["og_desc"],
        "__TW_TITLE__": L["tw_title"], "__TW_DESC__": L["tw_desc"],
        "__LD__": ld_json(L), "__MSG__": msg_json(L),
        "__NAV_CATALOG__": L["nav_catalog"], "__NAV_GUIDE__": L["nav_guide"], "__NAV_FAQ__": L["nav_faq"],
        "__NAV_LANG__": L["nav_lang"], "__LANG_HREF__": other_page, "__LANG_HREFLANG__": other_hreflang,
        "__BTN_LIGHT__": L["btn_to_light"], "__BTN_DARK__": L["btn_to_dark"],
        "__H1_PRE__": L["h1_pre"], "__H1_EM__": L["h1_em"], "__SUB__": L["sub"],
        "__TOTAL__": str(total), "__NLANG__": str(len(langs)), "__NLIC__": str(len(lics)),
        "__SNAPSHOT__": gen_at or "2026-09-12",
        "__ST_TOTAL__": L["st_total"], "__ST_LANG__": L["st_lang"], "__ST_LIC__": L["st_lic"], "__ST_SNAP__": L["st_snap"],
        "__SEARCH_PH__": L["search_ph"], "__ARIA_SEARCH__": L["aria_search"],
        "__LANG_ALL__": L["lang_all"], "__LIC_ALL__": L["lic_all"],
        "__ARIA_LANG__": L["aria_lang"], "__ARIA_LIC__": L["aria_lic"], "__ARIA_SORT__": L["aria_sort"], "__ARIA_CLEAR__": L["aria_clear"],
        "__SORT_STARS__": L["sort_stars"], "__SORT_UPDATED__": L["sort_updated"], "__SORT_NAME__": L["sort_name"],
        "__CLEAR__": L["clear"], "__KBD_HINT__": L.get("kbd_hint",""),
        "__VIEW_CARDS__": L["view_cards"], "__VIEW_ROWS__": L["view_rows"], "__ARIA_VIEW__": L["aria_view"],
        "__RSUM_TOTAL__": L["rsum_total"].replace("{n}", str(total)), "__RSUM_NOTE__": L["rsum_note"],
        "__EMPTY__": L["empty"], "__MORE0__": fill(L["more"], {"n": 24, "s": 24, "t": total}),
        "__GUIDE_H2__": L["guide_h2"], "__GUIDE__": guide_html(L),
        "__FAQ_H2__": L["faq_h2"], "__FAQ__": faq_html(L),
        "__FOOTER_L__": L["footer_l"], "__FOOTER_R__": L["footer_r"],
        "__CARDS__": cards_html(L), "__DATA__": data_json,
        "__LANGOPTS__": lang_opts(L), "__LICOPTS__": lic_opts(L),
    }
    for k, v in reps.items():
        page = page.replace(k, v)
    return page

import os
zh = build("zh", SITE+"en.html", "en")
en = build("en", SITE, "zh-CN")
io.open(os.path.join(OUTDIR, "index.html"), "w", encoding="utf-8", newline="\n").write(zh)
io.open(os.path.join(OUTDIR, "en.html"), "w", encoding="utf-8", newline="\n").write(en)
print("index.html:", f"{len(zh)/1024:.0f} KB", "| en.html:", f"{len(en)/1024:.0f} KB")

# favicon.svg
FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🐋</text></svg>'
io.open(os.path.join(OUTDIR, "favicon.svg"), "w", encoding="utf-8", newline="\n").write(FAVICON)

# manifest.webmanifest
manifest = {
    "name": "DSH Plugins 插件目录 / DeepSeek Harness Plugin Directory",
    "short_name": "DSH Plugins",
    "start_url": SITE,
    "lang": "zh-CN",
    "display": "standalone",
    "background_color": "#071522",
    "theme_color": "#173c58",
    "icons": [{"src": SITE+"favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
}
io.open(os.path.join(OUTDIR, "manifest.webmanifest"), "w", encoding="utf-8", newline="\n").write(json.dumps(manifest, ensure_ascii=False, indent=2))

# feed.xml (RSS, top 24 by stars)
items = []
for p in plugins[:24]:
    items.append(f"""    <item>
      <title>{esc(p['n'])} ★ {p['s']}</title>
      <link>https://github.com/{esc(p['r'])}</link>
      <guid isPermaLink="false">{esc(p['r'])}</guid>
      <description>{esc(p['d'][:300])}</description>
    </item>""")
feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>DSH Plugins 插件目录 · 最新热门插件</title>
    <link>{SITE}</link>
    <description>DeepSeek Harness (DSH) 社区插件目录 · 星标前 24 名 / Top plugins by stars</description>
    <language>zh-cn</language>
    <lastBuildDate>Sat, 12 Sep 2026 00:00:00 GMT</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
io.open(os.path.join(OUTDIR, "feed.xml"), "w", encoding="utf-8", newline="\n").write(feed)

# sitemap.xml (zh + en)
sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>{SITE}</loc>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}en.html"/>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{SITE}en.html</loc>
    <xhtml:link rel="alternate" hreflang="zh-CN" href="{SITE}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}en.html"/>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
"""
io.open(os.path.join(OUTDIR, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sitemap)
print("favicon.svg / manifest.webmanifest / feed.xml / sitemap.xml written")

# robots.txt
_robots = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n"
io.open(os.path.join(OUTDIR, "robots.txt"), "w", encoding="utf-8", newline="\n").write(_robots)
print("robots.txt written")

# llms.txt (assets template, keep UTF-8 BOM for no-charset scenarios; __COUNT__ = plugin count)
_llms_src = os.path.join(REPO_ROOT, "assets", "llms.txt")
if os.path.exists(_llms_src):
    _llms = io.open(_llms_src, "r", encoding="utf-8-sig").read()
    _llms = _llms.replace("__COUNT__", str(len(plugins)))
    io.open(os.path.join(OUTDIR, "llms.txt"), "w", encoding="utf-8-sig", newline="\n").write(_llms)
    print("llms.txt written (with BOM, count=%d)" % len(plugins))
