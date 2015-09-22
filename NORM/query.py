
from psycopg2.extras import DictCursor

class Query(object):
    def __init__(self, conn, query, args):
        self.conn = conn
        self.c = self.conn.cursor(cursor_factory=DictCursor)
        self.c.execute(query, args)

    def __iter__(self):
        for row in self.c:
            yield row
        self.c.close()
