from flask import Flask,render_template,request,redirect,url_for import mysql.connector 
from datetime import datetime 
import random 
from Crypto.Cipher import AES 
from Crypto.Util import Counter 
from Crypto import Random 
import PyPDF2 
import os 
import base64 
import random 
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText  
from email.mime.base import MIMEBase  
from email import encoders 
UPLOAD_FOLDER = 'static/file/' 
app = Flask(name) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
BS = 16 
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) %  BS), 'utf-8') 
unpad = lambda s : s[0:-ord(s[-1:])] 
class AESCipher: 
 def init( self, key ): 
 self.key = bytes(key, 'utf-8') 
 def encrypt( self, raw ): 
 raw = pad(raw) 
 iv = Random.new().read( AES.block_size ) 
 cipher = AES.new(self.key, AES.MODE_CBC, iv )
 return base64.b64encode( iv + cipher.encrypt( raw ) ) 
 def decrypt( self, enc ): 
 enc = base64.b64decode(enc) 
 iv = enc[:16] 
 cipher = AES.new(self.key, AES.MODE_CBC, iv )  return unpad(cipher.decrypt( enc[16:] )).decode('utf8') 
cipher = AESCipher('mysecretpassword') 
@app.route('/') 
@app.route('/main') 
def index(): 
 return render_template('main.html') 
@app.route('/sender') 
def sender(): 
 return render_template('sender.html') 
@app.route('/receiver') 
def receiver(): 
 return render_template('receiver.html') 
@app.route('/sregister') 
def sreg(): 
 return render_template('/sregister.html') 
@app.route('/rregister') 
def rreg(): 
 return render_template('/rregister.html') 
@app.route('/svalidate',methods=['POST','GET']) def svalid(): 
 global data1 
 if request.method == 'POST': 
 data1 = request.form.get('username')
 data2 = request.form.get('password') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "SELECT * FROM send WHERE name = %s AND  password = %s" 
 val = (data1, data2) 
 mycursor.execute(sql,val) 
 account = mycursor.fetchone() 
 print(account) 
 if account: 
 return render_template('sadmin.html',u=data1)  else: 
 return render_template('sender.html',msg = 'Invalid  Username or Password') 
@app.route('/rvalidate',methods=['POST','GET']) 
def rvalid(): 
 global rdata1 
 if request.method == 'POST': 
 rdata1 = request.form.get('username') 
 data2 = request.form.get('password') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "SELECT * FROM receive WHERE name = %s AND  password = %s" 
 val = (rdata1, data2) 
 mycursor.execute(sql,val) 
 account = mycursor.fetchone() 
 print(account) 
 if account: 
 return redirect('view') 
 else: 
return render_template('sender.html',msg = 'Invalid 
Username or Password') 
@app.route('/sregisterform',methods=['POST','GET']) def sregform(): 
 if request.method == 'POST': 
 name = request.form.get('name') 
 mail = request.form.get('mail') 
 password = request.form.get('password') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "INSERT INTO send (name, email, password) VALUES  (%s, %s, %s)" 
 val = (name, mail, password) 
 mycursor.execute(sql, val) 
 mydb.commit() 
 return render_template('sender.html') 
@app.route('/rregisterform',methods=['POST','GET']) def rregform(): 
 if request.method == 'POST': 
 name = request.form.get('name') 
 mail = request.form.get('mail') 
 password = request.form.get('password') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "INSERT INTO receive (name, email, password)  VALUES (%s, %s, %s)" 
 val = (name, mail, password) 
 mycursor.execute(sql, val) 
 mydb.commit() 
 return render_template('receiver.html')
@app.route('/uploadpage') 
def uppage(): 
 return render_template('sadmin.html') 
@app.route('/upload',methods=['POST','GET']) 
def upload(): 
 global encrypted 
 if request.method == 'POST': 
 s_name = data1 
 file_name = request.form.get('filename') 
 file = request.files['file'] 
 file_path = os.path.join(app.config['UPLOAD_FOLDER'],  file.filename) 
 encrypted = cipher.encrypt(file_path) 
 # hashid = hashlib.sha256(file_name.encode()).hexdigest()  file.save(file_path) 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "SELECT * FROM files WHERE f_name = %s"  val = (file_name,) 
 mycursor.execute(sql,val) 
 account = mycursor.fetchone() 
 if account: 
 return render_template('sadmin.html',msg='File Name  Already Exists') 
 else:  
 a = [] 
 file = file_path 
 splits = [2,4] 
 pdfFileObj = open(file, 'rb') 
 fileReader = PyPDF2.PdfFileReader(pdfFileObj)  start = 0 
 end = splits[0] 
 for i in range(len(splits)+1): 
 pdfWriter = PyPDF2.PdfFileWriter()
 output = file.split('.pdf')[0] + str(i) + '.pdf' 
 a.append(output) 
 for page in range(start,end): 
 pdfWriter.addPage(fileReader.getPage(page))  with open(output, "wb") as f: 
 pdfWriter.write(f) 
 start = end 
 try: 
 end = splits[i+1] 
 except IndexError: 
 end = fileReader.numPages 
 pdfFileObj.close() 
 file1 = a[0] 
 file2 = a[1] 
 encrypt1 = cipher.encrypt(file1) 
 encrypt2 = cipher.encrypt(file2) 
 sql = "INSERT INTO files (s_name, f_name, f_path1,  f_path2, f_path3) VALUES (%s, %s, %s, %s, %s)" 
 val = (s_name, file_name,encrypted, encrypt1, encrypt2)  mycursor.execute(sql, val) 
 mydb.commit() 
 return render_template('sadmin.html',msg='File Upload  Successfully') 
@app.route('/file') 
def file(): 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 cursor = mydb.cursor() 
 sql = "SELECT * FROM files WHERE s_name = %s "  val = (data1,) 
 cursor.execute(sql,val) 
 result = cursor.fetchall() 
 return render_template('sfile.html',data = result) 
@app.route('/req')
def re(): 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "SELECT * FROM req WHERE s_name = %s AND req =  %s " 
 val = (data1,'Yes') 
 mycursor.execute(sql,val) 
 account = mycursor.fetchall() 
 return render_template('sreq.html',data = account) 
@app.route('/key',methods=['POST','GET']) 
def key(): 
 global r 
 if request.method == 'POST': 
 fname = request.form.get('fname') 
 rname = request.form.get('rname') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "SELECT * FROM receive WHERE name = %s "  val = (rname,) 
 mycursor.execute(sql,val) 
 account = mycursor.fetchall() 
 if account: 
 for i in account: 
 r = random.randint(100000,999999) 
 ema = i[2] 
 fromaddr = "daminmain@gmail.com" 
 toaddr = ema 
 msg = MIMEMultipart()  
 msg['From'] = fromaddr  
 msg['To'] = toaddr  
 msg['Subject'] = 'Security Key From Sender'  body = f"This is your OTP for {fname} : {r} \nPlease 
enter properly." 
 msg.attach(MIMEText(body, 'plain'))  
 s = smtplib.SMTP('smtp.gmail.com', 587)   s.starttls()  
 s.login(fromaddr, "kpqtxqskedcykwjz")  
 text = msg.as_string()  
 s.sendmail(fromaddr, toaddr, text)  
 s.quit() 
 return render_template('sfile.html') 
@app.route('/down',methods=['POST','GET']) 
def down(): 
 key1 = r 
 if request.method == 'POST': 
 fname = request.form.get('fname') 
 key = request.form.get('key') 
 if key1 == int(key): 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 cursor = mydb.cursor() 
 sql = "SELECT * FROM files WHERE f_name = %s"  val = (fname ,) 
 cursor.execute(sql,val) 
 result = cursor.fetchall() 
 if result: 
 for i in result: 
 filea = i[3] 
 decrypted = cipher.decrypt(filea) 
 return  
render_template('download.html',fpath=decrypted) 
 else: 
 return 'Wrong Key!' 
@app.route('/view') 
def view(): 
 mydb = 
mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 cursor = mydb.cursor() 
 sql = "SELECT * FROM files" 
 cursor.execute(sql) 
 result = cursor.fetchall() 
 return render_template('radmin.html',data = result) 
@app.route('/request',methods=['POST','GET']) 
def reque(): 
 if request.method == 'POST': 
 sname = request.form.get('sname') 
 fname = request.form.get('fname') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "INSERT INTO req (s_name, r_name, f_name, req)  VALUES (%s, %s, %s, %s)" 
 val = (sname, rdata1, fname, 'Yes') 
 mycursor.execute(sql, val) 
 mydb.commit() 
 return render_template('sfile.html') 
@app.route('/down',methods=['POST','GET']) 
def down(): 
 key1 = r 
 if request.method == 'POST': 
 fname = request.form.get('fname') 
 key = request.form.get('key') 
 if key1 == int(key): 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 cursor = mydb.cursor() 
 sql = "SELECT * FROM files WHERE f_name = %s"  val = (fname ,)
 cursor.execute(sql,val) 
 result = cursor.fetchall() 
 if result: 
 for i in result: 
 filea = i[3] 
 decrypted = cipher.decrypt(filea) 
 return  
render_template('download.html',fpath=decrypted) 
 else: 
 return 'Wrong Key!' 
@app.route('/view') 
def view(): 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 cursor = mydb.cursor() 
 sql = "SELECT * FROM files" 
 cursor.execute(sql) 
 result = cursor.fetchall() 
 return render_template('radmin.html',data = result) 
@app.route('/request',methods=['POST','GET']) 
def reque(): 
 if request.method == 'POST': 
 sname = request.form.get('sname') 
 fname = request.form.get('fname') 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 mycursor = mydb.cursor() 
 sql = "INSERT INTO req (s_name, r_name, f_name, req)  VALUES (%s, %s, %s, %s)" 
 val = (sname, rdata1, fname, 'Yes') 
 mycursor.execute(sql, val) 
 mydb.commit() 
 return render_template('radmin.html')
@app.route('/verify') 
def verify(): 
 mydb =  mysql.connector.connect(host="localhost",user="root",password="", database="cloud-1") 
 cursor = mydb.cursor() 
 sql = "SELECT * FROM req WHERE r_name = %s "  val = (rdata1, ) 
 cursor.execute(sql,val) 
 result = cursor.fetchall()  
 return render_template('verify.html',data = result)  
if name == 'main': 
 app.run(debug=True,port=4000)