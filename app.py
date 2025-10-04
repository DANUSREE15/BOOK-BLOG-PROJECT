from flask import Flask,flash, render_template, request,url_for,redirect,Response,session,send_file,send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from functools import wraps

import os
import csv
import random

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','UPLOAD_FOLDER')

UPLOAD_FOLDER='static/images'
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app=Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='db_book'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql=MySQL(app)

@app.route("/")  
@app.route("/home",methods=["POST","GET"])
def home():
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        if request.form.get("submit") == "submit":
            a = request.form["rname"]
            b = request.form["remail"]
            c = request.form["raddress"]
            d = request.form["rcity"]
            e = request.form["rmobile"]
            f = request.form["rpass"]
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_register (rname, remail, raddress, rcity, rmobile, rpass) VALUES (%s, %s, %s, %s, %s,%s)", (a, b, c, d, e, f))
            mysql.connection.commit()
            cur.close()
   
    return render_template("register.html")
    
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        if request.form["submit"] == "submit":
            a = request.form["uname"]
            b = request.form["upass"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM tbl_register WHERE rname=%s AND rpass=%s", (a, b))
            data = cur.fetchone()
            cur.close()
            if data:
                session['logged_in'] = True
                session['rid'] = data['rid']
                session['lname'] = data['rname']  
                session['lpass'] = data['rpass']  
                flash('Login Successfully', 'success')
                return redirect(url_for('blog'))
            else:
                flash('Invalid Login. Try Again', 'danger')
                return redirect(url_for('login'))
    return render_template("login.html")



@app.route('/blog',methods=["POST","GET"])
def blog():
    return render_template("blog.html")

@app.route('/addblog',methods=["POST","GET"])
def addblog():	
    return render_template("addblog.html")
    
@app.route('/blog_home',methods=["POST","GET"])
def blog_home():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_blog b inner join tbl_register r on b.rid=r.rid")
    data1=cur.fetchall()	
    return render_template("blog_home.html",datas=data1)
    
@app.route('/blogpage',methods=["POST","GET"])
def blogpage():
    if request.method == 'POST':
        if request.form["submit"] == "submit":
            a = request.form["btitle"]
            b = request.form["bdesc"]
            file = request.files['file']
            if file and allowed_extensions(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                new_filename = secure_filename(str(random.randint(10000,99999)) + file_extension)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO tbl_blog(btitle,bdesc,bimage,rid) VALUES (%s,%s,%s,%s)", (a, b, new_filename, session['rid']))
                mysql.connection.commit()
                cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_blog")
    data = cur.fetchall()
    cur.close()

    return render_template("blogpage.html",datas=data)
    
def allowed_extensions(file_name):
    return '.' in file_name and file_name.rsplit('.',1)[1].lower() in FILE_EXTENSIONS
      
@app.route('/blog_view',methods=["POST","GET"])
def blog_view():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_blog where rid=%s",(session['rid'],))
    data=cur.fetchall()	
    return render_template("blog_view.html",datas=data)
    
@app.route('/blogdelete/<string:bid>',methods=["POST","GET"])
def blogdelete(bid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_blog where bid=%s",(bid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("blogpage"))

@app.route('/update_profile',methods=["POST","GET"])
def update_profile():
    if request.method == 'POST':
            if request.form["submit"] == "submit":
                a = request.form["uname"]
                b = request.form["uemail"]
                c = request.form["uaddress"]
                d = request.form["ucity"]
                e = request.form["umobile"]
                f = request.form["upass"]
                cur=mysql.connection.cursor()
                cur.execute("UPDATE tbl_register SET rname=%s,remail=%s,raddress=%s,rmobile=%s,rcity=%s,rpass=%s where rid=%s",(a,b,c,d,e,f,session['rid']))
                mysql.connection.commit() 
                cur.close()
                return redirect(url_for('update_profile'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_register where rid=%s",(session['rid'],))
    data= cur.fetchone()
    cur.close()
    
    return render_template("update_profile.html",datas=data)

@app.route('/view_profile',methods=["POST","GET"])
def view_profile():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_register where rid=%s",(session['rid'],))
    data=cur.fetchall()	
    return render_template("view_profile.html",datas=data)
    
@app.route('/change_pass',methods=["POST","GET"])
def change_pass():
    if request.method == 'POST':
        if request.form["Change Password"] == "Change Password":
            a = request.form["npass"]
            b = request.form["cpass"]
            cur = mysql.connection.cursor()
            if(a==b):
                cur.execute("UPDATE tbl_register SET rpass=%s  where rid=%s",(a,session['rid'],))
                data = cur.fetchone()
                cur.close()
                return redirect(url_for("change_pass"))
                
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_register where rid=%s",(session['rid'],))
    data= cur.fetchall()
    cur.close()
    
    return render_template("change_pass.html",datas=data)
    
@app.route('/blog_comments',methods=["POST","GET"])
def blog_comments():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_blog s inner join tbl_register r on s.rid=r.rid where r.rid=%s",(session['rid'],))
    data=cur.fetchall()	
    return render_template("blog_comments.html",datas=data)
    
@app.route('/view_comments/<string:bid>',methods=["POST","GET"])
def view_comments(bid): 
    if request.method=='POST':
        if request.form['submit'] == 'Add Comment':
            a = request.form["tcomment"]
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_comment(rid, bid, ccomment) VALUES (%s, %s, %s)", (session['rid'], bid, a))
            mysql.connection.commit()
            cur.close()
    cur = mysql.connection.cursor()
    cur.execute("select * from tbl_blog  where bid=%s",(bid,))
    data= cur.fetchall()
    cur.close()
 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_comment c inner join tbl_blog b on c.bid=b.bid inner join tbl_register r on c.rid=r.rid where c.bid=%s",(bid,))
    data1= cur.fetchall()
    cur.close()
    return render_template("view_comments.html",status=data1,datas=data)
    
@app.route('/text_comment/<string:bid>',methods=["POST","GET"])
def text_comment(bid):
    if request.method=='POST':
        if request.form['submit'] == 'Add Comment':
            a = request.form["tcomment"]
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_comment(rid, bid, ccomment) VALUES (%s, %s, %s)", (session['rid'], bid, a))
            mysql.connection.commit()
            cur.close()
    cur = mysql.connection.cursor()
    cur.execute("select * from tbl_blog where bid=%s",(bid,))
    data= cur.fetchall()
    cur.close()
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_comment c inner join tbl_blog b on c.bid=b.bid inner join tbl_register r on c.rid=r.rid where c.bid=%s",(bid,))
    data1= cur.fetchall()
    cur.close()
    return render_template("text_comment.html",status=data1,datas=data)

@app.route('/logout',methods=["POST","GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))
    
if  __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)