import googleDriveAPI
import encryption
from flask import Flask, render_template, redirect, request, flash
import pickle
import sys
import os
import sqlite3



database="database1.db"

def createtable():
    conn=sqlite3.connect(database)  
    cursor=conn.cursor()
    cursor.execute("create table if not exists register (id integer primary key autoincrement, name text, mailid text, password text)")
    cursor.execute("create table if not exists upload(id integer primary key autoincrement, mail text, filename text, fildId text, key text)")
    cursor.execute("create table if not exists status(id integer primary key autoincrement, mail text, filename text, fildId text, key text,status text,user text)")
    conn.commit()
    conn.close()
createtable()


app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('login.html')

@app.route('/data')
def data():
    return render_template('data.html')



@app.route('/register', methods=['GET','POST'])
def register():   
    if request.method == 'POST':
        name = request.form['userid']
        mail = request.form['mail']
        password = request.form['password']
        con=sqlite3.connect(database)
        cur=con.cursor()
        cur.execute("SELECT mailid FROM register WHERE mailid=?", (mail,))
        registered = cur.fetchall()
        if registered:
            return display_popup1 ("your userid already registered")
        else:   
             cur.execute("insert into register(name, mailid, password  )values(?,?,?)",(name, mail, password))
             con.commit()
             return render_template('login.html')            
    return render_template('login.html')

data1=[]
data2=[]
@app.route('/login', methods=['GET','POST'])
def login():
    global mail
    if request.method == 'POST':
        try:
            mail = request.form['userid']
            password = request.form['password']
            con=sqlite3.connect(database)
            cur=con.cursor()
            cur.execute("select * from register where mailid=? and password=?",(mail,password))
            data=cur.fetchone()
            data1.append(data[1])
            data2.append(data[2])
            if data is None:
                    return "failed"       
            else:               
                return render_template('data.html',name=data1[-1],email=data2[-1])        
        except Exception as e:
                return 'Login Failed'
    return render_template('login.html')

@app.route('/back', methods=['GET','POST'])
def back():
    return render_template('data.html',name=data1[-1],email=data2[-1])        


@app.route('/input', methods=['GET','POST'])
def input():
    if request.method == 'POST':
        try:            
            user_In = request.files['image']
            print(user_In)
            filename = user_In.filename
            data = googleDriveAPI.searchFile(filename)
            print(data)
            
            if data == 'item':
                print('data',data)
                upload_folder = os.path.join(os.getcwd(), 'uploads')
                print(upload_folder)
                if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, f'{filename}')               
                user_In.save(file_path)
                print('work')
                key=encryption.encrypt(filename)
                print(key)
                googleDriveAPI.uploadFile(filename)
                fileId = googleDriveAPI.fileID(filename)
                print('id',fileId)
                con=sqlite3.connect(database)
                cur=con.cursor()
                cur.execute("insert into upload(mail, filename, fildId, key)values(?,?,?,?)",(mail, filename, (str(fileId)), (str(key))))
                con.commit()
                output="Upload Successfully"
                return render_template('output.html',output=output)
            else: 
                 output="Already File Name Exists"
                 return render_template('output.html',output=output)
        except Exception as e:
            print(e)
            output="Try again to upload"
            return render_template('output.html',output=output)
    return render_template('input.html')

@app.route('/download', methods=['GET','POST'])
def download():
    if request.method == 'POST':
        try:
            user_In = request.form['image']            
            key = request.form['key']
            fileID= googleDriveAPI.fileID(user_In)
            googleDriveAPI.downloadFile(fileID, user_In)
            encryption.decrypt(user_In, key)
            output="Download Successfully"
            return render_template('output.html',output=output)            
        except:
            output="Something went Wrong"
            return render_template('output.html',output=output) 
    return render_template('download.html')

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
            user_In = request.form['image']            
            fileID= googleDriveAPI.fileID(user_In)
            con=sqlite3.connect(database)
            cur=con.cursor()
            cur.execute("select * from upload where fildId=?",(fileID,))
            data=cur.fetchone()
            if data is None:
                    return "file not found"        
            else:
                cur.execute("insert into status(mail, filename, fildId, key,status,user)values(?,?,?,?,?,?)",(data[1],data[2],data[3],data[4],0,mail))
                con.commit() 
                output="Request Sent"
                return render_template('output.html',output=output)
    return render_template('search.html')


@app.route('/search1', methods=['GET','POST'])
def search1():
        conn=sqlite3.connect(database)
        cursor=conn.cursor()
        cursor.execute("select * from status where status=? and  mail=? ",(0,mail))
        data=cursor.fetchall()
        return render_template("request.html",results=data)
                       

@app.route('/accept', methods=['GET','POST'])
def accept():
        userid=request.form["number1"]
        conn=sqlite3.connect(database)
        cursor=conn.cursor()
        cursor.execute("update status set status=1 where id=?",(userid))
        conn.commit()
        output="Quantum Key sent"
        return render_template('output.html',output=output)
    
@app.route('/message', methods=['GET','POST'])
def message():
        conn=sqlite3.connect(database)
        cursor=conn.cursor()
        cursor.execute("select * from status where status=? and  user=? ",(1,mail))
        data=cursor.fetchall()
        return render_template("message.html",results=data)



if __name__ == "__main__":
   app.run(port=8080, debug=False)
