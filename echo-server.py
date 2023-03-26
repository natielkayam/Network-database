# python ./echo-server.py 127.0.0.1:8081 127.0.0.1:8080 127.0.0.1 8082
# python ./echo-server.py 127.0.0.1:8080 127.0.0.1:8081 127.0.0.1 8082
# python ./echo-server.py 127.0.0.1:8082 127.0.0.1:8081 127.0.0.1 8080


import socket
import sys
import threading
import traceback
import json


#dic data strcture to store things

class State(object):

    def __init__(self, args):
        self.host = self._parseHost(args[0]) 
        self.siblings = [self._parseHost(x) for x in args[1:]]
        self.connections = {}
        self.d = {}
        #Init gets args from command:
        #host = ip,port
        #sibilings = send to - ip,port
        #connections = num of connections 

    def siblingFile(self, sibling):
        bool = False
        (con, f) = self.connections.get(sibling, (None, None))
        if con is None or con.fileno() == -1:
            try:
                con = socket.create_connection(sibling)
                f = con.makefile(mode='rw', encoding='utf-8')
                f.write('sibling\n')
                self.connections[sibling] = (con, f)
                bool = True
            except:
                return None
        if(bool):
            f.write(json.dumps(self.d))
            f.write('\n')
            f.flush()  
        return f 
  

    def _parseHost(self, hostAndPort):
        parts = hostAndPort.split(':')
        host = parts[0]
        port = int(parts[1])
        return (host, port)
        #host = ip,port

    def client(self, cmd, f):
        
        #TODO:
        #chaeck wether is set or get 
        #create data structh 
        #if its get not need to store the data
        if(cmd[0:1] == "{" and len(self.d) < len(json.loads(cmd))):
            self.d = json.loads(cmd)
        print('Got command: ', cmd)
        l = cmd.rstrip('\n\r \t').split(" ")
        #l[1] = key, l[2:] = value
        if(l[0] != "get" and l[0] != "set"): 
            f.write("Error - only get,set allowed")
            f.write('\n')
            f.flush()
            return

        if(l[0] == "get"):
            
            if(l[1] in self.d):
                f.write(self.d[l[1]])
                f.write('\n')
                f.flush()
            else:
                f.write('No value for this key')
                f.write('\n')
                f.flush()
                

        if(l[0] == "set"):
            #create dic 
            self.d[l[1]]=' '.join(l[2:])

            for sibling in self.siblings:
                try:
                    con = self.siblingFile(sibling)
                    if(con != None):
                        con.write(json.dumps(self.d))
                        con.write('\n')
                        con.flush()
                        response = con.readline()
                        if(cmd !=''):
                            if response.rsplit('\r\n \t') != 'processed':
                                raise "wrong response from server"
                        if(cmd == ''):
                            print("hey " , len(self.d))
                            self.d = json.loads(response)
                            print("Got it", len(self.d))
                except:
                 self.connections.pop(sibling)   


        
    def sibling(self, cmd, f):
        print("From Sibling: ", cmd)
        print(len(self.d))
        if(cmd.rsplit('\r\n \t') != '' and cmd[0:1] == "{"):
            if(len(json.loads(cmd)) > len(self.d)):
                self.d = json.loads(cmd)
        if(cmd == ''):
            f.write(json.dumps(self.d))
            f.flush()
            return
        f.write('Processed\n')
        f.flush() #clears the internal buffer of the file

        
    def run(self, s, addr):

        a = ''
        try:
            for c in self.siblings:
               a = self.siblingFile(c)

            with s, s.makefile(mode='rw', encoding='utf-8') as f:
                firstLine = f.readline()
                isSibling = firstLine.rstrip('\n\r \t') == 'sibling'
                print('first line: ', firstLine, isSibling)
                if(firstLine.rstrip('\n\r \t') =='' and a != None):
                   isSibling = True
                
                if not isSibling:
                    self.client(firstLine, f)
                else:
                    print("Got sibling connection from ", addr)

                for line in f:
                    if isSibling:
                        o = self.sibling(line, f)
                        if(o == None):
                            isSibling = False
                    else:
                        self.client(line, f)
        except:
            print('Connection failed with ', addr)
            traceback.print_exc()# traceback - a python libary that can tell where the con fail. 





state = State(sys.argv[1:])
listener = socket.socket() #object of the comunication
listener.bind(state.host) #bind the listner to the adress,port to the host ip
listener.settimeout(1) # don't hang
listener.listen(2)
print("Ready! Listening on ", state.host, "siblings: ", state.siblings)

#when connection succed !!! 
while True:
    try:
        clientSocket, addr = listener.accept()
        print("Accepted request from: ", addr)
        threading.Thread(target=state.run, args=[clientSocket, addr]).start()
        #create a thread of the 


        
    except socket.timeout:
        pass