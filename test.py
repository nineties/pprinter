from pretty import *
from nose.tools import *

def test_list_or_str():
    eq_(pprint_s([]), '')
    eq_(pprint_s(['Hello', 'World']), 'HelloWorld')
    eq_(pprint_s(['Hello', ['Pretty', 'Printer']]), 'HelloPrettyPrinter')

def test_newline():
    doc = weave('abcdefg', nl())
    eq_(pprint_s(doc), 'a\nb\nc\nd\ne\nf\ng')

def test_breakable():
    doc = breakable(weave('abcdefg', nl()))
    eq_(pprint_s(doc), 'abcdefg')
    eq_(pprint_s(doc, width=3), 'abc\ndef\ng')

    doc = breakable(weave('abcdefg', nl(';')))
    eq_(pprint_s(doc), 'a;b;c;d;e;f;g')
    eq_(pprint_s(doc, width=4), 'a;b\nc;d\ne;f\ng')

def test_group():
    doc = group(weave('abcdefg', nl()))
    eq_(pprint_s(doc), 'abcdefg')
    eq_(pprint_s(doc, width=7), 'abcdefg')
    eq_(pprint_s(doc, width=6), 'a\nb\nc\nd\ne\nf\ng')

    doc = group([
            group(weave('abcdefg', nl())),
            nl(),
            group(weave('ABCDEFG', nl()))
            ])
    eq_(pprint_s(doc), 'abcdefgABCDEFG')
    eq_(pprint_s(doc, width=7), 'abcdefg\nABCDEFG')

def test_nest():
    doc = nest(2, breakable(weave('abcdefg', nl())))
    eq_(pprint_s(doc), 'abcdefg')
    eq_(pprint_s(doc, width=4), 'abcd\n  ef\n  g')

    doc = nest(2, group(weave('abcdefg', nl())))
    eq_(pprint_s(doc), 'abcdefg')
    eq_(pprint_s(doc, width=4), 'a\n  b\n  c\n  d\n  e\n  f\n  g')
