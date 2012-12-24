NORM
====

Not an ORM - a CRUD helper for python

NORM is a very lightweight database layer for python, built on top of 
DBAPI.  It aims to make it extremely easy to do the simple stuff with
an RDBMS, while still allowing you to drop down to SQL for the complex
stuff.

Record objects behave as dictionaries, but can be persist to the 
database by calling the store method.

On construction, the record object is given a standard python database
connection object, which it uses for storing and retrieving records.

Class methods are provided for performing simple queries on tables.  
These return iterators that yield instances of the required class.

Using NORM
----------

Defining a table mapping:

    class Person(NORM.DBObject):
		TABLE = 'people'
		FIELDS = ['firstname','surname','age']


Loading an object:

	conn = psycopg2.connect('dbname=employees')
	person = Person(conn, id = 1)
	print "{o[firstname]} {o[surname]} is {o[age]} years old".format(
		o = person
	)

Creating an object:

	person = Person(conn)
	person.update({
		'firstname': 'fred',
		'surname': 'bloggs',
		'age': 27
	})
	person.store()


Updating an object:

	person = Person(conn, id = 7)
	person.update({
		'age': 28
	})
	person.store()

or
	
	person = Person(conn, id = 7)
	person['age'] = 28
	person.store()


Querying the table:

	for person in People.select(conn, surname = 'bloggs'):
		print "{o[firstname]} {o[surname]} is {o[age]} years old".format(
			o = person
		)
