# GitHub Pages 发布

这个目录已经是可直接发布的静态站点。

## 打开方式

1. 把整个仓库推到 GitHub。
2. 进入仓库 `Settings -> Pages`。
3. `Source` 选择 `Deploy from a branch`。
4. Branch 选择 `main`，Folder 选择 `/docs`。
5. 保存后等待 GitHub Pages 完成部署。

## 站点内容

- 首页宣传站：`/docs/index.html`
- 在线体验版：`/docs/app/index.html`
- Mac 下载包：`/docs/downloads/*.dmg`
- 主题封面：`/docs/assets/themes`
- 主题试听：`/docs/assets/audio`

## 重新生成

```bash
python3 scripts/build_marketing_site.py
```
