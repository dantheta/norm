
import NORM
import NORM.utils
import psycopg2
import unittest
import logging

logging.basicConfig(level = logging.WARN)

class Person(NORM.DBObject):
	TABLE = 'people'
	FIELDS = ['firstname','surname','age']

class FakeCursor(object):
	def __init__(self, conn):
		self.conn = conn

	def execute(self, sql, args = []):
		logging.info("%s: %s", sql, args)
		self.conn.append(sql, args)
		self.sql = sql
		self.args = args

	def fetchone(self):
		if self.sql.lower().startswith('select'):
			if len(self.args) == 0 or self.args[0] == 1:
				return {'firstname': 'joe','surname':'bloggs','age':27,'id':1}
			else:
				return {'firstname': 'jason','surname':'connery','age':52,'id':2}
		elif self.sql.lower().startswith('insert'):
			return {'newid': 2}

	def __iter__(self):
		yield self.fetchone()

	def close(self):
		pass

class FakeConnection(object):
	def __init__(self):
		self.statements = []

	def cursor(self, cursor_factory = None):
		return FakeCursor(self)

	def append(self, sql, args):
		self.statements.append( (sql, args) )

class NormTest(unittest.TestCase):
	def setUp(self):
		self.conn = FakeConnection()
		#self.conn = psycopg2.connect('dbname=normtest')

	def testDelete(self):
		person = Person(self.conn, 2)
		person.delete()

		self.assertEquals(
			self.conn.statements[-1],
			('delete from people where id = %s', [2])
			)

	def testLoad(self):
		person = Person(self.conn, 1)
		self.assertEquals(person['firstname'], 'joe')
		self.assertEquals(person['surname'], 'bloggs')
		self.assertEquals(person['age'], 27)
		self.assertEquals(person['id'], 1)

		if hasattr(self.conn, 'statements'):
			self.assertEquals(
				self.conn.statements[-1],
				('select * from people where id = %s', [1])
			)

	def testLimit(self):
		people = Person.select_all(self.conn, _limit = 10)

		self.assertIn(' LIMIT 10', self.conn.statements[-1][0])

		person = Person.select_all(self.conn, _limit = (10, 10))

		self.assertIn(' LIMIT 10 OFFSET 10', self.conn.statements[-1][0])

	def testSelect(self):
		people = Person.select_all(self.conn)

		self.assertEquals(len(people), 1)
		if hasattr(self.conn, 'statements'):
			self.assertEquals(
				self.conn.statements[-1],
				('select * from people', [])
			)

	def testUpdate(self):
		person = Person(self.conn, 1)
		person['age'] = 28
		person.store()

		if hasattr(self.conn, 'statements'):
			sql, args = self.conn.statements[-1]

			self.assertIn('age = %(age)s', sql)
			self.assertIn('firstname = %(firstname)s', sql)
			self.assertIn('surname = %(surname)s', sql)
			self.assertEquals(args, 
				{'firstname': 'joe','surname':'bloggs','age':28,'id':1}
			)

	def testCreate(self):
		person = Person(self.conn)
		person.update({
			'firstname': 'jason',
			'surname':'connery',
			'age':52,
		})
		person.store()

		if hasattr(self.conn, 'statements'):
			sql, args = self.conn.statements[-1]

			self.assertRegexpMatches(sql, '^insert into people')
			self.assertIn('age', sql)
			self.assertIn('firstname', sql)
			self.assertIn('surname', sql)
			self.assertIn('%(age)s', sql)
			self.assertIn('%(firstname)s', sql)
			self.assertIn('%(surname)s', sql)
			self.assertIn('returning id as newid', sql)
			self.assertEquals(args, {
				'firstname': 'jason',
				'surname': 'connery',
				'age': 52,
				'id': None,
			})

		self.assertEquals(person['id'], 2)

class UtilsTest(unittest.TestCase):
	def testEncodeWhere(self):
		wherestr, args = NORM.utils.encode_where({'age': 20})

		self.assertEquals(wherestr, 'age = %(age)s')
		self.assertIn('age', args)
		self.assertEquals(args['age'], 20)

	def testEncodeWhereCmp(self):
		wherestr, args = NORM.utils.encode_where({'age' : ('>', 20)})
		self.assertEquals(wherestr, 'age > %(age)s')
		self.assertIn( 'age',args)
		self.assertEquals(args['age'], 20)




unittest.main()
