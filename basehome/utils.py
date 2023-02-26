import re

def get_sidebar_section_links(body_text):
    """This will find all the tags in a posts body that has id='section-*'.
    """

    regex = r'<.*?id="(section.*?)".*?>(.*?)<'
    sections = []
    for match in re.finditer(regex, body_text):
        sections.append(
            {
                'label': str(match[2]).title(),
                'url': '#' + str(match[1])
            }
        )
    
    sidebar_section = None
    if sections:
        sidebar_section = ('Links of this page', sections)
    
    return sidebar_section
