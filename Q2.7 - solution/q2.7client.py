#   Heights sockets Ex. 2.7 template - client side
#   Author: Aharon S. 2019

import os
import socket
AVAILABLE_COMMANDS = ('TAKE_SCREEN_SHOT', 'SEND_FILE', 'DIR', 'DELETE', 'COPY', 'EXECUTE', 'EXIT')
#  Amount of bits per query to server, or response from server:
AMOUNT_OF_BITS = 99
#  the client's host name (The first part of the socket)
IP = '127.0.0.1'
PORT = 8820


def valid_request(request):
    """Check if the request is valid (is included in the available commands)
    Return:
        True if valid, False if not
    """
    if request in AVAILABLE_COMMANDS:
        return True
    else:
        print("'" + request + "' is not recognized as an internal or external command")
        return False


def input_path(request):
    """ According to the client's query, we will request the path

    :param request:
        The main command
    :return:
        The path
    """
    path = ""
    if request == 'TAKE_SCREEN_SHOT':
        while True:
            #  The path on the client's computer:
            path = input('In which folder do you want us to save the photo to?\nfor example  "C:\\Cyber" \n')
            if not os.path.exists(path):
                print("'" + path + "' is not exists in your PC, Pleas try again")
            else:
                break
    elif request == 'SEND_FILE':
        #  The path on the server's computer:
        path = input('Enter the path to the file name _for example_ "C:\\Cyber\\screen_shot.jpg"\n')
        #  The path on the client's computer:
        while True:
            client_path = input('In which folder do you want us to save the photo to?\n'
                                'for example  "C:\\Cyber"\n')
            if not os.path.exists(client_path):
                print("'" + client_path + "' is not exists in your PC, Pleas try again")
            else:
                break
        path = path + ' ' + client_path
    elif request == 'DIR':
        #  The path on the server's computer:
        path = input('What is the folder name? _for example_ C:\\Cyber\n')
    elif request == 'DELETE':
        #  The path on the server's computer:
        path = input('What is the file name to DELETE? _for example_ "C:\\Cyber\\screen_shot.jpg"\n')
    elif request == 'COPY':
        #  The path on the server's computer:
        path = input('What is the name of the original file? _for example_ "C:\\Cyber\\screen_shot.jpg"\n')
        #  The path on the server's computer:
        path = path + ' ' + input('In which folder do you want us to save the COPY file ? '
                                  '_for example_ "C:\\Cyber\\screen_shot_copy.jpg" \n')
    elif request == 'EXECUTE':
        #  The path on the server's computer:
        path = input('What software would you like me to run? _for example_ notepad++.exe\n')
    elif request == 'EXIT':
        path = 'EXIT'
    return path


def send_request_to_server(my_socket, request):
    """Send the request to the server. First the length of the request (2 digits), then the request itself
    Args:
        new-request a string who include the 'path' and the 'length' of the request
    Example: '04EXIT'
    Example: '12DIR c:\cyber'
    """
    new_request = ""
    path = input_path(request)
    # if size of all the request < 10...
    if (len(request) + len(str(path)) + 1) < 10:
        new_request = '0' + str(len(request) + len(str(path)) + 1) + request + ' ' + path
    # if size of all the request < max bits (AMOUNT_OF_BITS)...
    elif (len(request) + len(str(path)) + 1) < AMOUNT_OF_BITS:
        new_request = str(len(request) + len(str(path)) + 1) + request + ' ' + path
    # if size of all the request > max bits (AMOUNT_OF_BITS)...
    elif (len(request) + len(str(path)) + 1) > AMOUNT_OF_BITS:
        print("'" + request + "' is not recognized as an internal or external command")
        new_request = 'The request has too many bits'
    my_socket.send(new_request.encode())


def handle_server_response(my_socket, request):
    """Receive the response from the server and handle it, according to the request

    For example, DIR should result in printing the contents to the screen,
    while SEND_FILE should result in saving the received file and notifying the user
    """
    if request == 'SEND_FILE':
        name_file = my_socket.recv(100).decode()
        temp = name_file
        temp = temp.split()
        temp = temp[0]
        temp = ''.join(temp)
        if not temp.isdigit():
            message = name_file
            print(message)
        else:
            try:
                tmp = name_file
                tmp = tmp.split()
                size = tmp[0]
                size = ''.join(size)
                size = int(size)
                tmp = tmp[3]
                tmp = ''.join(tmp)
                tmp = tmp + '\\screen_shot_SEND_FILE.jpg'
                index = AMOUNT_OF_BITS
                with open(tmp, 'wb') as f:
                    while True:
                        if size - AMOUNT_OF_BITS > 0:
                            data = my_socket.recv(index)
                            f.write(data)
                            size -= AMOUNT_OF_BITS
                        else:
                            index = size
                            data = my_socket.recv(index)
                            f.write(data)
                            print('Done successfully')
                            break
            except Exception as e:
                print(str(e).encode())
    else:
        data = my_socket.recv(1024)
        print(data.decode())


def main():
    # open socket with the server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    # print instructions
    print('\nWelcome to remote computer application. Available commands are:')
    print('{TAKE_SCREEN_SHOT, SEND_FILE, DIR, DELETE, COPY, EXECUTE, EXIT}')

    done = False
    # loop until user requested to exit
    while not done:
        request = input("Please enter command:\n").upper()
        if valid_request(request):
            send_request_to_server(my_socket, request)
            handle_server_response(my_socket, request)
            if request == 'EXIT':
                done = True
    my_socket.close()


if __name__ == '__main__':
    main()
