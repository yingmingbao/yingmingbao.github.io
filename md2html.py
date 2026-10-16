# -*- coding: utf-8 -*-
"""
md2html — 一个轻量、零依赖的 Markdown → HTML 转换程序。

用法（作为程序直接运行）：
    python md2html.py input.md                 # 输出到 input.html
    python md2html.py input.md output.html     # 指定输出
    python md2html.py input.md - title="xxx"   # 指定标题

作为模块导入（build_index.py 使用）：
    from md2html import convert
    html = convert(md_text, title="...", back_href="../index.html", source_label="管理学习")

支持：ATX 标题(#~######)、围栏代码块(```)、行内代码、粗体/斜体、
链接、图片、无序/有序列表（含嵌套）、引用、表格、分隔线、段落。
生成的文档自带阅读样式、目录(TOC)与“返回知识库”链接。
"""
import re
import sys
import os


# --------------------------------------------------------------------------
# 行内格式
# --------------------------------------------------------------------------
def _inline(text):
    # 1) 抽取行内代码，避免其内部被二次格式化
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return "\x00CODE%d\x00" % (len(codes) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)
    # 2) 转义 HTML 特殊字符（防止原始 < > 被当作标签 / 脚本注入）
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # 3) 图片
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    # 4) 链接（保留外部链接新窗口打开）
    def link(m):
        url = m.group(2)
        target = ' target="_blank" rel="noopener"' if re.match(r"https?://", url) else ""
        return '<a href="%s"%s>%s</a>' % (url, target, m.group(1))

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    # 5) 粗体
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    # 6) 斜体
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"<em>\1</em>", text)
    # 7) 还原代码
    def restore(m):
        c = codes[int(m.group(1))]
        return "<code>" + c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</code>"

    text = re.sub(r"\x00CODE(\d+)\x00", restore, text)
    return text


def _slug(txt):
    s = re.sub(r"[^\w一-鿿]+", "-", txt).strip("-")
    return s or "section"


# --------------------------------------------------------------------------
# 列表（递归，支持嵌套）
# --------------------------------------------------------------------------
def _indent(s):
    return len(s) - len(s.lstrip(" "))


def _is_list_item(s):
    return bool(re.match(r"^\s*([-*+]|\d+\.)\s+", s))


def _parse_list(lines, i, base_indent):
    first = lines[i]
    ordered = bool(re.match(r"^\s*\d+\.\s+", first))
    tag = "ol" if ordered else "ul"
    parts = []

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and _is_list_item(lines[j]) and _indent(lines[j]) >= base_indent:
                i = j
                continue
            break

        ind = _indent(line)
        if ind < base_indent:
            break
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if not m:
            break

        item_indent = len(m.group(1))
        content_lines = [m.group(3)]
        i += 1

        while i < len(lines):
            nl = lines[i]
            if not nl.strip():
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and _indent(lines[j]) > item_indent and _is_list_item(lines[j]):
                    break  # 嵌套列表交给递归
                if j < len(lines) and _indent(lines[j]) > item_indent and not _is_list_item(lines[j]):
                    content_lines.append(nl.strip())
                    i += 1
                    continue
                break
            nl_ind = _indent(nl)
            if _is_list_item(nl):
                if nl_ind == base_indent:
                    break  # 同级下一个条目
                if nl_ind > base_indent:
                    sub, i = _parse_list(lines, i, nl_ind)
                    content_lines.append("\n" + sub + "\n")
                    continue
                break
            elif nl_ind > item_indent:
                content_lines.append(nl.strip())
                i += 1
                continue
            else:
                break

        # 把内容与可能的嵌套 HTML 分开：嵌套块以 \n<html>\n 形式存在
        blocks = re.split(r"\n(<(?:ul|ol)[^>]*>[\s\S]*?</(?:ul|ol)>)\n", "\n".join(content_lines))
        html = ""
        for b in blocks:
            if re.match(r"^<(?:ul|ol)[^>]*>", b.strip()):
                html += b
            elif b.strip():
                html += "<p>" + _inline(b.strip()) + "</p>"
        parts.append("<li>" + html + "</li>")

    return "<%s class='md-list'>\n%s\n</%s>" % (tag, "\n".join(parts), tag), i


def _is_block_start(line, lines, i):
    s = line.strip()
    if not s:
        return False
    if s.startswith("```"):
        return True
    if re.match(r"^#{1,6}\s+", line):
        return True
    if re.match(r"^(---|\*\*\*|___)\s*$", s):
        return True
    if s.startswith(">"):
        return True
    if "|" in s and i + 1 < len(lines) and "-" in lines[i + 1] and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]):
        return True
    if _is_list_item(line):
        return True
    return False


# --------------------------------------------------------------------------
# 主转换
# --------------------------------------------------------------------------
def convert(md_text, title=None, back_href="../index.html", source_label=""):
    lines = md_text.replace("\r\n", "\n").split("\n")
    out = []
    toc = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        s = line.strip()

        # 围栏代码块
        if s.startswith("```"):
            lang = s[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```
            code = "\n".join(buf)
            code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            cls = "code" + (" lang-" + lang if lang else "")
            out.append("<pre class='%s'><code>%s</code></pre>" % (cls, code))
            continue

        if not s:
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            txt = m.group(2).strip()
            anchor = _slug(txt)
            # 避免锚点重复
            base = anchor
            cnt = 1
            while any(a == anchor for _, a, _ in toc):
                cnt += 1
                anchor = "%s-%d" % (base, cnt)
            out.append("<h%d id='%s'>%s</h%d>" % (level, anchor, _inline(txt), level))
            if level <= 3:
                toc.append((level, anchor, txt))
            i += 1
            continue

        # 分隔线
        if re.match(r"^(---|\*\*\*|___)\s*$", s):
            out.append("<hr>")
            i += 1
            continue

        # 引用
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % _inline(" ".join(buf)))
            continue

        # 表格
        if "|" in s and i + 1 < n and "-" in lines[i + 1] and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]):
            header = [c.strip() for c in s.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "<tr>" + "".join("<th>%s</th>" % _inline(h) for h in header) + "</tr>"
            tbody = "".join("<tr>" + "".join("<td>%s</td>" % _inline(c) for c in r) + "</tr>" for r in rows)
            out.append("<table class='md-table'><thead>%s</thead><tbody>%s</tbody></table>" % (thead, tbody))
            continue

        # 列表
        if _is_list_item(line):
            html, i = _parse_list(lines, i, _indent(line))
            out.append(html)
            continue

        # 段落
        buf = []
        while i < n and lines[i].strip() and not _is_block_start(lines[i], lines, i):
            buf.append(lines[i])
            i += 1
        para = " ".join(x.strip() for x in buf)
        out.append("<p>%s</p>" % _inline(para))

    body_html = "\n".join(out)

    # 标题来源：显式传入 > 第一个标题 > 文件名
    page_title = title
    if not page_title and toc:
        page_title = toc[0][2]
    if not page_title:
        page_title = "文档"

    # TOC
    toc_html = ""
    if toc:
        items = []
        for level, anchor, txt in toc:
            items.append("<li class='toc-l%d'><a href='#%s'>%s</a></li>" % (level, anchor, _inline(txt)))
        toc_html = "<nav class='toc'><div class='toc-title'>目录</div><ul>%s</ul></nav>" % "\n".join(items)

    source_tag = ("<span class='src-label'>%s</span>" % source_label) if source_label else ""

    return PAGE_TEMPLATE % {
        "title": _inline(page_title),
        "back": back_href,
        "source": source_tag,
        "toc": toc_html,
        "body": body_html,
    }


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<style>
:root{--li-blue:#0a66c2;--text:#1d2226;--sec:#5e5e5e;--border:#e8e8e8;--bg:#f3f2ef;--code-bg:#0d1117;--code-fg:#e6edf3;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.75;}
.topbar{position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid var(--border);}
.topbar-inner{max-width:860px;margin:0 auto;height:52px;display:flex;align-items:center;gap:12px;padding:0 18px;}
.back{color:var(--li-blue);font-weight:600;text-decoration:none;font-size:14px;}
.back:hover{text-decoration:underline;}
.src-label{margin-left:auto;font-size:12px;color:var(--sec);background:#eef3f8;padding:4px 10px;border-radius:999px;}
.wrap{max-width:860px;margin:24px auto;padding:0 18px 60px;}
.doc-title{font-size:30px;line-height:1.3;margin:8px 0 18px;font-weight:800;}
.toc{background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:0 0 26px;}
.toc-title{font-size:13px;font-weight:700;color:var(--sec);margin-bottom:8px;letter-spacing:.05em;}
.toc ul{list-style:none;margin:0;padding:0;}
.toc li{margin:4px 0;}
.toc li a{color:var(--li-blue);text-decoration:none;font-size:14px;}
.toc li a:hover{text-decoration:underline;}
.toc .toc-l2{padding-left:14px;}
.toc .toc-l3{padding-left:28px;font-size:13px;}
.content{background:#fff;border:1px solid var(--border);border-radius:12px;padding:26px 30px;}
.content h1,.content h2,.content h3,.content h4,.content h5,.content h6{line-height:1.4;margin:1.4em 0 .6em;font-weight:700;}
.content h1{font-size:24px;border-bottom:2px solid var(--border);padding-bottom:.3em;}
.content h2{font-size:20px;border-bottom:1px solid var(--border);padding-bottom:.25em;}
.content h3{font-size:17px;}
.content p{margin:.8em 0;}
.content a{color:var(--li-blue);text-decoration:none;}
.content a:hover{text-decoration:underline;}
.content ul,.content ol{margin:.7em 0;padding-left:1.6em;}
.content li{margin:.3em 0;}
.content blockquote{margin:1em 0;padding:.6em 1em;border-left:4px solid var(--li-blue);background:#f0f6fc;color:#33475b;border-radius:0 8px 8px 0;}
.content hr{border:none;border-top:1px solid var(--border);margin:1.8em 0;}
.content img{max-width:100%%;border-radius:8px;margin:.6em 0;}
.content code{background:#eef1f4;color:#b5245a;padding:.15em .4em;border-radius:4px;font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;font-size:.9em;}
.content pre.code{background:var(--code-bg);color:var(--code-fg);padding:16px 18px;border-radius:10px;overflow:auto;margin:1em 0;line-height:1.6;}
.content pre.code code{background:none;color:inherit;padding:0;}
.content table.md-table{border-collapse:collapse;width:100%%;margin:1em 0;font-size:14px;}
.content table.md-table th,.content table.md-table td{border:1px solid var(--border);padding:8px 12px;text-align:left;}
.content table.md-table th{background:#f3f6f9;font-weight:700;}
.content table.md-table tr:nth-child(even) td{background:#fafbfc;}
.foot{text-align:center;color:var(--sec);font-size:12px;margin-top:30px;}
@media(max-width:600px){.content{padding:18px 16px;}.doc-title{font-size:24px;}}
</style>
</head>
<body>
<div class="topbar"><div class="topbar-inner">
  <a class="back" href="%(back)s">← 返回知识库</a>
  %(source)s
</div></div>
<div class="wrap">
  <h1 class="doc-title">%(title)s</h1>
  %(toc)s
  <div class="content">
%(body)s
  </div>
  <div class="foot">本页由 Markdown 自动转换生成 · 点击左上角返回知识库索引</div>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------
# 命令行入口
# --------------------------------------------------------------------------
def main(argv):
    if len(argv) < 2:
        print("用法: python md2html.py input.md [output.html] [- title=标题]")
        return 1
    inp = argv[1]
    outp = argv[2] if len(argv) > 2 and not argv[2].startswith("-") else os.path.splitext(inp)[0] + ".html"
    title = None
    for a in argv[2:]:
        if a.startswith("title="):
            title = a[len("title="):]
    with open(inp, "r", encoding="utf-8", errors="ignore") as f:
        md = f.read()
    html = convert(md, title=title)
    with open(outp, "w", encoding="utf-8") as f:
        f.write(html)
    print("已转换: %s -> %s (%d 字节)" % (inp, outp, len(html)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
