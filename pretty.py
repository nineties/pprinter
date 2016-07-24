"""A python library to create pretty printer.

This library is based on the following paper.
* Philip Wadler. "A pretty printer."
* http://homepages.inf.ed.ac.uk/wadler/papers/prettier/prettier.pdf

"""

__all__ = ['weave', 'nl', 'breakable', 'group', 'nest', 'pprint', 'pprint_s']

import sys
from io import StringIO
from collections import namedtuple

# Utility function
def weave(seq, x):
    seq = list(seq)
    r = []
    n = len(seq)
    for i, y in enumerate(seq):
        r.append(y)
        if i < n-1:
            r.append(x)
    return r

# Document Nodes
Newline = namedtuple('Newline', 'sep')
Nest = namedtuple('Nest', 'indent sep')
Group = namedtuple('Group', 'doc')
Breakable = namedtuple('Breakable', 'doc')

def nl(sep=''):
    return Newline(sep)

def nest(indent, doc):
    if indent == 0:
        return doc
    elif isinstance(doc, str):
        return doc
    elif isinstance(doc, list):
        return [ nest(indent, d) for d in doc ]
    elif isinstance(doc, Nest):
        return doc._replace(indent=indent + doc.indent)
    elif isinstance(doc, Breakable) or isinstance(doc, Group):
        return doc._replace(doc=nest(indent, doc.doc))
    elif isinstance(doc, Newline):
        return Nest(indent, doc.sep)
    else:
        raise Exception('Unknown document: {}'.format(doc))

def group(doc):
    return Group(doc)

def breakable(doc):
    return Breakable(doc)

# Pretty Printer
def occupy(doc):
    if isinstance(doc, str):
        return len(doc)
    elif isinstance(doc, Newline) or isinstance(doc, Nest):
        return len(doc.sep)
    elif isinstance(doc, Group):
        return occupy(doc.doc)
    elif isinstance(doc, Breakable):
        return occupy(doc.doc)
    elif isinstance(doc, list):
        size = 0
        for d in doc:
            size += occupy(d)
        return size
    else:
        raise Exception('Unknown document: {}'.format(doc))

def remain(doc, cont=[]):
    if isinstance(doc, str):
        return len(doc) + remain(cont)
    elif isinstance(doc, Newline) or isinstance(doc, Nest):
        return 0
    elif isinstance(doc, Group) or isinstance(doc, Breakable):
        return remain(doc.doc, cont)
    elif isinstance(doc, list):
        if doc:
            return remain(doc[0], doc[1:]+cont)
        elif cont:
            return remain(cont, [])
        else:
            return 0
    else:
        raise Exception('Unknown document: {}'.format(doc))

def layout(out, w, k, b, c, docs):
    if not docs:
        return k

    doc = docs[0]
    if isinstance(doc, str):
        out.write(doc)
        return layout(out, w, k-len(doc), b, c, docs[1:])
    elif isinstance(doc, Newline):
        if c or (b and len(doc.sep) + remain(docs[1:]) <= k):
            out.write(doc.sep)
            return layout(out, w, k-len(doc.sep), b, c, docs[1:])
        else:
            out.write('\n')
            return layout(out, w, w, b, c, docs[1:])
    elif isinstance(doc, Nest):
        if c or (b and len(doc.sep) + remain(docs[1:]) <= k):
            out.write(doc.sep)
            return layout(out, w, k-len(doc.sep), b, c, docs[1:])
        else:
            out.write('\n')
            out.write(' '*doc.indent)
            return layout(out, w, w-doc.indent, b, c, docs[1:])
    elif isinstance(doc, Group):
        if occupy(doc) <= k:
            k = layout(out, w, k, b, True, [doc.doc])
            return layout(out, w, k, b, c, docs[1:])
        else:
            return layout(out, w, k, b, c, [doc.doc] + docs[1:])
    elif isinstance(doc, Breakable):
        k = layout(out, w, k, True, c, [doc.doc])
        return layout(out, w, k, b, c, docs[1:])
    elif isinstance(doc, list):
        return layout(out, w, k, b, c, doc + docs[1:])

def pprint(doc, out=sys.stdout, width=80):
    layout(out, width, width, False, False, [doc])

def pprint_s(doc, width=80):
    sio = StringIO()
    pprint(doc, out=sio, width=width)
    return sio.getvalue()
