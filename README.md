# gpt_math_markdown_convert

A small CLI tool that normalizes math-like content in Markdown and reduces KaTeX parse errors.

## Features
- Convert standalone `[ ... ]` math blocks into `$$ ... $$`
- Convert selected inline `( ... )` expressions into `$ ... $`
- Keep existing `$...$` / `$$...$$` regions untouched
- Support single-file and multi-file conversion
- Support drag-and-drop usage after packaging as `.exe`

## Quick start

### Run with Python
```powershell
python tr.py input.md
python tr.py input.md -o output.md
python tr.py a.md b.md c.md
```

If no input argument is provided, the tool asks for filenames interactively.

### Build EXE
Install dependency:
```powershell
python -m pip install pyinstaller
```

Build:
```powershell
python -m PyInstaller --onefile tr.py
```

Output path:
- `dist\tr.exe`

### Drag-and-drop
After building, drag one or multiple `.md` files onto `tr.exe`.
You can also drag files onto `convert_drag.bat` (it uses `dist\\tr.exe` first, then falls back to `python tr.py`).

## Project structure
- `tr.py`: CLI and converter logic
- `scripts/build_exe.ps1`: build helper script
- `convert_drag.bat`: drag-and-drop launcher for Windows
- `dist/`: packaged executable output (optional)

## Notes
- Input files are read as UTF-8.
- Default output is `<input_stem>_converted.md` in the same folder.
- Use `-o/--output` only when converting a single file.
