'''
19 December 2018
'''

import sys
import time
from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname
import threading 
import pygame           # run "python -m pip install pygame" from command line (windows)
import pygame.freetype  # Import the freetype module.

def listener():
    # listen for peer acknowledgement then listen for messages
    listenAck()
    time.sleep(1)
    listening()

def listenAck():
    # listen for first message from peer; once recieved set the peer name
    global ack, mySocket, DST, dstPort, myname, othername, chatLog
    chatLog.append("Waiting to Connect...")
    while not ack:
        data = ""
        data = mySocket.recvfrom(size)[0]
        if len(data) > 0:
            othername = data.decode()
            chatLog.append("Connected With: " + othername)  
            mySocket.sendto(myname.encode(),(DST,dstPort)) 
            ack = True
            
def listening():
    # listen for peer messages
    global ack, done, mySocket, DST, dstPort, myname, othername, chatLog
    chatLog.append("Communication Established")
    
    while not done:
        data = ""
        data = mySocket.recvfrom(size)[0]
        if len(data.decode()) > 4:
            if data.decode()[:4] == "True":
                chatLog.append(othername + ": " +data.decode()[4:])
                
def sender():
    # get ack confirmed before sending messages
    senderAck()
    time.sleep(1)
    sending()
            
def senderAck():
    # send my username in intervals until reacted to
    global ack, done, mySocket, DST, dstPort, myname, othername, chatLog
    while not ack:
        mySocket.sendto(myname.encode(),(DST,dstPort)) 
        time.sleep(1)            
            
def sending():
    # send my message if it isn't empty
    global ack, done, mySocket, DST, dstPort, myname, othername, chatLog, sendMsg
    while not done:
        msg = sendMsg
        if len(msg) > 0:
            mySocket.sendto((str(ack) + msg).encode(),(DST,dstPort)) 
        
            chatLog.append(myname + ": " + msg)
            sendMsg = ""
            #print(myname + ": " + msg)
            
def display():
    # This method has the main loop for displaying the chat state
    global chatLog, sendMsg, nameSet, myname
    
    pygame.init()
    width = 800
    height = 600
    screen = pygame.display.set_mode((width, height))
 
    # I don't know the difference in these two, but if I sub them out it breaks
    msgFont = pygame.freetype.SysFont(None, 24)
    font = pygame.font.Font(None, 24)
    
    # self explananatory
    clock = pygame.time.Clock()
    inputBox = pygame.Rect(50, 550, 700, 24)
    colorInactive = pygame.Color('lightskyblue3')
    colorActive = pygame.Color('dodgerblue2')
    color = colorInactive 
    
    text = '' # input message
    if not nameSet:
        text = "Enter a name: "
    
    remaining = 50 # chars remaining in input
    active = False # name set
    running =  True
   
    # main display loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
                print("Session Ended")
                #mySocket.sendto("done".encode(),(DST,dstPort)) 
                
            # mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the inputBox rect.
                if inputBox.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = True
                else:
                    active = False
                # Change the current color of the input box.
                color = colorActive if active else colorInactive
                
            # key presses
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        # take input as name, send to peer
                        if not nameSet:
                            if len(text) > len("Enter a name: "):
                                myname = text[len("Enter a name: "):]
                                nameSet = True
                                chatLog.append("Welcome: " + myname)
                                text = ""
                        else:
                            sendMsg = text
                            text = ''
                        remaining = 50
                    elif event.key == pygame.K_BACKSPACE:
                        if text != "Enter a name: ":
                            text = text[:-1]
                            if remaining < 50:
                                remaining += 1
                    else:
                        if len(text) < 50:
                            text += event.unicode
                            remaining -= 1
        
        #initial message height
        y = 30
        # delete old logs to make space on screen
        if len(chatLog) > int((height-100) / 24):
            chatLog.remove(chatLog[0])
            
        screen.fill((255,255,255))
        
        # print the logs
        msgColor = (0, 0, 0)
        for i in chatLog:
            
            # my messages blue
            if myname in i[:len(myname)+2] and len(myname) > 0:
                msgColor = (0,0,255)
                msgFont.render_to(screen, (50, y), i, msgColor)
            # their messages are red
            elif othername in i[:len(othername)+2] and len(othername) > 0:
                msgColor = (255, 0, 0)
                msgFont.render_to(screen, (50, y), i, msgColor)
            # Sys messages are black
            else:
                msgColor = (0, 0, 0)
                msgFont.render_to(screen, (50, y), i, msgColor)
            
            # increase message position
            y += 24
         
        # render remaining character counter
        msgFont.render_to(screen, (50, height - 75), f"Remaining: {remaining}", (0, 0, 0))
        
        # Render the current unsent msg.
        txtSurface = font.render(text, True, color)

        # Blit the text.
        screen.blit(txtSurface, (inputBox.x+5, inputBox.y+5))
        # Blit the inputBox rect.
        pygame.draw.rect(screen, color, inputBox, 2)

        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()  
    
'''
establish sockets
'''

# SRC info
srcPort = input("Please enter source port")    

# DST info
DST = input("Please enter destination IP")  
dstPort = input("Please enter destination port")     
size = 1024

# Build Server 
SRC = gethostbyname( '0.0.0.0' )
mySocket = socket( AF_INET, SOCK_DGRAM )
mySocket.bind((SRC, srcPort))

'''
Begin main loop
'''
sendMsg = ""
chatLog = ["Welcome to P2PMessage"]
nameSet = False 
 
myname = ""
#print("waiting to connect")
othername = ""

# Client logic
ack = False # used to establish the link
done = False # used in main communication loop

t3 = threading.Thread(target = display) 
t1 = threading.Thread(target = listener) 
t2 = threading.Thread(target = sender)


t3.start()
# get the name input before begin sending packets
while not nameSet:
    time.sleep(1)
    
t1.start() 
t2.start() 

# I don't know what join means but I think I need it
t3.join() 
t1.join()  
t2.join() 



