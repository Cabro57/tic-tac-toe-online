
from PySide6.QtWidgets import QWidget, QApplication, QGridLayout, QPushButton, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from socket import socket, error, AF_INET, SOCK_STREAM, gethostname
from threading import Thread
import sys, json, time, os

class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.parent().resetGame()

class ClickableInfoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)

    def mousePressEvent(self, event):
        if self.text() == "Sunucuya bağlan" or "Tekrar dene" in self.text():
            Thread(target=self.parent().connect_server).start()
            self.setText("bağlanılıyor...")
            
        
        elif self.text() in ["Kaybettin", "Kazandın", "Berabere"]:
            print("bağlanılıyor...")
            Thread(target=self.parent().connect_server).start()
            self.setText("bağlanılıyor...")


class TicTacToe(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.client_socket = None

        #self.initGame()
        file_path = "settings.json"
        if not os.path.isfile(file_path):
            with open(file_path, "w") as file:
                data = {"host": "127.0.0.1", "port": 57070}
                json_data = json.dumps(data)
                file.write(json_data)
            

    def closeEvent(self, event):
        data = {"where": "server", "type": "quit"}
        json_data = json.dumps(data)
        self.client_socket.send(json_data.encode())
        print("closeEvent Gönderdi")
        self.client_socket.close()
        event.accept()
    
    def setupUI(self):
        self.setWindowTitle("XOX")
        self.setMinimumSize(500,600)
        self.setMaximumSize(500,600)
        self.setStyleSheet("""
        QWidget#board_widget {
            background-color: #F36153;
        }
        QWidget#game_body {
            background-color: #F03D2D;
            }
        QWidget#score_widget {
            background-color: white;
            }
        QWidget#o_widget, QWidget#x_widget {
            background-color: white;
            border: 1px solid #70757a;
            border-radius: 6px;
            }
        QLabel {
            font-size: 32px;
            font-weight: bold;
            color: #222222;
        }
        QPushButton {
            background-color: #F36153;
            border: unset;
            font-size: 32px;
            font-weight: bold;
            color: White;
            }
        """)
        
        self.central_layout = QGridLayout(self)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.score_widget = QWidget()
        self.score_widget.setObjectName("score_widget")

        self.score_layout = QHBoxLayout(self.score_widget)
        self.score_layout.setSpacing(5)
        self.score_layout.setContentsMargins(10, 10, 10, 10)

        self.x_widget = QWidget()
        self.x_widget.setObjectName("x_widget")
        
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.x_layout = QHBoxLayout(self.x_widget)

        self.x_name_label = QLabel()
        
        self.x_name_label.setSizePolicy(sizePolicy)
        self.x_name_label.setText("X")

        self.x_layout.addWidget(self.x_name_label)

        self.x_score_label = QLabel()
        self.x_score_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.x_score_label.setText("-")

        self.x_layout.addWidget(self.x_score_label)

        self.score_layout.addWidget(self.x_widget)

        self.o_widget = QWidget()
        self.o_widget.setObjectName("o_widget")

        self.o_layout = QHBoxLayout(self.o_widget)

        self.o_name_label = QLabel()
        self.o_name_label.setSizePolicy(sizePolicy)
        self.o_name_label.setText("O")

        self.o_layout.addWidget(self.o_name_label)

        self.o_score_label = QLabel()
        self.o_score_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.o_score_label.setText("-")

        self.o_layout.addWidget(self.o_score_label)

        self.score_layout.addWidget(self.o_widget)

        self.central_layout.addWidget(self.score_widget, 0, 0)

        self.board_widget = QWidget()
        self.board_widget.setObjectName("board_widget")
        
        self.board_layout = QVBoxLayout(self.board_widget)
        self.board_layout.setContentsMargins(10, 10, 10, 10)

        self.game_body = QWidget()
        self.game_body.setObjectName("game_body")
        
        self.gridLayout = QGridLayout(self.game_body)
        self.gridLayout.setSpacing(15)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.buttons = []
        for row in range(3):
            for col in range(3):
                button = QPushButton()
                button.setSizePolicy(sizePolicy)
                button.clicked.connect(self.buttonClicked)
                self.gridLayout.addWidget(button, row, col)
                self.buttons.append(button)
        
        self.board_layout.addWidget(self.game_body)
            
        self.central_layout.addWidget(self.board_widget, 1, 0)

        self.resultLabel = ClickableLabel(self)
        self.resultLabel.setStyleSheet("QLabel { background-color: rgba(255, 255, 255, 150); padding: 10px; }")
        self.resultLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resultLabel.setVisible(False)

        self.central_layout.addWidget(self.resultLabel, 1, 0)

        self.infoLabel = ClickableInfoLabel(self)
        self.infoLabel.setStyleSheet("QLabel { background-color: rgba(255, 255, 255, 150); padding: 10px; }")
        self.infoLabel.setText("Sunucuya bağlan")
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoLabel.setVisible(True)
        self.infoLabel.setFixedSize(500, 520)

        self.central_layout.addWidget(self.infoLabel, 1, 0)

    def initGame(self, data):


        if data["type"] == "start":

            self.score_widget.setStyleSheet("QWidget#x_widget {border-bottom: 3px solid #F03D2D}")
            self.infoLabel.setText("Oyun başlıyor...")
            time.sleep(1)
            self.resetGame()
            time.sleep(2)
            self.infoLabel.setVisible(False)
        
        elif data["type"] == "info":
            if data[0][1] == "game ready":
                self.infoLabel.setVisible(False)
    
            else:
                self.infoLabel.setText(data[0][1])
        
        elif data["type"] == "move":
            buton = self.buttons[data["index"]]
            buton.setText(data["player"])
            buton.setEnabled(False)
            self.score_widget.setStyleSheet(f"QWidget#{'o' if data['player'] == 'X' else 'x'}_widget" + "{border-bottom: 3px solid #F03D2D}")
        
        elif data["type"] == "result":
            send_data = {"where": "server", "type": "quit"}
            json_data = json.dumps(send_data)
            self.client_socket.send(json_data.encode())

            if data["result"] == "win":
                self.infoLabel.setText("Kazandın")
                self.infoLabel.setVisible(True)
                if data["player"] == "X":
                    try:
                        score = int(self.x_score_label.text()) + 1
                        self.x_score_label.setText(str(score))
                    except ValueError:
                        self.x_score_label.setText("1")
                elif data["player"] == "O":
                    try:
                        score = int(self.o_score_label.text()) + 1
                        self.o_score_label.setText(str(score))
                    except ValueError:
                        self.o_score_label.setText("1")

            elif data["result"] == "draw":
                self.infoLabel.setText("Berabere")
                self.infoLabel.setVisible(True)

            elif data["result"] == "lose":
                self.infoLabel.setText("Kaybettin")
                self.infoLabel.setVisible(True)
                if data["player"] == "X":
                    try:
                        score = int(self.x_score_label.text()) + 1
                        self.x_score_label.setText(str(score))
                    except ValueError:
                        self.x_score_label.setText("1")
                elif data["player"] == "O":
                    try:
                        score = int(self.o_score_label.text()) + 1
                        self.o_score_label.setText(str(score))
                    except ValueError:
                        self.o_score_label.setText("1")


    """def initGame(self):
        self.currentPlayer = "X"
        self.moves = 0
        self.board = [['', '', ''],
                      ['', '', ''],
                      ['', '', '']]
        self.score_widget.setStyleSheet("QWidget#x_widget {border-bottom: 3px solid #F03D2D}")"""

    def buttonClicked(self):
        button = self.sender()
        index = self.buttons.index(button)
        #print(index, index//3, index%3)
        row = index // 3
        col = index % 3

        data = {"where": "game", "type": "move", "move": [row, col], "index": index}
        json_data = json.dumps(data)

        self.client_socket.send(json_data.encode())

        """if self.board[row][col] == '':
            self.board[row][col] = self.currentPlayer
            button.setText(self.currentPlayer)
            self.moves += 1

        if self.checkWin(row, col):
            self.showWinner(self.currentPlayer)
            self.updateScore(self.currentPlayer)
        elif self.moves == 9:
            self.showDraw()
        else:
            if self.currentPlayer != "X":
                self.score_widget.setStyleSheet("QWidget#x_widget {border-bottom: 3px solid #F03D2D}")
                self.currentPlayer = "X"
            else:
                self.score_widget.setStyleSheet("QWidget#o_widget {border-bottom: 3px solid #F03D2D}")
                self.currentPlayer = "O"
            #self.currentPlayer = "O" if self.currentPlayer == "X" else "X"""

    def checkWin(self, row, col):
        symbol = self.board[row][col]

        # Check row
        if self.board[row][0] == self.board[row][1] == self.board[row][2] == symbol:
            return True

        # Check column
        if self.board[0][col] == self.board[1][col] == self.board[2][col] == symbol:
            return True

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == symbol:
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == symbol:
            return True

        return False

    def showWinner(self):
        self.resultLabel.setText("Kazandın")
        self.resultLabel.setVisible(True)
    """def showWinner(self, player):
        self.resultLabel.setText(f"Player {player} wins!")
        self.resultLabel.setVisible(True)
        #self.disableButtons()"""

    def showDraw(self):
        self.resultLabel.setText("Berabere!")
        self.resultLabel.setVisible(True)
        #self.disableButtons()

    def resetGame(self):
        for button in self.buttons:
            button.setText("")
            button.setEnabled(True)
        #self.resultLabel.setVisible(False)

    def disableButtons(self):
        for button in self.buttons:
            button.setEnabled(False)

    def enableButtons(self):
        for button in self.buttons:
            button.setEnabled(True)
    
    def updateScore(self, player):
        if player == "X":
            try:
                score = int(self.x_score_label.text()) + 1
                self.x_score_label.setText(str(score))
            except ValueError:
                self.x_score_label.setText("1")
        elif player == "O":
            try:
                score = int(self.o_score_label.text()) + 1
                self.o_score_label.setText(str(score))
            except ValueError:
                self.o_score_label.setText("1")
    
    def connect_server(self):
        with open("settings.json", "r") as file:
            data = json.load(file)
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        server_address = (data["host"], data["port"])

        try:
            self.client_socket.connect(server_address)

            connect = self.client_socket.recv(1024).decode("utf-8")
            if connect == "connect":
                self.infoLabel.setText("Bağlanıldı\noyuncu bekleniyor...")

                self.receive_thread = Thread(target=self.receive_data)
                self.receive_thread.start()
        except ConnectionRefusedError:
            print("Bağlantı başarısız")
            self.infoLabel.setText("Bağlantı başarısız\nTekrar dene...")
            return
        except TimeoutError:
            print("Zaman Aşımı")
            self.infoLabel.setText("Zaman Aşımı\nTekrar dene...")

    
    def receive_data(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                print(data)

                if not data:
                    break # sunucu ile bağlantı kesilir.

                json_data = json.loads(data)
                self.initGame(json_data)
            
            #self.initGame(position)
            
            except ConnectionResetError as a:
                self.infoLabel.setText("Sunucu kapandı\nTekrar dene...")
                self.infoLabel.setVisible(True)
                print(a)
                break

            except OSError as a:
                self.infoLabel.setText("Veri gönderme hatası\nTekrar dene...")
                self.infoLabel.setVisible(True)
                print(a)
                break
            
            # except Exception as a:
            #     self.infoLabel.setVisible(True)
            #     self.infoLabel.setText(f"Veri Alma Hatası\nHata: {str(a)}")
            #     print(a)
            #     time.sleep(2)
            #     self.infoLabel.setText(f"Veri Alma Hatası\nTekrar dene...")
            #     break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tictactoe = TicTacToe()
    tictactoe.show()
    sys.exit(app.exec())

