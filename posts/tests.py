from django.test import TestCase

from .sublink import parse_sublinks, SUBLINK_DIV


class TestSublink(TestCase):
    text = """
        <h3>1. This is a header</h3><h4>2. This is its subheader</h4>
            <h4>3. This is its subheader</h4>
            <p>Here's some explanation.<p>
            <h4>4. This is another subheader</h4>
            <p>Here's some explanation.<p>
        <h3>5. Here is a new header</h3>
        <h2>6. TEST</h2>
            <h4>7. With</h4>
            <p>Here's some explanation.<p>
            <h5 attr='test'>8. some</h5>
            <p>Here's some explanation.<p>
            <h2t>Should be skipped</h2t>
            <h3t attr='test'>Should be skipped</h3t>
        <h4>9, other</h4>
            <p>Here's some explanation.<p>
        <h4>10. subheaders</h4>
            <p>Here's some explanation.<p>
    """
        
    def test_parse_sublinks(self):
        ut, sll = parse_sublinks(self.text)
        
        id_len = 0
        for sl in sll:
            id_len += len(SUBLINK_DIV.format(sl.div_id))

        self.assertEqual(len(sll), 10)
        self.assertEqual(len(ut), len(self.text) + id_len)
        
        # check indents
        self.assertEqual(sll[0].indent, 0)
        self.assertEqual(sll[1].indent, 1)
        self.assertEqual(sll[4].indent, 0)
        self.assertEqual(sll[5].indent, 0)
        self.assertEqual(sll[6].indent, 1)
        self.assertEqual(sll[7].indent, 2)

        self.assertEqual(sll[5].text, '6. TEST')
        self.assertEqual(sll[9].text, '10. subheaders')
