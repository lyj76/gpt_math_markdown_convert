import argparse
import re
import sys
from pathlib import Path


class MathMarkdownConverter:
    def __init__(self):
        # Common markers that likely indicate math-like content
        self.math_markers = [
            r'\\[a-zA-Z]+',         # LaTeX command, e.g. \cup \sqrt \in
            r'\^',                   # superscript
            r'_',                    # subscript
            r'=',                    # equality
            r'\\mid',
            r'\\to',
            r'\\in',
            r'\\cup',
            r'\\cap',
            r'\\subset',
            r'\\sqrt',
            r'\{', r'\}',
            r'[A-Za-z]+\([^\)]*\)',
        ]

        # Chinese explanatory phrases that are usually not pure inline math
        self.non_math_phrases = [
            "意义",
            "表示",
            "例如",
            "几何",
            "定义",
            "所以",
            "因为",
            "得到",
            "重要思想",
            "思考",
            "为什么",
            "不是",
            "所有",
            "代数几何",
        ]

    def looks_like_math(self, s: str) -> bool:
        s = s.strip()
        if not s:
            return False

        if len(s) > 80:
            return False

        chinese_chars = re.findall(r'[\u4e00-\u9fff]', s)
        if len(chinese_chars) >= 4:
            return False

        for phrase in self.non_math_phrases:
            if phrase in s:
                return False

        # Avoid converting plain words/identifiers like f, xy, why, etc.
        if re.fullmatch(r'[A-Za-z]+', s):
            return False

        # Avoid converting a bare LaTeX command token like \cdot in prose labels.
        if re.fullmatch(r'\\[A-Za-z]+', s):
            return False

        # Require at least one strong math signal to reduce false positives.
        if not re.search(r'(\\[A-Za-z]+|[\^_=+\-*/{}0-9])', s):
            return False

        for marker in self.math_markers:
            if re.search(marker, s):
                return True

        return False

    def normalize_math_text(self, s: str) -> str:
        s = s.strip()

        s = re.sub(r'[ \t]+', ' ', s)

        s = re.sub(r'\s*\\cup\s*', r' \\cup ', s)
        s = re.sub(r'\s*\\cap\s*', r' \\cap ', s)
        s = re.sub(r'\s*\\subset\s*', r' \\subset ', s)
        s = re.sub(r'\s*\\in\s*', r' \\in ', s)
        s = re.sub(r'\s*\\to\s*', r' \\to ', s)
        s = re.sub(r'\s*\\mid\s*', r' \\mid ', s)

        s = re.sub(r'\s*,\s*', ', ', s)
        s = re.sub(r'\s*;\s*', '; ', s)

        s = re.sub(r' {2,}', ' ', s)

        s = re.sub(r'\\sqrt\s+([A-Za-z0-9]+)', r'\\sqrt{\1}', s)

        return s.strip()

    def convert_display_brackets(self, text: str) -> str:
        """
        Convert a standalone block:
        [
        ...
        ]
        into:
        $$
        ...
        $$
        """
        pattern = re.compile(
            r'^[ \t]*\[\s*\n(.*?)\n[ \t]*\][ \t]*$',
            flags=re.MULTILINE | re.DOTALL
        )

        def repl(m):
            content = self.normalize_math_text(m.group(1))
            return f'$$\n{content}\n$$'

        return pattern.sub(repl, text)

    def convert_single_line_brackets(self, text: str) -> str:
        """
        Convert single-line standalone bracket expression:
        [ V(xy) ]
        into:
        $$V(xy)$$
        """
        pattern = re.compile(r'^[ \t]*\[\s*(.*?)\s*\][ \t]*$', flags=re.MULTILINE)

        def repl(m):
            content = m.group(1).strip()
            if '\n' in content:
                return m.group(0)
            content = self.normalize_math_text(content)
            return f'$${content}$$'

        return pattern.sub(repl, text)

    def convert_inline_parentheses(self, text: str) -> str:
        """
        Cautiously convert inline parentheses like (x^2), (k[x_1,\\dots,x_n]), (V(f))
        into $...$ only when content looks math-like.
        """
        pattern = re.compile(r'\(([^()\n]{1,80})\)')
        math_span_pattern = re.compile(r'(\$\$.*?\$\$|\$[^$\n]+\$)', flags=re.DOTALL)

        def replace_in_plain_segment(segment: str) -> str:
            def repl(m):
                inner = m.group(1).strip()
                full = m.group(0)
                if self.looks_like_math(inner):
                    inner = self.normalize_math_text(inner)
                    return f'${inner}$'
                return full

            return pattern.sub(repl, segment)

        parts = []
        last = 0
        for m in math_span_pattern.finditer(text):
            plain = text[last:m.start()]
            parts.append(replace_in_plain_segment(plain))
            parts.append(m.group(0))
            last = m.end()

        parts.append(replace_in_plain_segment(text[last:]))
        return ''.join(parts)

    def cleanup(self, text: str) -> str:
        text = re.sub(r'\$\$\s*\$\$', '$$\n$$', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'^\$\$(.+?)\$\$$', r'$$\n\1\n$$', text, flags=re.MULTILINE)
        return text.strip() + '\n'

    def convert(self, text: str) -> str:
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = self.convert_display_brackets(text)
        text = self.convert_single_line_brackets(text)
        text = self.convert_inline_parentheses(text)
        text = self.cleanup(text)
        return text


def convert_file(input_path: str, output_path: str = None):
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"找不到输入文件: {input_file}")

    if output_path is None:
        output_file = input_file.with_name(input_file.stem + "_converted.md")
    else:
        output_file = Path(output_path)

    text = input_file.read_text(encoding="utf-8")

    converter = MathMarkdownConverter()
    converted = converter.convert(text)

    output_file.write_text(converted, encoding="utf-8")
    print(f"转换完成: {output_file}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="将 Markdown 文本中的数学表达式规则化并输出为新文件。"
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="输入文件路径，可传多个。例如: python tr.py 0.md 1.md",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出文件路径。仅在单个输入文件时生效。",
    )
    return parser.parse_args()


def collect_inputs(args) -> list[str]:
    if args.inputs:
        return args.inputs

    raw = input("请输入要转换的文件名（可多个，空格分隔）: ").strip()
    if not raw:
        return []
    return raw.split()


def main() -> int:
    args = parse_args()
    inputs = collect_inputs(args)

    if not inputs:
        print("未提供输入文件。")
        return 1

    if args.output and len(inputs) > 1:
        print("错误: 传入多个输入文件时不能同时使用 -o/--output。")
        return 1

    has_error = False
    for input_path in inputs:
        try:
            output_path = args.output if len(inputs) == 1 else None
            convert_file(input_path, output_path)
        except Exception as exc:
            has_error = True
            print(f"处理失败 [{input_path}]: {exc}")

    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
