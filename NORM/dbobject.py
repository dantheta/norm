
from __future__ import with_statement

import sys
import utils
from contextlib import closing

from psycopg2.extras import DictCursor

from exceptions import *

class DBObject(object):
    """ Base class for 'Model' type objects. """

    TABLE = None
    FIELDS = []
    RETURN_NEW_ID = True
    SYSTEM_FIELDS = ['id','created','last_updated']
    
    
    def __init__(self, conn, id = None, data = None):
        """Arguments: db connection.  Optional: id or data to load/preload a specific record."""
        
        self.conn = conn
        self.clear()
        if id != None:
            self.load(id)
        elif data != None:
            self.load_dict(data)

    @property
    def id(self):
        """defined only for convenience - self['id'] is the authoritative var for this"""
        return self['id']

    def load(self, objid):
        """Load a record from the target table identified by ID."""
        with closing(self.conn.cursor(cursor_factory = DictCursor)) as c:
            c.execute("select * from %s where id = %%s"%(self.TABLE), [objid])
            row = c.fetchone()
            if row == None:
                raise ObjectNotFound(objid, self.TABLE)
            self.load_dict(row)

    def reload(self):
        self.load(self['id'])
        
    def load_dict(self, row):
        """Load data from supplied dictionary"""
        self.clear()
        self.data.update(row)


    def store(self):
        """Insert to / Update target table with data in this instance."""
        if self['id'] != None:
            self._update(**self.data)
        else:
            self['id'] = self._insert(**self.data)
            return self['id']

    def delete(self):
        """Delete currently loaded record from the target table."""
        if self['id'] != None:
            self._delete(self['id'])

    def clear(self):
        """Reset the data variables for this instance."""
        self.data = {'id': None}

    def update(self, data):
        """Update data from supplied dictionary (like dict.update).  
        Use DBObject.store to save the record."""
        self.data.update(data)
    
    def __setitem__(self, index, value):
        """Set data using the dictionary interface."""
        self.data[index] = value

    def __getitem__(self, index):
        """Fetch data using the dictionary interface."""
        return self.data[index]

    def get(self, index, default = None):
        """Fetch data using the dictionary interface."""
        return self.data.get(index, default)

    def get_data(self):
        return self.data

    def keys(self):
        """Return defined column names."""
        return self.data.keys()


    #- SQL


    @classmethod
    def do_select(klass, conn, id = None, _orderby = None, _limit = None, **kw):
        """Heavy lifting for select methods"""
        sql = "select * from %s" %(klass.TABLE)
        args = []
        if id != None or kw != {}:
            sql += " where "
        if kw:
            if id != None:
                kw['id'] = id
            sql +=  utils.encode_where(kw)
            args = kw
        elif id != None:
            sql += " id = %s"
            args = [id]
        if _orderby:
            if type(_orderby) == str:
                _orderby = [_orderby]
            for orderterm in _orderby:
                if orderterm.lstrip('-') not in (klass.FIELDS + klass.SYSTEM_FIELDS):
                    raise InvalidFieldError("Invalid sort order", orderterm)
            sql += ' ORDER BY ' + ','.join([ ("%s DESC" % (x[1:]) if x[0] == '-' else x) for x in _orderby])
        if _limit:
            if isinstance(_limit, tuple):
                sql += " LIMIT %d" %(int(_limit[0]))
                sql += " OFFSET %d" %(int(_limit[1]))
            else:
                sql += " LIMIT %d" %(int(_limit))
        c = conn.cursor(cursor_factory = DictCursor)
        c.execute(sql, args)
        return c

    @classmethod
    def select(klass, conn, id = None, **kw):
        """Select rows from target table.   Returns generator for result set."""
        with closing(klass.do_select(conn, id, **kw)) as c:
            for row in c:
                yield klass(conn, data = row)
    
    @classmethod
    def select_one(klass, conn, id = None, **kw):
        """Select a single row from the target table.  Returns dict"""
        with closing(klass.do_select(conn, id, **kw)) as c:
            row = c.fetchone()
            if row == None:
                raise ObjectNotFound(klass.TABLE)
            return klass(conn, data = row)

    @classmethod
    def count(klass, conn, **kw):
        sql = "select count(*) from " + klass.TABLE 
        if kw:
            where = utils.encode_where(kw)
            sql +=  " WHERE " + where
        with closing(conn.cursor()) as c:
            c.execute(sql, kw)
            row = c.fetchone()
            return row[0]
            
    @classmethod
    def select_iter(klass, conn, id = None, **kw):
        """Alias for select."""
        return klass.select(conn, id, **kw)

    @classmethod
    def select_all(klass, conn, id = None, **kw):
        """Select rows from target table.  Returns whole resultset as list of dicts"""
        return list( klass.select(conn, id, **kw) )

    def _update(self, id, **kw):
        """Update target table with data specified as keyword parameters."""
        sql = "update %s set " %(self.TABLE)
        for k in kw:
            if k in self.SYSTEM_FIELDS: continue
            sql += " %s = %%(%s)s," % (k,k)
        sql += "last_updated = now() where id = %(id)s"

        values = kw.copy()
        values['id'] = id

        with closing(self.conn.cursor(cursor_factory = DictCursor)) as c:
            c.execute(sql, values)

    def _insert(self, **kw):
        """Insert to target table, returning ID for new record."""
        f = []
        v = []
        for k in kw:
            if k in self.SYSTEM_FIELDS: continue
            if kw[k] != None:
                f.append(k)
                v.append( "%%(%s)s" %(k) )

        sql = "insert into %s (" %(self.TABLE)
        sql += ','.join(f)
        sql += ", created, last_updated) values ("
        sql += ','.join(v)
        sql += ", now(), now())"
        if self.RETURN_NEW_ID:
            sql += " returning id as newid"

        values = kw.copy()

        with closing(self.conn.cursor(cursor_factory = DictCursor)) as c:
            c.execute(sql, values)
            if self.RETURN_NEW_ID:
                newid = c.fetchone()['newid']
                return newid

    def _delete(self, id):
        """Delete row from target table."""
        self._real_delete(id)

    def _real_delete(self, id):
        """Delete row from target table."""
        sql = "delete from %s" %(self.TABLE)
        sql += " where id = %s"

        with closing(self.conn.cursor()) as c:
            c.execute(sql, [id])

    ## pickle support

    def __getstate__(self):
        args = self.__dict__.copy()
        args['conn'] = None
        return args

    ## session support
    def detach(self):
        self.conn = None

    def attach(self, conn):
        self.conn = conn


