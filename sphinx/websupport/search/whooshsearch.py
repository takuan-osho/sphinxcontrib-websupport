# -*- coding: utf-8 -*-
"""
    sphinx.websupport.search.whooshsearch
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Whoosh search adapter.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from whoosh import index
from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh import highlight

from sphinx.util.osutil import ensuredir
from sphinx.websupport.search import BaseSearch

class WhooshSearch(BaseSearch):
    schema = Schema(path=ID(stored=True, unique=True),
                    title=TEXT(field_boost=2.0, stored=True),
                    text=TEXT(analyzer=StemmingAnalyzer(), stored=True))

    def __init__(self, db_path):
        ensuredir(db_path)
        if index.exists_in(db_path):
            self.index = index.open_dir(db_path)
        else:
            self.index = index.create_in(db_path, schema=self.schema)
        self.searcher = self.index.searcher()

    def init_indexing(self, changed=[]):
        for changed_path in changed:
            self.index.delete_by_term('path', changed_path)
        self.writer = self.index.writer()

    def finish_indexing(self):
        self.writer.commit()
       
    def add_document(self, path, title, text):
        self.writer.add_document(path=unicode(path),
                                 title=title, 
                                 text=text)

    def handle_query(self, q):
        res = self.searcher.find('text', q)
        results = []
        for result in res:
            context = self.extract_context(result['text'], q)
            
            results.append((result['path'],
                            result.get('title', ''),
                            context))
        
        return results, len(res), res.scored_length()
