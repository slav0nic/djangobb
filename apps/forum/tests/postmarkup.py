import unittest

from forum.markups import mypostmarkup

class PostmarkupTestCase(unittest.TestCase):
    def setUp(self):
        self.markup = mypostmarkup.markup

    def testLinkTag(self):
        link = 'http://ya.ru/'
        self.assertEqual('<a href="%s">%s</a>' % (link, link),
                         self.markup('[url]%s[/url]' % link))


    def testPlainTest(self):
        text = 'just a text'
        self.assertEqual(text, self.markup(text))
    
    def testNewLines(self):
        text = 'just a\n text'
        self.assertEqual('just a<br/> text', self.markup(text))
    
    def testCodeTag(self):
        text = 'foo [code]foo\nbar[/code] bar'
        self.assertEqual('foo <pre><code>foo\nbar</code></pre>bar', self.markup(text))

