# 双端发布指南

本仓库是 DSH 插件目录的**单一事实源**：数据机器人每日更新 `catalog/plugins.json`，由此构建出两种发布产物。

## 数据自动更新（GitHub Actions）

- `.github/workflows/sync.yml`：每天北京时间 09:17（cron `17 1 * * *` UTC）自动运行
  1. `npm run sync`：搜索 GitHub 上 `topic:dsh-plugin` 的仓库，逐仓库校验补丁文件真伪，重写 `catalog/plugins.json`
  2. `npm run check`：校验目录完整性
  3. 有变化才自动 commit（diff 检查），无变化不产生提交
- 也可在 Actions 页面手动触发（workflow_dispatch）

## 产物一：DeepSeek Whale 静态站（WorkBuddy 平台发布）

```bash
python scripts/gen_site.py --out <输出目录> [--site https://你的域名/]
```

- 读取 `catalog/plugins.json`，生成完全自包含的静态站：
  `index.html`（中文）+ `en.html`（英文）+ `robots.txt` + `sitemap.xml` + `feed.xml` + `manifest.webmanifest` + `favicon.svg` + `llms.txt`（带 BOM）
- 特性：JSON-LD 结构化数据（WebSite + ItemList + FAQPage）、hreflang 双语声明、深浅双主题、卡片/横条视图切换、URL 同步筛选状态、`/` 快捷键、复制降级
- 当前发布到 WorkBuddy 平台：`dsh-plugins.app.workbuddy.host`（appId `wbapp_NVdbf9G7GWE1BB58rJAgJv`），由 WorkBuddy 每日定时任务自动：拉取本仓库 raw 数据 → 生成 → 重发

## 产物二：Cloudflare Workers 版（可选）

```bash
npm install          # 装 wrangler
npm run build        # 构建 dist/（原版前端：双语首页 + 705 详情页 + about/privacy）
npm run deploy       # wrangler deploy（需要 Cloudflare 账号与 wrangler login）
```

- `SITE_URL=https://你的域名 npm run build` 可参数化站点域名
- `src/worker.js`：`/api/plugins` 代理本仓库 raw 的 `catalog/plugins.json`（15 分钟边缘缓存 + 失败回退部署内副本）
- `wrangler.jsonc` 需要把 routes 里的自定义域名改成你自己的
- 也可接 GitHub Actions 自动部署：`cloudflare/wrangler-action`，需在仓库 Secrets 配置 `CLOUDFLARE_API_TOKEN`

## 其他命令

```bash
npm run check   # 校验 catalog 完整性
npm run test    # 构建 + 跑 SEO/数据测试
npm run list    # 列出目录内插件
```

## 数据来源与许可

- 数据管道与前端工程改造自 [lwmxiaobei/dsh-plugins](https://github.com/lwmxiaobei/dsh-plugins)（MIT License，见 LICENSE）
- 插件元数据来自各插件上游公开 GitHub 仓库
