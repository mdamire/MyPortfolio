import re


SUBLINK_DIV = '<div id="{}" class="post-sublink"></div>'


class PostSubLink():

    def __init__(self, div_id, text, indent=0) -> None:
        self.div_id = div_id
        self.text = text
        self.indent = indent
        self.indent_range = list(range(indent))


def parse_sublinks(text) -> tuple[str, list[PostSubLink]]:
    h_re = re.compile(r'<h([\d]) ?.*?>(.*?)</h\1>')
    start_pos = 0
    updated_text = ''
    sublink_list = []
    indent = 0
    last_level = None

    for cnt, match in enumerate(h_re.finditer(text), start=1):
        div_id = f'sub_heading_{cnt}'
        updated_text += text[start_pos:match.start()] + SUBLINK_DIV.format(div_id) + text[match.start():match.end()]

        try:
            if last_level is not None and int(match.group(1)) > last_level:
                indent += 1
            elif last_level is not None and int(match.group(1)) < last_level and indent > 0:
                indent -= last_level - int(match.group(1))
                if indent < 0:
                    indent = 0
            
            last_level = int(match.group(1))
        except Exception:
            pass

        sublink_list.append(PostSubLink(div_id, match.group(2), indent))
        start_pos = match.end()
    
    updated_text += text[start_pos:]
    return updated_text, sublink_list
