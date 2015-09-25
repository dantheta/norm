
from query import Query
from utils import encode_where

class View(Query):
    def __init__(self, conn, viewname, **kw):
        self.sql = "SELECT * from {viewname}".format(viewname=viewname)
        if kw:
            self.sql += " WHERE " + utils.encode_where(kw)
        super(View,self).__init__(conn, self.sql, kw)

