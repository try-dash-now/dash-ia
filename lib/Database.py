# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
import sqlite3
def CreateTable(dbname, table,table_define):
    db = sqlite3.connect(dbname)  
    cu=db.cursor()
    cu.execute("""create table %s ( %s )"""%(table,table_define))
    db.commit()
    cu.close()
    db.close()
def InsertRecord(dbname, table,record):
    db = sqlite3.connect(dbname)  
    cu=db.cursor()
    cu.execute('''insert into %s values(%s)'''%(table,record))
    db.commit()
    cu.close()
    db.close()
def UpdateRecord(dbname,table, action, condition ):
    #cu.execute("update tasks set status='compleded' where id = 0")
    db = sqlite3.connect(dbname)  
    cu=db.cursor()
    cu.execute('''update %s set %s where %s'''%(table,action,condition))
    db.commit()
    cu.close()
    db.close()   
def RemoveRecord(dbname,table, condition ):
    #cu.execute("update tasks set status='compleded' where id = 0")
    db = sqlite3.connect(dbname)  
    cu=db.cursor()
    cu.execute('''delete from %s where %s'''%(table,condition))
    db.commit()
    cu.close()
    db.close()   
def FetchRecord(dbname,table, condition=''):
    db = sqlite3.connect(dbname)  
    cu=db.cursor()
    if condition!='':
        condition="where %s"%condition
    records =cu.execute('''select * from %s %s'''%(table,condition))
    result =[]    
    for i in records:
        i= list(i)
        result.append(i)
     
    db.commit()
    cu.close()
    db.close()   
    return result

def FetchOne(dbname,table, condition=''):
    db = sqlite3.connect(dbname)  
    cu=db.cursor()
    if condition!='':
        condition="where %s"%condition
    records =cu.execute('''select * from %s %s'''%(table,condition))
    records =cu.fetchone()
    if records:
        result =list(records)
    else:
        result=None   
    db.commit()
    cu.close()
    db.close()   
    return result


        