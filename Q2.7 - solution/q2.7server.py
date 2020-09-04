#   Heights sockets Ex. 2.7 template - server side
#   Author: Aharon S. 2017
import glob
import os
import shutil
import socket
import subprocess
from PIL import ImageGrab

AVAILABLE_COMMANDS = ('TAKE_SCREEN_SHOT', 'SEND_FILE', 'DIR', 'DELETE', 'COPY', 'EXECUTE', 'EXIT')
#  Amount of bits per query to server, or response from server:
AMOUNT_OF_BITS = 99
PORT = 8820
IP = '0.0.0.0'


def receive_client_request(client_socket):
    """Receives the full message sent by the client

    Works with the protocol defined in the client's "send_request_to_server" function

    Returns:
        command: such as DIR, EXIT, SCREEN_SHOT etc
        params: the parameters of the command

    Example: 12DIR c:\\cyber as input will result in command = 'DIR', params = 'c:\\cyber'
    """
    data = client_socket.recv(100)
    temp_data = data.decode()
    #  if size of all the request > max bits (AMOUNT_OF_BITS)...
    if temp_data == 'return nothing':
        return 'return nothing', 'None'
    else:
        temp_data = temp_data.split()
        # size_of_messeg = temp[0][0:2]
        command = temp_data[0][2:]
        params = temp_data[1:]
        return ''.join(command), ' '.join(params)


def check_client_request(command, params):
    """Check if the params are good.

    For example, the filename to be copied actually exists

    Returns:
        valid: True/False
        error_msg: None if all is OK, otherwise some error message
    """
    #  checking the size of client's request :
    if command == 'The request has too many bits':
        return False, 'The request has too many bits'.encode()
    #  checking the path on the server's computer:
    if command == 'TAKE_SCREEN_SHOT':
        temp_path = params
        temp_path = temp_path.split()
        temp_path = ''.join(temp_path)
        if os.path.exists(temp_path):
            return True, None
        else:
            message = "'" + temp_path + "' on the server's computer"
            return False, message.encode()
    if command == 'EXECUTE':
        return True, None
    #  checking the path on the server's computer:
    elif command == 'SEND_FILE' or command == 'DIR' or command == 'DELETE':
        temp_path = params
        if params != '' and params != ' ':
            temp_path = temp_path.split()
            temp_path = ''.join(temp_path[0])
        if os.path.exists(temp_path):
            return True, None
        else:
            message = "'" + temp_path + r"' on the server's computer, not found"
            return False, message.encode()
    elif command == 'COPY':
        temp_path = params
        if params != '' and params != ' ':
            temp_path = temp_path.split()
            temp_path = ''.join(temp_path[0])
        if os.path.exists(temp_path):
            return True, None
        else:
            message = "'" + temp_path + "' on the server's computer not found"
            return False, message.encode()
    elif command == 'EXIT':
        return False, 'Thank you for using remote computer application'.encode()
    else:
        message = "'" + command + "' is not recognized as an internal or external command"
        return False, message.encode()


def handle_client_request(command, params):
    """Create the response to the client, given the command is legal and params are OK

    For example, return the list of filenames in a directory

    Returns:
        response: the requested data
    """
    if command == 'TAKE_SCREEN_SHOT':
        try:
            snapshot = ImageGrab.grab()
            save_path = params + '\\screen_shot.jpg'
            snapshot.save(save_path)
            snapshot.show()
            message = 'screen_shot successfully done, saved on ' + save_path
            return message.encode()
        except Exception as e:
            return str(e).encode()
    elif command == 'SEND_FILE':
        new_params = command + ' ' + params
        return new_params
    elif command == 'DIR':
        try:
            params = params + r'\*.*'
            files_list = glob.glob(params)
            return str(files_list).encode()
        except Exception as err_DIR:
            return str(err_DIR).encode()
    elif command == 'DELETE':
        try:
            os.remove(params)
            return 'The file was successfully deleted'.encode()
        except Exception as err_DELETE:
            return str(err_DELETE).encode()
    elif command == 'COPY':
        try:
            file_copy = str(params)
            file_copy = file_copy.split()
            file_past = file_copy[1]
            file_copy = file_copy[0]
            shutil.copy(file_copy, file_past)
            return 'The file was successfully copied'.encode()
        except Exception as err_COPY:
            return str(err_COPY).encode()
    elif command == 'EXECUTE':
        try:
            subprocess.call(params)
            return 'The program successfully opened'.encode()
        except Exception as err_EXECUTE:
            return str(err_EXECUTE).encode()
    elif command == 'EXIT':
        return str(command).encode()


def send_response_to_client(response, client_socket):
    """Create a protocol which sends the response to the client

    The protocol should be able to handle short responses as well as files
    (for example when needed to send the screenshot to the client)
    """
    if response == 'EXIT':
        client_socket.send(response.encode())
    else:
        temp_response = response
        temp_response = temp_response.split()
        if temp_response[0] == 'SEND_FILE':
            #  name of file exist
            temp_response = temp_response[1]
            temp_response = ''.join(temp_response)
            try:
                with open(temp_response, 'rb') as f:
                    contents = f.read()
                #  amount of bits in the file
                amount_of_bits = str(len(contents))
                message = amount_of_bits + ' ' + str(response)
                amount_of_bits = int(amount_of_bits)
                client_socket.send(message.encode())
                index = AMOUNT_OF_BITS
                with open(temp_response, 'rb') as f:
                    while True:
                        if amount_of_bits - AMOUNT_OF_BITS > 0:
                            contents = f.read(index)
                            client_socket.send(contents)
                            amount_of_bits -= AMOUNT_OF_BITS
                        else:
                            index = amount_of_bits
                            contents = f.read(index)
                            client_socket.send(contents)
                            break
            except Exception as err_SEND_FILE:
                client_socket.send(str(err_SEND_FILE).encode())
        else:
            client_socket.send(response)


def main():
    # open socket with client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()

    # handle requests until user asks to exit
    done = False
    while not done:
        command, params = receive_client_request(client_socket)
        valid, error_msg = check_client_request(command, params)
        if valid:
            response = handle_client_request(command, params)
            send_response_to_client(response, client_socket)
        else:
            send_response_to_client(error_msg, client_socket)

        if command == 'EXIT':
            done = True

    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    main()
