import re

from forum.markups import postmarkup

RE_FIRST_LF = re.compile('^\s*\r?\n')
markup = postmarkup.create(exclude=['link', 'url', 'code'], use_pygments=False)

class LinkTagNoAnnotate(postmarkup.LinkTag):
    def annotate_link(self, domain):        
        return ''


class CodeTagNoBreak(postmarkup.CodeTag):
    def render_open(self, parser, node_index):

        contents = self._escape(self.get_contents(parser))
        contents = RE_FIRST_LF.sub('', contents)
        self.skip_contents(parser)
        return '<pre><code>%s</code></pre>' % contents

    def _escape(self, s):
        return postmarkup.PostMarkup.standard_replace_no_break(s.rstrip('\n'))


markup.tag_factory.add_tag(LinkTagNoAnnotate, 'url')
markup.tag_factory.add_tag(CodeTagNoBreak, 'code')

