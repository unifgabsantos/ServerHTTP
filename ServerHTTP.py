from os import remove,path
from socket import socket,AF_INET,SOCK_STREAM
from threading import Thread
def writeFile(file,data):
    file = open(f"./public{file}","w",encoding="utf-8")
    file.write(data)
    file.close()
serverSocket = socket(AF_INET,SOCK_STREAM)
not_Found =  """
            <!DOCTYPE html>
                <html lang="pt-br">
                <head>
                    <meta charset="UTF-8">
                    <title>404</title>
                </head>
                <body>
                    <h1>Pagina não encontrada!</h1>
                </body>
            </html>
            """

def readFile(path:str)->tuple:
    file = path.split(".")
    filename,extension = file[0].replace("/",""),file[1]
    try:
        #Tentando abrir o arquivo de texto como leitura.(Exemplo: HTML,TXT)
        _file = open(f"./public/{filename}.{extension}","r",encoding="UTF-8")
        payload = _file.read()
        _file.close()
        return payload,"200 OK",f"Content-Type: text/{extension}"
    except:
        try:
            filename,extension = file[0].replace("/",""),file[1]
            #Caso ele tenha dado erro no try, signifca que não é um arquivo de texto, como por exemplo HTML, então ele vai abrir como binario
            _file = open(f"./public/{filename}.{extension}","rb")
            payload = _file.read()
            _file.close()
            if(extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']): 
                return payload,"200 OK",f"Content-Type: image/{extension}"
            if(extension in ["mp4","webm","ogg"]):
                return payload,"200 OK",f"Content-Type: video/{extension}"
            if(extension in ["mp3", "midi", "mpeg", "webm", "ogg", "wav"]):
                return payload,"200 OK",f"Content-Type: audio/{extension}"
            return payload,"200 OK",f"Content-Type: application/{extension}"
        except:
            #Caso ele não consiga encontrar nenhum arquivo, ele envia uma pagina 404
            return not_Found,"404","Content-Type: text/html"

class Server():
    def __init__(self,ip:str,port:int):
        serverSocket.bind((ip,port))
        self.resources = {}
        
    def start(self):
        serverSocket.listen(1)
        while(True):
            try:
                connectionSocket, addr = serverSocket.accept()
                thread = Thread(target=self.__Run__, args=(connectionSocket,))
                thread.start()
            except:
                pass
    def __Resource__(self,request):
        request=request.split("\r\n")
        method = request[0].split(" ")[0]
        resource = request[0].split(" ")[1]
        body = request[-1]
        if (method=="GET"):
            if(resource=="/"):
                return readFile("index.html")
            return readFile(resource)
        if (method=="PUT"):
            if(path.exists(f"./public{resource}")):
                writeFile(resource,body)
                return "Recurso alterado","200","Content-Type: text/plain"
            writeFile(resource,body)
            return "Recurso criado","201","Content-Type: text/plain"
        if(method=="DELETE"):
            if(path.exists(f"./public{resource}")):
                remove(f"./public{resource}")
                return "Recurso deletado","200","Content-Type: text/plain"
            return "Recurso não existente","404","Content-Type: text/plain"
        try:
            payload =  self.resources[resource](body)
            return payload
        except:
            return not_Found,"404","Content-Type: text/html"
    def POST(self,resourceName:str,script):
        self.resources.update({resourceName:script})
    def __Run__(self,connectionSocket):
        data = connectionSocket.recv(2048)
        connectionSocket.settimeout(1)
        try:
            while(True):
                if not request: 
                    break
                request = connectionSocket.recv(2048)
                data+=request
        except:
            pass
        connectionSocket.settimeout(0)
        request = data.decode("utf-8")
        try:
            response,status_code,content = self.__Resource__(request)
            if(type(response)==bytes):
                payload = f"HTTP/1.1 {status_code}\n{content}\n\n".encode() + response
            else:
                payload = f"HTTP/1.1 {status_code}\n{content}\n\n{response}\n".encode()
            connectionSocket.sendall(payload)
            connectionSocket.close()
        except:
            pass