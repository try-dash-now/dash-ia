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

if __name__== '__main__':
    dbname= 'sean.db'#sys.argv[1]
    option= 'INIT' #str(sys.argv[2]).upper()
    import sys
    option= sys.argv[1]
    rtdb = sqlite3.connect(dbname)  
    cu=rtdb.cursor() 
    if option.lower().find('reset')!=-1:

        tables = cu.execute('''SELECT name FROM sqlite_master
                                WHERE type='table'
                                ''')
        
        #tables= ['tcpportpool']
        print('reset/delete all tables in  %s'%dbname)
        tables=list(tables)
        for tab in tables:
            try:
                tab=tab[0]
                cu.execute('''drop table %s'''%(tab))
                print('drop talbe %s'%tab)
            except Exception as e:
                print(e)

        print('init database%s'%dbname)
#===============================================================================
# databasename,sean.db
# runningcase,starttime,result,pid,cmd,tcpport
# runningsuie,starttime,result,pid,cmd,tcpport
# historycase,starttime,result,pid,cmd,endtime,duration,tcpport
# historysuite,starttime,result,pid,cmd,endtime,duration,pass,fail,notrun,total,tcpport
# tcpportpool,port,status(in-use,idle)   
#===============================================================================
        tcppool ='tcpportpool'
        try:
            try:
                CreateTable(dbname,tcppool,'port integer primary key UNIQUE ,status varchar(32)')
            except:
                pass
            r = [ """50010, 'idle'""", """50011, 'idle'""", """50012, 'idle'""", """50013, 'idle'""", """50014, 'idle'"""]
            try:
                for i in r:   
                    InsertRecord(dbname, tcppool, i)
            except Exception as e:
                print(e)
            
        except Exception as e:
            print(e)
        
        try:
            CaseInfo='CaseInfo'
            CreateTable(dbname, CaseInfo, 'start_time double primary key UNIQUE, end_time double, pid integer, case_cmd varchar(1024), status varchar(32)')
        except Exception as e:
            print(e)

        taskpool ='tasktcppool'
        try:
            try:
                CreateTable(dbname,taskpool,'port integer primary key UNIQUE ,status varchar(32)')
            except:
                pass
            r = [ """50015, 'idle'""", """50016, 'idle'""", """50017, 'idle'""", """50018, 'idle'""", """50019, 'idle'"""]
            try:
                for i in r:   
                    InsertRecord(dbname, taskpool, i)
            except Exception as e:
                print(e)
            
        except Exception as e:
            print(e)

        try:
            taskpool='taskInfo'
            CreateTable(dbname, taskpool, 'start_time double primary key UNIQUE, end_time double, tcpport integer, task_cmd varchar(1024), status varchar(32)')
        except Exception as e:
            print(e)        
    elif option.lower().find('dump')!=-1:
        tables = cu.execute('''SELECT name FROM sqlite_master
                        WHERE type='table'
                        ORDER BY name; ''')    
        ltable=list(tables)
        for t in ltable:
            t = t[0]
            print('-'*80)
            print('table: %s:'%t)
            allrecord = cu.execute('''select * from %s'''%t)
            for r in allrecord:
                print('\t')
                for i in r:
                    print('\t%s'%i)
                print('')
            
    else:
        print('option not defined')
    try:
 
#===============================================================================
#         if option=='INIT':
#             rtdb = sqlite3.connect(dbname)  
#             cu=rtdb.cursor()   
#     
#             #cu.execute("""create table tasks ( id integer primary key UNIQUE AUTOINCREMENT,start_time varchar(30) UNIQUE , cmd varchar(1024)  ,status varchar(256))""")
#             #cu.execute("""create table case ( id integer primary key UNIQUE AUTOINCREMENT,start_time varchar(30) UNIQUE , cmd varchar(1024)  ,status varchar(256))""")
#         elif option=='RUN':
#             pass
#         
#         else:
#             print('TaskMgr databasename [init|run]\nTaskMgr ended!!!!')  
#         #cu.execute("insert into tasks values(0, '2014-6-23 01:01:02.1234', 'task1 abc def ghi', 'running')") 
#         #cu.execute("insert into tasks values(2, '2014-6-23 01:02:03.1234', 'task1 abc def ghi', 'running')") 
#         rtdb.commit()  
#         cu.execute("select * from tasks")   
#         print (cu.fetchall())  
#         cu.execute("select * from tasks where id = 2")   
#         #print (cu.fetchone())
#         a= list(cu.fetchone())
#         cu.execute("update tasks set status='compleded' where id = 0")   
#         rtdb.commit()   
#         cu.execute("select * from tasks")   
#         print (cu.fetchone())  
# 
# 
# 
# 
#         
#         cu.execute("delete from tasks where id = 1")   
#         rtdb.commit()   
#         cu.execute("select * from tasks")   
#         cu.fetchall()
#===============================================================================


        cu.close()  
        rtdb.close()   
    except Exception as e:
        print(e)
        