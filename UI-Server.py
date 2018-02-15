import sys
import socket
import threading
import select
import string
	
def broadcast (sock, message, usr):
    try:
        for socket in CLIST:
            if socket != server_socket and socket != sock:
                print('FROM: ', usr)
                print('MESSAGE: ' , message)
                print('INFO: Broadcasting...\n')
                socket.send(message)
    except:
        print('ERROR: Broadcast error - perhaps a client disconnected?')

if __name__ == "__main__":

    CLIST = []
    People = []
    
    print('INFO: Chat server - BETA')
    # port = str(input("Enter IP to bind server: "))
    port = '0.0.0.0'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((port, 6666))
    server_socket.listen(10)
 
    CLIST.append(server_socket)   # Add socket

    while 1:
        # Get list of ready to be read with select
        read_sockets, write_sockets, error_sockets = select.select(CLIST, [], [])

        for sock in read_sockets:

            if sock == server_socket: 
                sockfd, addr = server_socket.accept()   # New connection recieved 
                CLIST.append(sockfd)                    # Append the new connection
                print("STATUS: Client [%s, %s] connected" % addr)
                #broadcast(sockfd, "New client connected ",addr)

            else:
                try:
                    data = sock.recv(4096, )            # Data recieved from client
                except:
                    broadcast(sock, "STATUS: Client [%s, %s] is offline" % addr,
                            addr)
                    print("STATUS: Client [%s, %s] is offline" % addr)
                    sock.close()
                    CLIST.remove(sock)
                    continue

                if data:                                # Client send data
                    if data == "q" or data == "Q":      # If client quit
                        #broadcast(sock, "Client (%s, %s) quit" % addr, addr)
                        print("STATUS: Client [%s, %s] quit" % addr)
                        sock.close()                    # Close socket
                        CLIST.remove(sock)              # Remove from our list
                    #elif "$$$" in data.decode():
                        #THIS_NAME = data.strip(b'$$$')
                        #People.append(THIS_NAME)
                        #for socket in CLIST:
                            #if socket != server_socket and socket != sock:
                                #print(People)
                                #for person in People:
                                    #socket.send(person)
                                    #socket.send(b' | ')
                    else:
                        broadcast(sock, data, addr)                  
                
    server_socket.close()    
