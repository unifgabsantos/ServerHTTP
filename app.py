from ServerHTTP import Server
from hashlib import sha512
from uuid import uuid4
import json
from datetime import datetime
tokens = []


def checkMessage(msg:str):
    msg = msg.replace('"',"'")
    msg = msg.replace("+"," ")
    msg = msg.replace("%40","@")
    return msg

def getName(_token):
    for token in tokens:
        if(token[1]==_token):
            username = token[0]
            user,_ = findUser(username)
            return user["name"]
    return None
def getUser(_token):
    for token in tokens:
        if(token[1]==_token):
            username = token[0]
            return username
    return None
    
def writeChat(body:str):
    body = body.split("&")
    _token,msg = body[0].split("=")[1],body[1].split("=")[1] 
    username = None
    for token in tokens:
        if(token[1]==_token):
            username = token[0]
    if(username==None):
        return "Token não encontrado","404"
    try:
        file = open("./Private/chat.json","r")
        payload = file.read()
        try:
            payload = json.loads(payload)
        except:
            payload = []
        payload.append({"Name":getName(_token),"Date":datetime.today().strftime('%H:%M:%S'),"msg":checkMessage(msg)})
        file.close()
        file = open("./Private/chat.json","w")
        file.write(json.dumps(payload))
        file.close()
        return readPerfil(getName(_token),username),"200","Content-Type: text/html"
    except:
        file = open("./Private/chat.json","x")
        file.close()
        writeChat(_token)

def readChat():
    try:
        file = open("./Private/chat.json","r")
        payload = file.read()
        if (payload==""):
            return None
        payload = json.loads(payload)
        data = ""
        for msg in payload:
            data+=f"{msg['Name']} - {msg['Date']}  ->  {msg['msg']}\n"
        file.close()
        return data
    except:
        return "Usuario não encontrado","404","Content-Type: text/plain"

def findToken(username:str)->str:
    for token in tokens:
        if(token[0]==username):
            return token[1]
    createToken(username)

def createToken(username:str)-> bool:
    for value in tokens:
        if(value[0]==username):
            return False
    tokens.append((username,uuid4().hex))
    return True

def readPerfil(name:str,username:str):
    payload = ""
    file = open("./pages/perfil.html","r",encoding="UTF-8")
    msgs = readChat()
    token = findToken(username)
    for line in file.readlines():
        if ("%=Name%" in line):
            line="<h1>%s</h1>"%name
        elif("%=User%" in line):
            line = '<input type="hidden" name="Token" id="Token" value="%s"><br>'%token
        elif("%=Chat%" in line):
            line = f"<textarea rows='15' cols='70' class='textarea' readonly>{msgs}</textarea>"
        payload+=line
    return payload

def Crypt(string):
  return (sha512(string.encode())).hexdigest()

def findUser(username:str):
    file = open("./private/accounts.json","r")
    payload = file.read()
    if (payload==""):
        return None,None
    file.close()
    payload = json.loads(payload)
    user = None
    for user in payload:
        try:
            user = user[username]
            break
        except:
            user = None
            continue
    return user,payload

def setPassword(username:str,_payload:dict):
    file = open("./private/accounts.json","r")
    payload = file.read()
    payload = json.loads(payload)
    payload[0][username] = _payload[username]
    file.close()
    file = open("./private/accounts.json","w")
    file.write(json.dumps(payload))
    file.close()

def changePassword(body:str):
    body = body.split("&")
    Username,oldPassword,newPassword = (body[0].split("="))[1],(body[1].split("="))[1],(body[2].split("="))[1]
    oldPassword,newPassword = Crypt(oldPassword),Crypt(newPassword)
    token = findToken(Username)
    if(token==None):
        return "Usuario Não Encontrado","404","Content-Type: text/plain"
    _,payload = findUser(token)
    if(oldPassword!=payload[0][Username]["password"]):
        return "Senha Incorreta","401","Content-Type: text/plain"
    payload[0][Username]["password"] = newPassword
    setPassword(Username,payload[0])
    return "Senha Alterada","200","Content-Type: text/plain"

def Login(body:str):
    body = body.split("&")
    username,password = (body[0].split("="))[1],(body[1].split("="))[1]
    password = Crypt(password)
    user,payload = findUser(username)
    createToken(username)
    try:
        if(user["password"]!=password):
            return "Senha incorreta","200","Content-Type: text/plain"
        payload = readPerfil(user["name"],username)
        return payload,"200","Content-Type: text/html"
    except:
        return "Usuario nao encontrado","404","Content-Type: text/plain"

    
def createAccount(body:str):
    body = body.split("&")
    name,username,password = (body[0].split("="))[1],(body[1].split("="))[1],(body[2].split("="))[1]
    user,payload = findUser(username)
    password = Crypt(password)
    if(user!=None):
        return "Usuario Já Cadastrado","200","Content-Type: text/plain"
    if(not(type(payload)==list)):
        payload = []
    payload.append({username:{"name":name,"password":password}})
    file = open("./private/accounts.json","w")
    file.write(json.dumps(payload))
    file.close()
    return "Usuario cadastrado","200","Content-Type: text/plain"


app = Server("0.0.0.0",80)
app.POST("/Cadastrar",createAccount)
app.POST("/Login",Login)
app.POST("/Message",writeChat)
app.POST("/ChangePassword",changePassword)
app.start()
