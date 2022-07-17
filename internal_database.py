from os import path
import sqlite3 as sql
from random import choices
from string import ascii_lowercase, digits
from base64 import encodebytes,decodebytes

# for auto closing cursors
from contextlib import closing

from soupsieve import select

class internal_database():
    
    def __init__(self) -> None:
        
        
        database_name="internal.db"
        
        if not path.exists(database_name):
            # init database writer
            self.connector = sql.connect(database_name,check_same_thread=False)
            self.connector.row_factory = sql.Row
            self.__init_db()
            
            
        # init database writer
        self.connector = sql.connect(database_name,check_same_thread=False)
        self.connector.row_factory = sql.Row
        
        
        
        
             
    def __init_db(self) -> None:
        """create a table named METRICS with all rows specified in constructor
        each row is of type TEXT because it's easier
        """
        
        with closing(self.connector.cursor()) as cursor:
            
            cmd = "create table users(user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,username TEXT,api_key TEXT)"
            cursor.execute(cmd)
            self.connector.commit()
            
            cmd = "create table endpoints(endpoint_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,name TEXT,user_id INTERGER NOT NULL,FOREIGN KEY (user_id) REFERENCES users (user_id))"
            cursor.execute(cmd)
            self.connector.commit()
            
            
            
            
            
    def register_user(self,username:str):
        
        with closing(self.connector.cursor()) as cursor:
            
            username = encodebytes(username.encode("utf-8"))
            api_key = encodebytes("".join(choices(ascii_lowercase+digits,k=64)).encode("utf-8"))
            cursor.execute("INSERT INTO users (username,api_key) values(?,?)",(username,api_key))
            
            self.connector.commit()
            
            return cursor.lastrowid
        
        
    def user_exists(self,username:str)->bool:
        with closing(self.connector.cursor()) as cursor:
            
            username = encodebytes(username.encode("utf-8"))
            return cursor.execute("SELECT user_id FROM users WHERE username=?",(username,)).fetchall() != []
        
        
    def get_username(self,user_id:int)->str:
        
        with closing(self.connector.cursor()) as cursor:
            
            return decodebytes(dict(cursor.execute("SELECT username FROM users WHERE user_id=?",(user_id,)).fetchone())["username"]).decode("utf-8")
        
    def get_user_id(self,username:str)->int:
        
        with closing(self.connector.cursor()) as cursor:
            
            username = encodebytes(username.encode("utf-8"))
            return dict(cursor.execute("SELECT user_id FROM users WHERE username=?",(username,)).fetchone())["user_id"]
        
        
        
    def get_user_api_key(self,user_id:int)->int:
                
        with closing(self.connector.cursor()) as cursor:
            
            return decodebytes(dict(cursor.execute("SELECT api_key FROM users WHERE user_id=?",(user_id,)).fetchone())["api_key"]).decode("utf-8")
        
        
        
    def add_endpoint(self,user_id:str)->bool:
        """
        limite de 12/user, return false si atteinte
        """
        
        edp_n = len(self.get_user_endpoints(user_id)) +1
        
        if edp_n > 12:
            return False
                
        with closing(self.connector.cursor()) as cursor:
            
            cursor.execute("INSERT INTO endpoints (user_id,name) values(?,?)",(user_id,f"endpoint {edp_n}"))
            self.connector.commit()
            return cursor.lastrowid
    
    def endpoint_exists(self,endpoint_id:int):
        with closing(self.connector.cursor()) as cursor:
            
            return cursor.execute("SELECT * FROM endpoints WHERE endpoint_id=?",(endpoint_id,)).fetchall() != []
    
    def get_user_endpoints(self,user_id:int)->list:
        with closing(self.connector.cursor()) as cursor:
            
            return [dict(r) for r in cursor.execute("SELECT * FROM endpoints WHERE user_id=?",(user_id,)).fetchall()]
    
    def rename_endpoint(self,name:str,endpoint_id:int):
        with closing(self.connector.cursor()) as cursor:
            
            cursor.execute("UPDATE endpoints SET name=? WHERE endpoint_id=?",(name,endpoint_id))
            self.connector.commit()
    
    def is_key_allowing_endpoint(self,api_key:str,endpoint_id:int)->bool:
        
        api_key = encodebytes(api_key.encode("utf-8"))
        
        with closing(self.connector.cursor()) as cursor:
            
            return cursor.execute("SELECT api_key FROM endpoints e JOIN users u ON e.user_id=u.user_id WHERE e.endpoint_id=? and u.api_key=?",(endpoint_id,api_key)).fetchall()!= []