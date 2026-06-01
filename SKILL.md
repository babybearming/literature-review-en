---
name: literature-review-en
description: >
  搜索英文学术论文并生成高保真 HTML 文献综述报告。完整的端到端工作流：
  (1) 将用户的研究主题拆解为多组英文搜索关键词，
  (2) 优先通过 Google Scholar (gs-skills) 获取英文论文数据（标题、作者、年份、摘要、引用数、dataCid），
  (3) 如果 Chrome DevTools MCP 不可用，自动降级到 OpenAlex 学术 API，
  (4) 为每篇英文论文撰写中文标题翻译、核心创新点总结、研究动机分析，
  (5) 生成 APA 参考文献格式和正文引用格式，
  (6) 输出自包含的交互式 HTML 报告（支持分类筛选、搜索、排序、打印）。
  当用户需要：搜索英文学术论文、撰写英文文献综述、生成英文论文参考手册、
  做英文文献调研、获取英文论文引用格式、以 HTML 形式呈现英文论文集合时使用。
  触发词：英文文献综述、英文论文搜索、英文文献调研、English literature review。
  注意：本 skill 侧重英文文献。如需中文文献请使用 literature-review-cn。
---

# 英文文献综述 HTML 生成器 (Literature Review EN)

端到端的英文学术论文搜索与 HTML 报告生成工作流。支持 Google Scholar（首选）和 OpenAlex（降级）双通道数据采集。本 skill 侧重英文文献，如需中文文献请使用 literature-review-cn。

## 输入

用户提供一个**研究主题**（如"城市气候风险"、"大语言模型安全"等），以及可选的：
- 论文数量（默认 35）
- 年份范围（默认 2014–至今）
- 输出路径

## 工作流程

### Step 0: 检测搜索通道

检查 `mcp__chrome-devtools` MCP 工具是否可用：
- **可用** → 走 Google Scholar 通道（Step 2A）
- **不可用** → 走 OpenAlex 通道（Step 2B）

### Step 1: 拆解关键词

将研究主题拆解为 5–10 组学术搜索关键词，覆盖不同维度。示例：

```
主题: "城市气候风险"
→ urban climate risk
→ urban climate vulnerability
→ urban heat island risk
→ urban flooding climate change
→ urban climate resilience
→ climate change urban adaptation
→ urban climate risk assessment
→ urban heat vulnerability
```

向用户展示拆解结果，确认后继续。

### Step 2A: Google Scholar 搜索（首选）

**前置条件**：Chrome 浏览器运行中，Codex Chrome Extension 已安装，`mcp__chrome-devtools` 可用。

详细操作步骤见 `references/gs-skills-guide.md`。

#### 搜索流程

对每组关键词，依次执行：

1. **导航到 GS 搜索页**
   ```
   mcp__chrome-devtools__navigate_page
   url: https://scholar.google.com/scholar?q={URL_ENCODED_KW}&hl=en&num=10&as_ylo=2014
   ```

2. **提取搜索结果** (evaluate_script) — 使用 `references/gs-skills-guide.md` 中的 JS 脚本

3. **翻页获取更多结果**（可选，如需 >10 条）
   修改 URL 添加 `&start=10` 获取第 2 页

4. **CAPTCHA 处理**
   如果返回 `{error: 'captcha'}`：
   - 告知用户需要完成 CAPTCHA 验证
   - 等待用户确认后重试

5. **将结果标准化**
   每组关键词搜索完成后，将 scrape 结果保存为临时 JSON，然后用脚本标准化：
   ```bash
   python scripts/normalize_gs.py --input gs_result.json --output papers_raw.json --category "气候风险"
   ```

6. **合并多组结果**
   `normalize_gs.py` 会自动去重合并到同一个输出文件。

**重要**：每组搜索之间等待 2–3 秒，避免触发 CAPTCHA。

#### GS 结果字段映射

| GS 字段 | 标准字段 | 说明 |
|---------|---------|------|
| `title` | `title_en` | 英文标题 |
| `authors` | `authors` | 解析为标准格式 |
| `journalYear` | `venue` + `year` | 拆分期刊和年份 |
| `citedBy` | `cited_by` | 被引用数 |
| `snippet` | `abstract` | 搜索摘要（200-300字符） |
| `href` | `doi` | 可能包含 DOI 链接 |
| `dataCid` | `data_cid` | GS cluster ID |
| `fullTextUrl` | `full_text_url` | 直接 PDF 链接 |

### Step 2B: OpenAlex 搜索（降级方案）

当 Chrome DevTools MCP 不可用时使用。

```bash
python scripts/fetch_papers.py \
  --keywords "气候风险:urban climate risk" "气候脆弱性:urban climate vulnerability" \
  --top 35 --year-from 2014 --output papers_raw.json
```

参数说明：
- `--keywords`: 格式 `标签:搜索词`，至少 3 组
- `--top`: 选取 Top N 论文（按引用数）
- `--output`: 输出 JSON 路径

### Step 3: 撰写中文翻译与总结

**这是核心增值步骤** — 为每篇论文撰写：

1. **中文标题** (`title_cn`) — 学术规范的中文翻译
2. **核心问题与创新点** (`summary`) — 一句话总结文章要解决的问题和创新点
3. **研究动机** (`motivation`) — 作者为什么做这项研究

撰写原则：
- 基于论文标题和摘要/摘要片段（`abstract` 字段）推理
- summary 控制在 40–60 字，motivation 控制在 50–80 字
- 语言精练、学术化，避免空泛
- 如果 abstract 为空（GS 的 snippet 较短），基于标题推理

将 `title_cn`、`summary`、`motivation` 三个字段合并写入 JSON。
**必须保存为 `.py` 文件再执行**（避免 PowerShell 管道中文编码问题）：

```python
import json
with open("papers_raw.json", "r", encoding="utf-8") as f:
    papers = json.load(f)

paper_meta = [
    ("中文标题1", "一句话总结1", "研究动机1"),
    ("中文标题2", "一句话总结2", "研究动机2"),
    ...
]

for i, p in enumerate(papers):
    cn_title, summary, motivation = paper_meta[i]
    p["title_cn"] = cn_title
    p["summary"] = summary
    p["motivation"] = motivation

with open("papers_enriched.json", "w", encoding="utf-8") as f:
    json.dump(papers, f, ensure_ascii=False, indent=2)
```

**编码警告**：必须将 Python 脚本保存为 UTF-8 `.py` 文件再执行，禁止通过 PowerShell 管道输入（中文会被 GBK 截断为 `?`）。

### Step 4: 生成 HTML 报告

```bash
python scripts/generate_html.py \
  --input papers_enriched.json \
  --output report.html \
  --title "城市气候风险文献综述" \
  --subtitle "涵盖风险评估、脆弱性分析、热岛效应等方向 · 35 篇高引论文"
```

生成自包含 HTML 文件（无外部依赖），内嵌所有数据和交互逻辑。

### Step 5: 打开验证

用浏览器打开 HTML 文件，确认中文显示正常。

## HTML 报告功能

每篇论文卡片包含：
1. **中文标题** — 学术语体翻译
2. **英文原标题** — 斜体
3. **核心问题与创新点** — 一句话总结
4. **APA 参考文献格式** — 可直接复制
5. **研究动机** — 为什么做这项研究
6. **正文引用格式** — `(Author et al., Year)` 可直接嵌入综述

交互功能：分类筛选、关键词搜索、三种排序、打印优化。

## 文件结构

```
literature-review-html/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── fetch_papers.py               # OpenAlex API 采集脚本
│   ├── normalize_gs.py               # GS 数据标准化脚本
│   └── generate_html.py              # HTML 报告生成器
├── references/
│   └── gs-skills-guide.md            # Google Scholar 操作参考
└── assets/                           # 预留模板/资源目录
```

## 关键注意事项

- **编码**：Python 脚本中的中文字符必须保存为 `.py` 文件（UTF-8）再执行，不可通过管道输入
- **GS vs OpenAlex**：GS 优先（数据更准、引用数更实时），OpenAlex 作为可靠降级方案
- **CAPTCHA**：GS 搜索频率过高会触发验证码，每组搜索间隔 2–3 秒
- **去重**：`normalize_gs.py` 和 `fetch_papers.py` 都内置按标题去重逻辑
- **摘要**：GS 的 snippet 较短（200字符），OpenAlex 可返回完整摘要
- **dataCid**：GS 搜索结果中的 cluster ID，可用于后续引用追踪(gs-cited-by)和导出(gs-export)