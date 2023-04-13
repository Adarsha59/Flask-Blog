

from flask import Flask, render_template, request ,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail  import Mail
import os
import math
from werkzeug.utils import secure_filename

import json
# with open ('config.json','r') as c:
#     params = json.load(c)["params"]
local_server = True
with open('config.json', 'r', encoding='utf-8') as c:
    params = json.load(c)['params']

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['UPLOAD_FOLDER'] = params['upload_loc']
app.config.update(
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = '465',
        MAIL_USE_SSL=True,
        MAIL_USERNAME=params['g_user'],
        MAIL_PASSWORD=params['g_pass']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contracts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
class Posts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    Sn = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    slag = db.Column(db.String(120), nullable=False)
    Content = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
    tagline = db.Column(db.String(20), nullable=True)
    
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)

@app.route("/post/<string:post_slag>", methods=['GET'])
def post_route(post_slag):
    postss = Posts.query.filter_by(slag=post_slag).first()
    return render_template('post.html', params=params, post=postss)
@app.route("/about")
def about():
    return render_template('about.html',params=params)
   
@app.route("/login", methods = ['GET', 'POST'])
def login():
        if 'user' in session and session['user'] == params['admin_user'] :
            posts = Posts.query.all()
            return render_template('admin.html',params=params, posts =posts)
        if request.method =='POST':
            username = request.form.get('email')
            userpass = request.form.get('pass')

            if( username==params['admin_user'] and userpass == params['admin_pass']):
                # set this season variable
                session['user'] = username
                posts =Posts.query.all()
            return render_template('admin.html',params=params, post =posts)
        else:
            return render_template('login.html',params=params)



@app.route("/edit/<string:Sn>", methods=['GET', 'POST'])
def edits(Sn):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            Title = request.form.get('title')
            slag = request.form.get('slug')
            Content = request.form.get('content')
            img_file = request.form.get('img_file')
            tagline = request.form.get('tagline')
            date = datetime.now()
            if Sn == '0':
                post = Posts(Title=Title, slag=slag, Content=Content, Date =date,img_file=img_file, tagline=tagline)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(Sn=Sn).first()
                post.Title = Title
                post.slag = slag
                post.Content =Content
                post.img_file=img_file
                post.tagline = tagline
                post.Date =date
                db.session.commit()
                return redirect('/edit/'+Sn)
    post = Posts.query.filter_by(Sn=Sn).first()
    return render_template('edit.html', params=params,post =post )
@app.route("/delete/<string:Sn>", methods=['GET', 'POST'])
def delete(Sn):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(Sn=Sn).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/login')
   
@app.route("/uploader", methods = ['GET', 'POST'])
def upload():
    if 'user' in session and session['user'] == params['admin_user']:
        if(request.method=='POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],(f.filename)))
            return "uploaded sucessfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contracts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from from '+name,
                          sender=email,
                          recipients=[params['g_user']],
                          body= message+"\n"+phone)
    return render_template('contact.html',params=params)


app.run(debug=True)


