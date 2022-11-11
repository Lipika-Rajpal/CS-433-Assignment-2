from base64 import encode 
import base64 
import socket    
import os  
import time

def send_encryp(text):   #encrypts the text, adds header and sends to the client

    if (mode_encryption == 1):
        text= encrypt_cipher(text, shift_cipher)
    if (mode_encryption == 2):
        text= transpose(text)
           
    if (type(text) is not bytes):
        msg = str(mode_encryption) + text 
        s.send(msg.encode()) 
    else:
        s.send(str(mode_encryption).encode() + text)  

    
def encrypt_cipher(text, shift):  #shifts the alphanumeric characters by the offset of ascii value = shift
    
    
    if (type(text) is bytes):
        text = list(text) 
        for i in range(0, len(text)):
            text[i] = (text[i] + shift)%256  
        return bytes(text) 
    result = "" 
    for i in text:
        
        if (i.isdigit()):
            result += chr((ord(i) + shift - 48)%10 + 48)
        
        elif (i.isupper()):
            result += chr((ord(i) + shift-65) % 26 + 65)
  
        elif (i.islower()):
            result += chr((ord(i) + shift - 97) % 26 + 97)
        else:
            result += i  
    
    return result  

def transpose(text):    #reverses the text in word by word manner


    if (type(text) is bytes):
        text = list(text) 
       
        text.reverse()
        return bytes(text)
   
    lines = text.splitlines() 
    encrypted_lines = []
    for line in lines:
        result = "" 
        words = line.split() 
        for word in words:
            result += " "
            result += word[::-1]  
        encrypted_lines.append(result[1:]) 

    return '\n'.join(encrypted_lines)
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       #using TCP as the transport layer protocol 
 

port = 50345       #the port at which it will communicate with the server        
 

# s.connect(('10.0.0.1', port))      #connect the server with the port   (mininet)
s.connect(('10.0.2.15', port))      #connect the server with the port
# s.connect(('127.0.0.1', port)) 

print ("[SERVER] :", s.recv(1024).decode())  
mode_encryption = 0
shift_cipher = 2
while True:
    comm = input("Enter the command :")  
        
    
    if (comm[0:4] == "MODE"):       #client can change the mode of encryption
        mode_encryption = int(comm[5])  
        
        continue

    send_encryp(comm)
    if (comm== "BYE"):
        print("BYE")
        break   
    if (comm[0:3] == "UPD"):
        file_name = comm[4:] 
        file_basename = os.path.basename(file_name)    
        file_exist = os.path.exists(comm[4:])   #checking if the file exists
        s.recv(1024)
        # begin = time.time()
        if (file_exist):  
            m = "file is there"
            
            send_encryp(m)
            s.recv(1024)
            file= open(file_name, "rb")    #read the contents as bytes
            filesize = os.path.getsize(file_name)  
            rem_size = filesize 
            m1 = str(rem_size) 
          
            send_encryp(str(rem_size))   #send the file size to the server
            s.recv(1024)
            content = file.read(2048)     #read the file as chunks of 2048 bytes
     
            while rem_size>=0:          #loop runs until the file is read completely
                send_encryp(content) 
                s.recv(1024)
                content = file.read(2048) 
                
                rem_size -= 2048
               


            file.close()
            send_encryp("file closed")
            
        else: 
            # send_encryp("FAIL")
            m = "FAIL"     #as the file does not exist
           
            send_encryp(m)
        # end = time.time() 
        # print(f"[INFO] Upload time is {end - begin}")
    if (comm[0:3] == "DWD"):
         
        check_h = s.recv(1024).decode() 
        mode_encryption = int(check_h[0]) 
        check = check_h[1:]
        # print(check)
        if (mode_encryption == 1):
            check = encrypt_cipher(check, -1*shift_cipher) #for decryption, just shift the characters with a negative offset
        if (mode_encryption == 2):
            check= transpose(check)  
        # begin = time.time() 
        if (check == "file is there"): 
            send_encryp("ok")
            filename_base = os.path.basename(comm[4:]) 
            #name of the file when it will be downloaded in the client directory
            filename = filename_base[:len(filename_base)-4] + "_from_SERVER." +   filename_base[len(filename_base)-3:]
            
            file_exist = os.path.exists(comm[4:]) 
            # if (file_exist):

            file = open(filename, "wb")    #contents will be written in bytes
            
            # filesize = os.path.getsize(comm[4:])  
            rem_size_h = s.recv(1024).decode() 
            mode_encryption = int(rem_size_h[0])
            rem_size = rem_size_h[1:]
            if (mode_encryption == 1):
                    rem_size = encrypt_cipher(rem_size, -1*shift_cipher) 
            if (mode_encryption == 2):
                rem_size= transpose(rem_size)
            rem_size = int(rem_size)    #receives the file size from the server
            send_encryp("size rec")
            while rem_size>=0:
                content_h = s.recv(2054)  #2048 bytes for the file data chunk + extra data (for the header)
                mode_encryption = content_h[0]-48 
                content = content_h[1:]
                
                if (mode_encryption == 1):
                    content = encrypt_cipher(content, -1*shift_cipher) 
                if (mode_encryption == 2):
                    content= transpose(content) 
                
                    
                file.write(content) 
                send_encryp("DONE") #sends confirmation to the server
                rem_size -= 2048  
               
                
            file.close()
            print(filename) 
        else:
            send_encryp("NOK")
        # end = time.time() 
        # print(f"[INFO] Download time is {end - begin}")



    print("[SERVER] :")   #confirmation message by the server at the end of a service
    end_comm_h = s.recv(1024).decode()
    mode_encryption = int(end_comm_h[0]) 
    end_comm = end_comm_h[1:]
    if (mode_encryption == 1):
        end_comm = encrypt_cipher(end_comm, -1*shift_cipher) 
    if (mode_encryption == 2):
            end_comm = transpose(end_comm)
    print(end_comm) 
    continue
    

s.close()  
