from socket import socket, error, AF_INET, SOCK_STREAM
from threading import Thread
import json, os

def create_board():
    return [[' ' for _ in range(3)] for _ in range(3)]

def order_move(player):
    file_path = "order_status.txt"

    if not os.path.isfile(file_path):
        # Dosya yoksa, varsayılan sıra durumuyla oluşturun
        with open(file_path, "w") as file:
            file.write("X")

    with open(file_path, "r") as file:
        order_status = file.read().strip()

    if player == order_status:
        if player == "X":
            order_status = "O"
        else:
            order_status = "X"
        with open(file_path, "w") as file:
            file.write(order_status)
        return True
    else:
        return False
    
def make_move(board, row, col, player):
    board[row][col] = player

def print_board(board):
    print("#=============#")
    for row in board:
        print(row)

def board_full(client, board):
    for row in board:
        if ' ' in row:
            return False
    return True

def send_move(player, index):
    for client in clients:
        data = {"type": "move", "move":False if player == client["name"] else True, "player": player, "index": index}
        json_data = json.dumps(data)
        client["socket"].sendall(json_data.encode("utf-8"))

def send_result(player="draw"):
    for client in clients:
        if player == "draw":
            data = {"type": "result", "result": "draw"}
            json_data = json.dumps(data)
            client["socket"].send(json_data.encode())
        elif player != client["name"]:
            data = {"type": "result", "result": "lose", "player": player}
            json_data = json.dumps(data)
            client["socket"].send(json_data.encode())
        else:
            data = {"type": "result", "result": "win", "player": player}
            json_data = json.dumps(data)
            client["socket"].send(json_data.encode())

def play_game(client, data):

    if order_move(client["name"]) and data["type"] == "move":
        row, col = data["move"]
        make_move(board, int(row), int(col), client["name"])
        send_move(client["name"], data["index"])
        print_board(board)

        if checkWin(client, board, row, col):
            send_result(client["name"])
        if board_full(client, board):
            send_result()

def checkWin(client, board, row, col):
    symbol = client["name"]
    # Check row
    if board[row][0] == board[row][1] == board[row][2] == symbol:
        return True
    # Check column
    if board[0][col] == board[1][col] == board[2][col] == symbol:
        return True
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == symbol:
        return True
    if board[0][2] == board[1][1] == board[2][0] == symbol:
        return True
    return False

def close_client(client_socket):
    for client in clients:
        if client["socket"] == client_socket:
            if client["name"] == "X" and len(clients) == 2:
                clients.remove(clients[1])
            clients.remove(client)
            client["socket"].close()
            break

def handle_commands():
    while True:
        command = input()
        if command == "quit":
            for client in clients:
                close_client(client["socket"])
            # Sunucuyu kapatmak için 'quit' komutunu kullanabilirsiniz
            server_socket.close()
            break

        elif command == "clients":
            if len(clients) == 0:
                print([])
                continue
            for client in clients:
                print(client)
        else:
            pass

def receive_data(client):
    while True:
        try:
            data = client["socket"].recv(1024).decode()

            if not data:
                print("boş data")
                break #Sunucu ile bağlantı kesilir

            data = json.loads(data)

            if data["where"] == "server":
                if data["type"] == "quit":
                    close_client(client["socket"])
            
            elif data["where"] == "game":
                play_game(client, data)
        
        except Exception as a:
            print(a)
            break

    close_client(client["socket"])



if __name__ == "__main__":
    host = "127.0.0.1"
    port = 57070

    server_socket = socket(AF_INET, SOCK_STREAM)

    server_socket.bind((host, port))
    server_socket.listen(2)

    print(f"Sunucu {host}:{port} adresinde dinleniyor...")

    command_thread = Thread(target=handle_commands)
    command_thread.start()

    clients = []
    while True:
        try:
            client_socket, client_address = server_socket.accept()

            if len(clients) >= 2:
                close_client(client["socket"])
                print(f"Başarısız bağlantı {client_address}")
                continue
            
            client_socket.sendall("connect".encode("utf-8"))
            print(f"Başarılı bağlantı {client_address}")

            client = {"name": "O" if len(clients) != 0 else "X", "socket": client_socket, "address": client_address}
            clients.append(client)

            client_thread = Thread(target=receive_data, args=(client,))
            client_thread.start()


            if len(clients) == 2:
                board = create_board()
                with open("order_status.txt", "w") as file:
                    file.write("X")
                for client in clients:
                    data = {"type": "start", "turn": True if client["name"] == "X" else False}
                    json_data = json.dumps(data)
                    client["socket"].send(json_data.encode())
                print("Start Game")
        except OSError:
            print("Sunucu zorla kapatıldı")
            break
    
    server_socket.close()