import psycopg2
import psycopg2.extras

class ConnectDatabase():
	DB_SETTINGS = {
					"db" : '',
					"user" : "",
					"passwd" : "",
					"host" : "",
					"port" : "",
				}

	def connect_db(self):
		connection = psycopg2.connect(user = self.DB_SETTINGS['user'],
									  password = self.DB_SETTINGS['passwd'],
									  host = self.DB_SETTINGS['host'],
									  port = self.DB_SETTINGS['port'],
									  database = self.DB_SETTINGS['db'],
									  connect_timeout = 60)
		connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
		return  connection
