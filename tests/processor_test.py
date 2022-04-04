import unittest
from wiki.core import Processor


class TestProcessor(unittest.TestCase):
    def testProcessor(self):
        markdown = """title: Some text
tags: Tag1,Tag2,Tag3,Tag4,Tag5

asdfasdfasdf

#Header 1
Text
## subheader 1.1
text
### sub-sub-header
text
#Header 2
text#
## subheader 2.1
## subheader 2.2
        """
        processor = Processor(markdown)
        html, body, _meta, headers = processor.process()
        self.assertEqual(headers,
                         ['Header 1', 'subheader 1.1', 'Header 2', 'subheader 2.1', 'subheader 2.2'])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProcessor))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
