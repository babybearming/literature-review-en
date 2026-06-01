# Literature Review EN — 英文文献综述 HTML 生成器

[English](#english) | 中文

端到端的英文学术论文搜索与 HTML 报告生成工作流。支持 **Google Scholar**（首选）和 **OpenAlex**（降级）双通道数据采集，输出带交互功能的精美 HTML 文献综述报告。

---

## 功能特性

- 🔍 **双通道数据采集**：Google Scholar 优先，OpenAlex 自动降级
- 🧠 **智能关键词拆解**：将研究主题拆解为 5-10 组学术搜索关键词
- 📝 **中英双语分析**：中文标题翻译 + 核心创新点总结 + 研究动机分析
- 📚 **APA 引用格式**：自动生成 APA 参考文献格式和正文引用
- 🎨 **交互式 HTML 报告**：支持分类筛选、搜索、排序、打印
- 📊 **引用数统计**：获取论文被引次数，按影响力排序

## 数据源

| 通道 | 条件 | 优势 |
|------|------|------|
| Google Scholar | Chrome DevTools MCP 可用 | 数据更全、引用数准确 |
| OpenAlex | 降级方案，无需浏览器 | 免费 API、无需认证 |

## 文件结构

```
literature-review-en/
├── SKILL.md                          # Skill 主文件（工作流定义）
├── references/
│   └── gs-skills-guide.md            # Google Scholar 操作指南
└── scripts/
    ├── fetch_papers.py               # 论文数据抓取脚本
    ├── generate_html.py              # HTML 报告生成脚本
    └── normalize_gs.py               # Google Scholar 结果标准化
```

## 使用方法

在 Codex 中提供研究主题即可触发：

> 英文文献综述、英文论文搜索、英文文献调研、English literature review

### 示例

```
请帮我搜索关于 "urban climate risk" 的英文文献综述
```

### 可选参数

- **论文数量**：默认 35 篇
- **年份范围**：默认 2014–至今
- **输出路径**：自定义 HTML 保存位置

## 工作流程

```
用户输入研究主题
       ↓
拆解为 5-10 组关键词
       ↓
  ┌────┴────┐
  │ 检测通道 │
  └────┬────┘
       ↓
 Google Scholar / OpenAlex 搜索
       ↓
  收集论文元数据（标题、作者、摘要、引用数）
       ↓
  中文分析（翻译、创新点、动机）
       ↓
  生成 APA 引用格式
       ↓
  输出交互式 HTML 报告
```

## 注意事项

- 本 skill 侧重**英文文献**，如需中文文献请使用 `literature-review-cn`
- Google Scholar 通道需要 Codex Chrome Extension 配合使用

---

## English

End-to-end English literature search and HTML report generation. Supports Google Scholar (preferred) and OpenAlex (fallback) dual-channel data collection.

- Smart keyword decomposition from research topics
- Chinese title translation + innovation summary for each paper
- APA reference format generation
- Interactive HTML with filtering, search, sorting, and print support
- Trigger words: `English literature review`, `literature survey`
