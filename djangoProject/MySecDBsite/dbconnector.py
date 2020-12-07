from collections import defaultdict
import mariadb
import pyodbc


# RDS mariadb connectior, make it a single instance to avoid redundent reconnection
class MariadbConnector:
	# check whether connector exists
	the_instance = None

	# use defaultdict to store different connection
	def __init__(self):
		self.query = ""
		self.conn = defaultdict(lambda: None)
		self.cur = defaultdict(lambda: None)
		print("Creating an instance...")

	def connect(self, database, ini=False):
		# if connection exists, return
		if self.conn[database] is not None and not ini:
			return True
		if self.conn[database]:
			self.conn[database].close()
		try:
			self.conn[database] = mariadb.connect(
				# user="admin",
				# password="cs527group",
				user="readonly",
				password="password",
				host="cs527proj.c87d2nussxzu.us-east-2.rds.amazonaws.com",
				port=3306,
				database=database,
				autocommit=False
			)
			self.cur[database] = self.conn[database].cursor()
			return True
		except mariadb.Error as e:
			print(f"Connection failed: {e}")
			return False

	def set_query(self, query):
		self.query = query

	def perform_query(self, database):
		# change the data structure to fit the table render
		# eg. [{'id':1, 'name':'aaa'}, {'id':2, 'name':'bbb'}]
		try:
			self.cur[database].execute(self.query)
			if self.cur[database].description is None:
				return self.cur[database].rowcount
			lst = []
			heads = [column[0] for column in self.cur[database].description]
			data = self.cur[database].fetchmany(1000)
			# for rec in self.cur[database]:
			for rec in data:
				dic = {}
				for attr, head in zip(rec, heads):
					dic[head] = attr
				lst.append(dic)
			return lst
		except mariadb.Error as e:
			print(f"The query is not valid. Please check it again: {e}")
			# return None
			return e;

	@staticmethod
	def get_connected():
		# check if connector is instantialized
		if MariadbConnector.the_instance is None:
			MariadbConnector.the_instance = MariadbConnector()
		return MariadbConnector.the_instance


class RedshiftConnector:
	the_instance = None

	def __init__(self):
		self.query = ""
		self.conn = None
		self.cur = None
		print("Creating an instance...")

	def connect(self, ini=False):
		if self.conn is not None and not ini:
			return True
		try:
			self.conn = pyodbc.connect(
				"Driver={Amazon Redshift (x64)};\
				  Server=redshift-db.ch895iktyy2m.us-east-2.redshift.amazonaws.com;\
				  Database=dev;\
				  UID=readonly;\
				  PWD=Password123;\
				  Port=5439"
			)
			self.cur = self.conn.cursor()
			return True
		except pyodbc.Error as e:
			print(f"Connection failed: {e}")
			return False

	def set_query(self, query):
		self.query = query

	def perform_query(self):
		try:
			self.cur.execute(self.query)
			if self.cur.description is None:
				return self.cur.rowcount
			lst = []
			heads = [column[0] for column in self.cur.description]
			data = self.cur.fetchmany(1000)
			# for rec in self.cur:
			for rec in data:
				dic = {}
				for attr, head in zip(rec, heads):
					dic[head] = attr
				lst.append(dic)
			return lst
		except pyodbc.Error as e:
			print(f"The query is not valid. Please check it again: {e}")
			# return None
			return e

	def rollback(self):
		self.conn.rollback()

	def disconnect(self):
		self.conn.close()

	@staticmethod
	def get_connected():
		if RedshiftConnector.the_instance is None:
			RedshiftConnector.the_instance = RedshiftConnector()
		return RedshiftConnector.the_instance