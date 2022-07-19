from MySQLdb import _mysql
from constants import MYSQL


db=_mysql.connect(host="ThaaoBlues.mysql.pythonanywhere-services.com",user=MYSQL["username"],
                  password=MYSQL["password"],database="internal")