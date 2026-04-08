# GRE 背单词 App

打开 [index.html](/Users/ouzhang/Desktop/gre/index.html) 就能直接用。

现在已经内置了 [words_bank_raw/GRE_3000_Vocabularies/3000.xlsx](/Users/ouzhang/Desktop/gre/words_bank_raw/GRE_3000_Vocabularies/3000.xlsx) 解析出的 `GRE 3000` 词库，首次打开后可以在空状态页或“批量添加词表”弹层里一键导入。

现在也支持安装成 PWA。用 `localhost` 打开后，Chrome / Edge / Safari 都可以添加到桌面或主屏幕，作为一个独立 app 使用。

如果你想让“导出音频”功能更稳定，建议用本地静态服务器打开：

```bash
cd /Users/ouzhang/Desktop/gre
python3 -m http.server 4173
```

然后访问 `http://localhost:4173/index.html`。

说明：

- 单词数据保存在浏览器 `localStorage`
- 熟词会被降为低频词，并在后续轮次按低频重新出现
- 现在支持 `不熟悉 / 熟悉 / 太熟了` 三档调频：
  - `不熟悉`：本轮会再出现一次，之后保持每轮出现
  - `熟悉`：隔轮出现
  - `太熟了`：低频召回，约每 4 轮回来一次
- 现在支持把 `xlsx / xlsm / csv / txt` 直接拖进页面，自动识别词表并导入
- 导入时可以选择：
  - 新建一个词库
  - 继续扩充现有词库
  - 合并多个词库生成一个新词库
  - 按固定数量拆分一个词库
- 可以只学习某个词库，或者暂停某个词库，学习队列会跟着切换
- 内置词库数据文件是 [data/gre3000-bank.js](/Users/ouzhang/Desktop/gre/data/gre3000-bank.js)
- 如果原始 Excel 更新了，可以执行 `python3 scripts/build_word_bank.py` 重新生成内置词库
- [words_bank_raw](/Users/ouzhang/Desktop/gre/words_bank_raw) 已加入 [.gitignore](/Users/ouzhang/Desktop/gre/.gitignore)，运行时不依赖它；如果你还要重新生成词库，保留本地原始 Excel 即可
- “导出音频”依赖浏览器的标签页录音能力，成功时会下载 `webm`
- 浏览器不支持录音时，会自动降级为导出今日朗读脚本
