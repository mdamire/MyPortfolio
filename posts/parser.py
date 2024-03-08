import re


class PostSubLink():

    def __init__(self, div_id, text, indent=0) -> None:
        self.div_id = div_id
        self.text = text
        self.indent = indent


def parse_sublinks(text) -> tuple[str, list[PostSubLink]]:
    h_re = re.compile(r'<h([\d]) ?.*?>(.*?)</h\1>')
    start_pos = 0
    updated_text = ''
    sublink_list = []
    indent = 0
    cur_level = None

    for cnt, match in enumerate(h_re.finditer(text), start=1):
        div_id = f'sub_heading_{cnt}'
        updated_text += text[start_pos:match.end(1)] + f' id={div_id}' + text[match.end(1):match.end()]

        try:
            if cur_level is not None and int(match.group(1)) > cur_level:
                indent += 1
            elif cur_level is not None and int(match.group(1)) < cur_level and indent > 0:
                indent -= 1
            cur_level = int(match.group(1))
        except Exception:
            pass

        sublink_list.append(PostSubLink(div_id, match.group(2), indent))
        start_pos = match.end()
    
    updated_text += text[start_pos:]
    return updated_text, sublink_list
