# gpt_math_markdown_convert

[English README](./README.md)

一个面向 **KaTeX / LaTeX 公式报错修复** 的 Markdown 清洗工具。
主要用于 OCR、AI 生成、复制粘贴后出现公式混乱的笔记场景。

关键词：`Markdown 数学公式`、`KaTeX 报错`、`LaTeX 清洗`、`Obsidian 公式`、`Typora 数学渲染`

## 这个项目解决什么问题
常见报错包括：
- `Can't use function '$' in math mode`
- 公式被错误改写成 `V$f$`、`f$P$` 之类

本工具会把常见的“类数学片段”规范化，减少 KaTeX 解析错误。

## Before vs After（转换前后对比）

### 案例 1：显示公式内的行内公式被破坏

Before:
![alt text](image.png)

After:
![alt text](image-1.png)


```

### 案例 2：理想记号被破坏

转换前：
```markdown
$$
I(S)=$x, y$
$$
```

转换后：
```markdown
$$
I(S)=(x, y)
$$
```

### 案例 3：方括号公式块转标准数学块

转换前：
```markdown
[
k[x_1,\dots,x_n]
]
```

转换后：
```markdown
$$
k[x_1, \dots, x_n]
$$
```

## 功能
- 将独立的 `[ ... ]` 数学块转为 `$$ ... $$`
- 将部分行内 `( ... )` 转为 `$...$`
- 不改动已有 `$...$` / `$$...$$` 数学区域
- 降低误转换，避免二次引入 KaTeX 错误
- 支持单文件、多文件、Windows 拖拽处理

## 快速开始

### Python 运行
```powershell
python tr.py input.md
python tr.py input.md -o output.md
python tr.py a.md b.md c.md
```

如果不传输入参数，会进入交互输入文件名模式。

### 打包 EXE（Windows）
```powershell
python -m pip install pyinstaller
python -m PyInstaller --onefile tr.py
```

产物路径：
- `dist\\tr.exe`

### 拖拽使用
- 把一个或多个 `.md` 拖到 `dist\\tr.exe`
- 或拖到 `convert_drag.bat`（优先调用 EXE，不存在则回退到 Python）

## 项目结构
- `tr.py`：转换逻辑和命令行入口
- `scripts/build_exe.ps1`：PowerShell 打包脚本
- `convert_drag.bat`：Windows 拖拽启动器
- `dist/`：可执行文件输出目录

## 说明
- 输入编码：UTF-8
- 默认输出：`<输入文件名>_converted.md`（同目录）
- `-o/--output` 仅支持单文件输入

## 许可证
MIT（见 `LICENSE`）
