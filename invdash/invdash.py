#!/usr/bin/env python
"""
invdash.py: dash docs dbs from objects.inv

Usage:
    invdash.py [OBJECTS] [options]

Options:
    -q       print info
    -e       use extended schema
    -o PATH  write db to path
"""
import os

import attr
from docopt import docopt
from sphinx.util.inventory import InventoryFile
import sqlite3

types_mapping = {
    'c:function':      'Function',
    'c:macro':         'Macro',
    'c:member':        'Member',
    'c:type':          'Type',
    'c:var':           'Variable',
    'py:attribute':    'Attribute',
    'py:class':        'Class',
    'py:classmethod':  'Method',
    'py:data':         'Constant',
    'py:exception':    'Exception',
    'py:function':     'Function',
    'py:method':       'Method',
    'py:module':       'Module',
    'py:parameter':    'Parameter',
    'py:staticmethod': 'Method',
    # No good things for 'something that transforms something'
    # there's 'Modifier', but that's not the relevant sense of the word.
    'std:2to3fixer':   'XXX',
    'std:cmdoption':   'Option',
    'std:doc':         'Guide',
    'std:envvar':      'Variable',
    # Maybe 'Guide'
    'std:label':       'Section',
    'std:opcode':      'Instruction',
    'std:option':      'Option',
    'std:pdbcommand':  'Command',
    'std:term':        'Word',
    'std:token':       'Syntax',
}

standard_schema = """
id INTEGER PRIMARY KEY,
name TEXT,
type TEXT,
path TEXT
"""

schema_extensions = """
raw_type TEXT
"""

std_qry_tmpl = ('insert into searchIndex (name, type, path) '
                'values (?, ?, ?)')

ext_qry_tmpl = ('insert into searchIndex (name, type, path, raw_type) '
                'values (?, ?, ?, ?)')


@attr.s
class Config:
    db_path = attr.ib('docSet.dsidx')
    schema = attr.ib(default=standard_schema)
    query_tmpl = attr.ib(default=std_qry_tmpl)

    @property
    def is_extended_schema(self):
        return self.schema != standard_schema


config = Config()


def read_objs(path):
    with open(path, 'rb') as fp:
        inv = InventoryFile.load(fp, '', os.path.join)
    return inv


def mktab(inv):
    db = sqlite3.connect(config.db_path)
    db.execute('CREATE TABLE searchIndex ({})'.format(config.schema))
    insert_inv_records(db, inv)
    db.commit()
    db.close()


def insert_inv_records(db, inv):
    for inv_type, inv_recs in inv.items():
        insert_type_recs(db, inv_type, inv_recs)


def insert_type_recs(db, inv_type, inv_recs):
    dash_type = types_mapping[inv_type]

    if config.is_extended_schema:
        input_recs = [(rec_name, dash_type, rec[2], inv_type)
                      for rec_name, rec in inv_recs.items()]
    else:
        input_recs = [(rec_name, dash_type, rec[2])
                      for rec_name, rec in inv_recs.items()]

    db.executemany(config.query_tmpl, input_recs)


def print_info(inv):
    print(config.schema)

    if inv:
        print(list(inv.keys()))


def main(args):
    if args['-o']:
        config.db_path = args['-o']

    if args['-e']:
        config.schema = '{},\n{}'.format(standard_schema,
                                         schema_extensions)
        config.query_tmpl = ext_qry_tmpl

    if args['OBJECTS']:
        inv = read_objs(args['OBJECTS'])
    else:
        inv = None

    if args['-q']:
        print_info(inv)
        return

    if inv:
        mktab(inv)


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
