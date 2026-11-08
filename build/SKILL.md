---
name: vocab-story
description: 把一份英文单词表（截图/笔记/文本/链接）打乱重排成一段连贯英文故事，产出单文件交互网页：全文每个单词点击浮出中文、重点词逐词对照、每段中文全文译文、乱序词卡复背。触发词：单词表、词表、背单词、词汇、把这几个词串成一段话、打乱单词、点击显示中文、单词成文、vocabulary story。
version: "1.1.0"
author: "CodeBuddy AI"
created: "2026-11-08"
updated: "2026-11-08"
---

# Vocab Story · 单词打乱成文

把用户给的英文词表变成一篇**能读的故事**，再加一层**点击即查**的交互。用户是中文母语学习者，成品默认中英双语。

## 触发场景

- 「把这些单词打乱，组成一段话」「点击单词显示中文」
- 丢来一张手写/截图词表、iCloud/备忘录链接、Excel、粘贴的一串词
- 「照上次那个单词网页再做一份」

## 默认成品定义（用户先后确认过的偏好，勿擅自删减）

一个 `*.html` 单文件，包含五件事：

1. **故事正文**：词表里的词全部用上，顺序彻底打乱，重排成一篇有情节的英文短文（默认 7 段，800–1000 词）。
2. **全文可点（v1.1 追加的硬要求）**：正文**每一个单词**都能点，包括 the / was / and / of 这类虚词。点击浮出深色卡片：单词 + 词性 + 中文释义；若是词表重点词，再额外显示「重点词」徽章、英文释义，词形变化时显示「原形」。
3. **重点词标记**：103 个词表词带虚线（按词性配色）+ 计进进度；普通词无下划线、hover 才浮底色。绝对不能做成满页虚线。
4. **逐词对照**：`对照` 开关——**只给重点词**在词后加小号红色中文（709 个词全标会糊成一片，已试过，不可取）。
5. **全文译文**：`译文` 开关——每段英文下方展开中文翻译（浅红竖线，14.5px，行高 2.0）。默认收起但不许缺。

外加：右上角「已查看 x/N」+ 进度条、`重置`、第二 tab「乱序词卡」（重点词卡片随机排列，点击翻中文，`重新打乱` 重排）。

## 流程

### 1. 拿到词表

| 来源 | 做法 |
|---|---|
| 图片/截图 | PIL 纵向切 8 段，`resize(宽×5, LANCZOS)`，逐段 `ViewImage` 誊写；手写体易错，读完自查拼写 |
| iCloud / 备忘录链接 | `icloud.com.cn/notes/...` 需 Apple 登录，**WebFetch 必失败**，直接说明并改用用户附的截图 |
| 文本 / 表格 | 直接读；xlsx 走 sheetagent |

识别后去重（手写笔记常重复抄同一词）、按笔记上的中文注释核对释义、统计唯一词数 N。

### 2. 写故事

- **覆盖率 100%**：每个词至少出现一次；4–6 个词自然复现两次可以接受。
- **顺序打乱**：不保留原表顺序，不按字母/词性分组。
- **词形可变**：正文可写 compelled / wearing / peers，查词键仍是原形。
- 长尾词靠设定消化（democracy、opera、species → 小镇、旧歌剧院、本地传说），不要写成词表串烧。
- 7 段、每段 3–5 句，段段有推进。

### 3. 全词标注（关键步骤，别手工贴标签）

用脚本重建正文，而不是手写 700 个 `<w>`：

1. 先解析出 `const D`（重点词表）。
2. 把每段 `<p>` 里的已有目标词标签替换成占位符，再用
   `re.compile(r'\x00(\d+)\x00|([A-Za-z][A-Za-z\'\u2019\-]*)')` 切分，逐 token 输出：
   - 目标词 → `<w data-w="lower" data-k="key">原词形</w>`
   - 普通词 → `<w data-w="lower">word</w>`
3. 普通词词典 `W`（本次 267 条）单独维护：`word -> (中文, 词性)`，覆盖 the、was、been 这类高频虚词，以及 came / began / taken 等变形（中文里注明「begin 的过去式」）。
4. 生成后统计：`<w>` 总数（本次 709）、唯一词形（370）= 103 重点词 + 267 普通词；若正文出现词典里没有的词，脚本必须报错退出，不许留空。

> 交付前的自检：`document.querySelectorAll('#passage w')` 里 `没有 data-cn` 的数量必须为 0。

### 4. 校验（必做）

```bash
python3 ~/.codebuddy/skills/vocab-story/scripts/verify.py /workspace/xxx.html
```

输出必须 `dict == unique used == N`、`paragraphs == translations`、无 missing / unknown。再截图四态：默认、点击普通词、点击重点词、开译文/开对照（含 500px 窄屏）。

```bash
chromium --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --window-size=1280,1200 --screenshot=shot.png --virtual-time-budget=3000 file:///abs/path.html
```

验证点击态：复制临时 html，在 `</body>` 前插
`<script>setTimeout(()=>{document.querySelector('#passage w[data-w="ledger"]').click();},350);</script>`。

### 5. 交付

- 成品 `/workspace/<name>.html` + 全页预览 png；`present_files([html, png])`。
- 回复结构：故事梗概 → 功能表 → 需要用户确认的点（识别存疑词、是否要单段/双栏/默认展开译文）。

## 已知坑（全部踩过）

1. 自定义标签属性**必须带 `data-`**：`<w data-k="x">`；写 `<w k="x">` 会让 `dataset.k` 为 undefined。
2. `w::after` 用 `display:none → inline-block` 切换，**不要用 opacity/max-width transition 或 animation**：headless 截图里动画不推进，中文永远不显示。
3. tab 切换要显式 `display:block`，设成 `""` 会回落到样式表的 `display:none`，整块空白。
4. 按钮显隐用 `body.cardmode` + CSS，不要用 inline `visibility`（实测 computed 仍是 visible）。
5. 行内中文的 `margin-left` 只在对照态加，否则每个词后多出半个空格（`specify .` 就是这么来的）。
6. 对照态把 `#passage w` 设 `display:inline-block`，中文才跟着词走、不会单独掉到下一行；首段首个 `w` 要还原成 `inline`，否则 `::first-letter` 的下沉首字母失效。
7. 普通词点击**不能**计入进度：`markSeen()` 开头 `if(!k || !D[k]) return;`。
8. 打印样式只给 `w[data-k][data-cn]` 展开中文，否则 709 个词全印出来；同时 `display:block !important` 展开 `p.zh`、隐藏 `.tools`。
9. 校验脚本按属性顺序取 `data-k`，不要写死 `<w data-k="` 前缀（v1.1 起节点是 `data-w` 在前）。
10. headless Chromium 最小视口约 485px，窄屏验收用 500px；`--window-size=390` 会被放大。
11. 固定底栏会压正文，`.wrap` 的 `padding-bottom` 给到 230px。

## 输出风格

- 中文回复：先讲做了什么，再给功能表，最后列「需要你确认」的小问题。
- 页面里不写「AI 生成」字样；词表来源可在页脚用小字注明。
- 术语统一：词表里的词叫「重点词」，其余叫「普通词」。
