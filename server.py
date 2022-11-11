from base64 import encode
from email import message
import base64
import os
import socket
from statistics import mode
import time
from numpy import result_type 

def send_encryp(text):          #encrypts the text, adds header and sends to the client

    if (mode_encryption == 1):
        text= encrypt_cipher(text, shift_cipher)
    if (mode_encryption == 2):
        text= transpose(text)
           
    if (type(text) is not bytes):
        msg = str(mode_encryption) + text 
        c.send(msg.encode()) 
    else:
        c.send(str(mode_encryption).encode() + text)  

def encrypt_cipher(text, shift):        #shifts the alphanumeric characters by the offset of ascii value = shift
    
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

def transpose(text):            #reverses the text in word by word manner

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
         

 

mode_encryption = 0         #by default, mode of encryption is plain text
shift_cipher = 2            #offset value for the caeser cipher 
  

PORT = 50345                                            # The server will receive/send packets through this port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #The network uses TCP protocol at the trasport layer

print('[SERVER]: Socket successfully created') 


# s.bind(('10.0.0.1', PORT))  #mininet
s.bind(('10.0.2.15', PORT)) 

print("[SERVER]: socket binded to %s"  %(PORT)) 

s.listen()
# print(f'listening at {SERVER}')

c, addr = s.accept()    #c is the socket object of the client, addr is it's address
print ("[SERVER]: got connected to", addr) 
first_msg = "[SERVER]: HELLO! Please enter the commands below" 
c.send(first_msg.encode()) 
while True:
    
    combined_job = c.recv(1024).decode()   
    mode_encryption = int(combined_job[0] )     #header contains the mode of encryption
    # print(mode_encryption)
    header_end = 1
    
    
    job = combined_job[header_end:]             #remove the header
    #Decrypt the job/request
    if (mode_encryption == 1):
        job = encrypt_cipher(job, -1*shift_cipher) 
    if (mode_encryption == 2):
        
        job = transpose(job) 
        
    
    print("[CLIENT] ", job)
    
    if (job == "BYE"):          #command that terminates the communication
        print("BYE")
        break  
    

    elif (job == "CWD"):       #sends the current working directory to the client
        res = os.getcwd() 
        
        send_encryp(res)
        
        print("[SERVER] Service Provided") 

    elif (job == "LS"):         #sends the list of all files in the working directory as a string
        res = ' '.join(os.listdir())  
        
        send_encryp(res)
        
        print("[SERVER] Service Provided")  

    elif (job[0:2] == "CD"):    #changes the directory
        dir = ""
        for i in range(3, len(job)):
            dir += job[i]
        dir_exist = os.path.exists(dir) 
        if (dir_exist):        #if the directory exists, go to it
            os.chdir(dir) 
            confirmation = "OK" 
        else:
            confirmation = "NOK"    #directory does not exist, respond by NOK
     
        send_encryp(confirmation)
        # c.send(confirmation.encode())
        print(os.getcwd())
        print("[SERVER] Service Provided") 

    elif (job[0:3] == "UPD"):  
        send_encryp("send status")
        check_h = c.recv(1024).decode() 
        mode_encryption = int(check_h[0])   #decodes the header
        check = check_h[1:]
        # print(check)
        if (mode_encryption == 1):
            check = encrypt_cipher(check, -1*shift_cipher) 
        if (mode_encryption == 2):
            check= transpose(check)  
        # print(check)
        # begin = time.time()
        if (check == "file is there"):  #if file exists, continue the upload 
            send_encryp("size_rec")
            filename_base = os.path.basename(job[4:]) 
            #name of the file that will get uploaded to the server 
            filename = filename_base[:len(filename_base)-4] + "_from_CLIENT." +  filename_base[len(filename_base)-3:]
            #write into the file as bytes
            file = open(filename, "wb")   
            rem_size_h = c.recv(1024).decode()
            
            mode_encryption = int(rem_size_h[0])
            rem_size = rem_size_h[1:]
            if (mode_encryption == 1):
                    rem_size = encrypt_cipher(rem_size, -1*shift_cipher) 
            if (mode_encryption == 2):
                rem_size= transpose(rem_size)
            rem_size = int(rem_size)
            send_encryp("size received")
            #the loop will run until whole data of the uploading file is received
            begin = time.time()
            while rem_size>=0:
                content_h = c.recv(2054)        #2048 bytes of file data + extra data(accounting for the header)
        
                mode_encryption = content_h[0] - 48 
                content = content_h[1:]
                
                if (mode_encryption == 1):
                    content = encrypt_cipher(content, -1*shift_cipher) 
                if (mode_encryption == 2):
                    content= transpose(content) 
                
                    
                file.write(content) 
                send_encryp("DONE")
                rem_size -= 2048  #2048 bytes of the file data is received in each message
            end = time.time()
        
                    
            c.recv(1024)            
            file.close()
            print(filename) 
            print(f"Upload Time is {end - begin}")
        
        
            confirmation = f"STATUS : OK, file uploaded successfully. Upload time is {end - begin}" 
        else:
            confirmation = "STATUS : NOK, file upload fail"
        # end = time.time()
        send_encryp(confirmation)
        print("[SERVER] Service Provided") 
        


    elif (job[0:3] == "DWD"):
        
        file_name = job[4:] 
        file_exist = os.path.exists(job[4:]) 
        #download is only possible if the file exists
        if (file_exist):
            send_encryp("file is there")
            c.recv(1024)
            file= open(file_name, "rb")    #read the file content in bytes
             
            
            filesize = os.path.getsize(file_name)  
            rem_size = filesize   
            send_encryp(str(rem_size))
            c.recv(1024)
            start = time.time()
            while rem_size>=0: 
                content = file.read(2048) #each chunk of data is of 2048 bytes
            
                send_encryp(content)
                c.recv(2048)
                
                
                rem_size -= 2048


            file.close()
            end = time.time() 
            print(f"Download time is {end - start}")
            confirmation = f"STATUS : OK, file downloaded successfully. Download time is {end - start}" 
        else: 
            send_encryp("NO FILE")
            c.recv(1024)
            confirmation = "STATUS : NOK, file download fail"
                           
        send_encryp(confirmation)
        print("[SERVER] STATUS OK, Service Provided") 
        
        

    else:
        send_encryp("NOT a valid command")
        print("[SERVER] STATUS OK, Service Provided") 


s.close()       #close the socket connection

    






