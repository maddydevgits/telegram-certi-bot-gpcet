from flask import Flask,render_template,redirect,request,session
import json
import os
from werkzeug.utils import secure_filename
import boto3
client=boto3.client('s3')

def upload_files(file_name,bucket,object_name=None, args=None):
    if object_name is None:
        object_name = file_name
    client.upload_file(file_name,bucket,object_name, ExtraArgs={'ACL': 'public-read'})

def store_data_into_db(name,email,password):
    data={}
    data['name']=name
    data['email']=email
    data['password']=password
    data=json.dumps(data)
    f=open('dataset.txt','a')
    f.write('\n')
    f.writelines(data) 
    f.close()

def read_data_from_db():
    f=open('dataset.txt','r')
    k=f.readlines()
    f.close()
    return(k)

def shareFilestoUser(email,fileId):
    f=open('files.txt','a')
    data={}
    data['user']=session['email']
    data['email']=email
    data['fileId']=fileId
    data=json.dumps(data)
    f.write('\n')
    f.writelines(data)
    f.close()
    
app=Flask(__name__)
app.secret_key='makeskilled'
app.config["UPLOAD_FOLDER"] = "uploads/"

@app.route('/')
def indexPage():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/registerUser',methods=['GET','POST'])
def registerUser():
    name=request.form['name']
    email=request.form['email']
    password=request.form['pass']
    print(name,email,password)
    store_data_into_db(name,email,password)
    return render_template('index.html')

@app.route('/loginUser',methods=['POST','GET'])
def loginUser():
    name=request.form['your_name']
    password=request.form['your_pass']
    print(name,password)
    k=read_data_from_db()
    print(k)
    for i in k:
        if len(i)<3:
            continue
        dummy=json.loads(i)
        if (dummy['name']==name and dummy['password']==password):
            session['username']=name
            session['email']=dummy['email']
            return redirect('/dashboard')
    return render_template('index.html')

@app.route('/uploadDocument',methods=['POST','GET'])
def uploadDocument():
    files = request.files.getlist('chooseFiles')
    # doc=request.files['chooseFile']
    if session['username'] not in os.listdir():
        os.mkdir(session['username'])
    for i in files:
        doc1=secure_filename(i.filename)
        i.save(session['username']+'/'+doc1)
        upload_files(session['username']+'/'+doc1,'msteam')
    return redirect('/documents')

@app.route('/documents')
def documents():
    s3_resource = boto3.resource("s3", region_name='us-east-1')
    s3_bucket = s3_resource.Bucket('msteam')
    data=[]
    for obj in s3_bucket.objects.filter(Prefix=session['username']+"/"):
    # for obj in s3_bucket.objects.all():
        print(f'-- {obj.key}')
        dummy=[]
        dummy.append(obj.key)
        dummy.append(session['username'])
        dummy.append('https://msteam.s3.amazonaws.com/'+obj.key)
        data.append(dummy)
    print(data)
    return render_template('documents.html',len=len(data),dashboard_data=data)

@app.route('/shareDocument')
def shareDocument():
    k=read_data_from_db()
    print(k)
    data=[]
    for i in k:
        if len(i)<3:
            continue
        dummy=json.loads(i)
        if dummy['email']==session['email']:
            continue
        data.append(dummy['email'])
    
    s3_resource = boto3.resource("s3", region_name='us-east-1')
    s3_bucket = s3_resource.Bucket('msteam')
    data1=[]
    for obj in s3_bucket.objects.filter(Prefix=session['username']+"/"):
    # for obj in s3_bucket.objects.all():
        print(f'-- {obj.key}')
        data1.append(obj.key)
    
    return render_template('sharedocument.html',len=len(data),len1=len(data1),dashboard_data=data,dashboard_data1=data1)

@app.route('/toShareBuddy',methods=['POST','GET'])
def toShareBuddy():
    userId=request.form['userId']
    docId=request.form['docID']
    print(userId,docId)
    f=open('files.txt','r')
    k=f.readlines()
    f.close()
    for i in k:
        if len(i)<3:
            continue
        dummy=json.loads(i)
        print(dummy)
        if dummy['user']==session['email'] and dummy['email']==userId and dummy['fileId']==docId:
            break
    else:
        shareFilestoUser(userId,docId)
    return redirect('/sharedDocuments')

@app.route('/sharedDocuments')
def sharedDocuments():
    f=open('files.txt','r')
    k=f.readlines()
    f.close()
    data=[]
    for i in k:
        if len(i)<3:
            continue
        dummy=json.loads(i)
        if dummy['user']==session['email']:
            datai=[]
            datai.append(dummy['fileId'])
            datai.append(dummy['email'])
            datai.append('https://msteam.s3.amazonaws.com/'+dummy['fileId'])
            data.append(datai)
    l=len(data)
    print(data)
    return render_template('shareddocuments.html',len=l,dashboard_data=data)

@app.route('/buddyDocuments')
def buddyDocuments():
    f=open('files.txt','r')
    k=f.readlines()
    f.close()
    data=[]
    for i in k:
        if len(i)<3:
            continue
        dummy=json.loads(i)
        if dummy['email']==session['email']:
            datai=[]
            datai.append(dummy['fileId'])
            datai.append(dummy['user'])
            datai.append('https://msteam.s3.amazonaws.com/'+dummy['fileId'])
            data.append(datai)
    l=len(data)
    print(data)

    return render_template('buddydocuments.html',len=l,dashboard_data=data)
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

@app.route('/route/<id>')
def deleteSharing(id):
    f=open('files.txt','r')
    k=f.readlines()
    f.close()
    lineCount=0
    sCount=0
    mCount=0
    print(session['email'])
    for i in k:
        if len(i)<3:
            continue
        dummy=json.loads(i)
        lineCount+=1
        if dummy['user']==session['email']:
            #print(sCount)
            if(sCount==int(id)):
                mCount=lineCount
            sCount+=1
    print(mCount)

    try:
        with open('files.txt','r') as fr:
            lines=fr.readlines()
            ptr=1
            with open('files.txt','w') as fw:
                for line in lines:
                    if ptr!=mCount:
                        fw.write('\n')
                        fw.write(line)
                    
                        
                    ptr+=1
    except:
        print('Oops!')
    with open('files.txt', 'r') as f:
        with open('files.txt', 'w') as w:
            for line in f:
                if line.strip():
                    w.write(line)

    #print(id)
    return redirect('/sharedDocuments')

if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0',port=5001)