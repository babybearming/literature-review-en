# Google Scholar (gs-skills) 操作参考

本文件为 Codex Agent 提供 Google Scholar 搜索的完整操作指南。
所有 GS 操作依赖 Chrome DevTools MCP 工具 (`mcp__chrome-devtools`)。

## 前置条件

- Chrome 浏览器已安装并运行
- Codex Chrome Extension 已安装并启用
- `mcp__chrome-devtools` MCP 可用

## 1. 基础搜索 (gs-search)

**导航到搜索页**：
```
mcp__chrome-devtools__navigate_page
url: https://scholar.google.com/scholar?q={URL_ENCODED_KEYWORDS}&hl=en&num=10
```

**提取结果** (evaluate_script)：
```javascript
async () => {
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('#gs_res_ccl') || document.querySelector('#gs_captcha_ccl')) break;
    await new Promise(r => setTimeout(r, 500));
  }
  if (document.querySelector('#gs_captcha_ccl') || document.body.innerText.includes('unusual traffic')) {
    return { error: 'captcha', message: 'CAPTCHA required.' };
  }
  const items = document.querySelectorAll('#gs_res_ccl .gs_r.gs_or.gs_scl');
  const results = Array.from(items).map((item, i) => {
    const titleEl = item.querySelector('.gs_rt a');
    const meta = item.querySelector('.gs_a')?.textContent || '';
    const parts = meta.split(' - ');
    return {
      n: i + 1,
      title: titleEl?.textContent?.trim() || '',
      href: titleEl?.href || '',
      authors: parts[0]?.trim() || '',
      journalYear: parts[1]?.trim() || '',
      citedBy: item.querySelector('.gs_fl a[href*="cites"]')?.textContent?.match(/\d+/)?.[0] || '0',
      dataCid: item.getAttribute('data-cid') || '',
      fullTextUrl: (item.querySelector('.gs_ggs a') || item.querySelector('.gs_or_ggsm a'))?.href || '',
      snippet: item.querySelector('.gs_rs')?.textContent?.trim()?.substring(0, 300) || ''
    };
  });
  const totalText = document.querySelector('#gs_ab_md')?.textContent?.trim() || '';
  return { total: totalText, resultCount: results.length, currentUrl: window.location.href, results };
}
```

**返回字段说明**：
- `title`: 论文标题
- `authors`: "Author1, Author2" 格式
- `journalYear`: "Journal, Year" 格式
- `citedBy`: 被引用数
- `dataCid`: GS cluster ID（后续操作的关键标识）
- `fullTextUrl`: 直接 PDF/HTML 链接
- `snippet`: 搜索结果摘要片段（200-300字符）

## 2. 高级搜索 (gs-advanced-search)

通过 URL 参数精确过滤：

| 参数 | 含义 | 示例 |
|------|------|------|
| `q` | 关键词 | `q=urban+climate+risk` |
| `as_sauthors` | 作者 | `as_sauthors=Smith` |
| `as_publication` | 期刊 | `as_publication=Nature` |
| `as_ylo` | 起始年份 | `as_ylo=2018` |
| `as_yhi` | 截止年份 | `as_yhi=2025` |
| `as_epq` | 精确短语 | `as_epq=climate+resilience` |
| `as_occt` | 搜索范围 | `as_occt=title` (仅标题) |
| `num` | 每页结果数 | `num=10` (默认) 或 `num=20` |

URL 示例：
```
https://scholar.google.com/scholar?q=urban+climate+risk&as_ylo=2018&as_occt=title&hl=en&num=10
```

提取脚本同基础搜索。

## 3. 翻页 (gs-navigate-pages)

GS 使用 `start` 参数分页（0-indexed，步长 10）：
- 第 2 页: `&start=10`
- 第 3 页: `&start=20`

修改当前 URL 的 `start` 参数后导航，提取脚本同上。

## 4. CAPTCHA 处理

如果返回 `{error: 'captcha'}`：
1. 告知用户需要完成 CAPTCHA 验证
2. 等待用户确认
3. 重试 evaluate_script 提取

## 5. 关键注意事项

- GS 无公共 API，全部通过 DOM 抓取
- 请求间隔至少 2 秒，避免触发 CAPTCHA
- `num=10`（默认）最小化 CAPTCHA 风险
- `dataCid` 是 GS 的核心标识符
- 每次搜索 = 2 个工具调用（navigate_page + evaluate_script）
- 搜索结果中的 snippet 可作为论文摘要的替代来源