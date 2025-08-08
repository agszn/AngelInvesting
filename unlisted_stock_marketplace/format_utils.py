# unlisted_stock_marketplace/format_utils.py
#style the overview text
import re

def render_custom_format(text):
    if not text:
        return ''

    lines = text.split('\n')
    html_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        stripped = line.strip()

        # Handle headings and list markers
        if stripped.startswith('## '):
            html_lines.append(f'<h2 style="font-size: 24px; margin-top: 24px;">{stripped[3:]}</h2>')
        elif stripped.startswith('### '):
            html_lines.append(f'<h3 style="font-size: 20px; margin-top: 16px;">{stripped[4:]}</h3>')
        elif stripped == '>>':
            html_lines.append('<ul style="list-style: disc; padding-left: 20px;">')
            in_ul = True
        elif stripped == '<<':
            html_lines.append('</ul>')
            in_ul = False
        elif stripped == '//':
            html_lines.append('<ol style="padding-left: 20px;">')
            in_ol = True
        elif stripped == '\\\\':
            html_lines.append('</ol>')
            in_ol = False
        elif stripped.startswith('||') and stripped.endswith('||'):
            content = stripped.strip('|')
            html_lines.append(f'<li style="margin-bottom: 6px;">{content}</li>')
        elif stripped:
            # Inline formatting — escape only here
            line = (
                stripped.replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
            )
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong style="font-weight: 600;">\1</strong>', line)
            line = re.sub(r'!!(.+?)!!', r'<em style="font-style: italic;">\1</em>', line)
            line = re.sub(r'~~(.+?)~~', r'<span style="text-decoration: underline;">\1</span>', line)
            html_lines.append(f'<p style="font-size: 16px; margin-bottom: 10px;">{line}</p>')

    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')

    return '\n'.join(html_lines)
