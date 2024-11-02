
#Ui side imports
import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit


#client side imports
import socket
import os
from Encryption import aes_encrypt

# Server IP address and port
SERVER_IP = ''
SERVER_PORT = 12345

# Paths of Sending files
file_paths = []

# Encryption key (must be 16, 24, or 32 bytes long)
ENCRYPTION_KEY = b'Sixteen byte key'




#Function for client side
# 1) for chunking the file
def chunk_file(file_path, chunk_size=1024):
    """Splits a file into chunks of specified size."""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk



#2) sending to server function
def send_file(file_path):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((SERVER_IP, SERVER_PORT))
        
        # file name
        file_name = os.path.basename(file_path)
        s.sendall(file_name.encode())
        
        # acknowledgment of file name
        s.recv(1024)
        
        # file size
        file_size = os.path.getsize(file_path)
        s.sendall(str(file_size).encode())
        
        # acknowledgment of Size
        s.recv(1024)
        
        # Sending of chunks
        for chunk in chunk_file(file_path):
            encrypted_chunk = aes_encrypt(chunk, ENCRYPTION_KEY)
            s.sendall(encrypted_chunk)
        
    finally:
        s.close()


#3) Start the Sender function
def start_client():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((SERVER_IP, SERVER_PORT))
        
        # Sending total files no.
        num_files = len(file_paths)
        s.sendall(str(num_files).encode())
        
        # acknowledgment for file no.
        s.recv(1024)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

    finally:
        s.close()

    # Sending each files
    for file_path in file_paths:
        send_file(file_path)








class FileDropWidget(QLabel):
    def __init__(self):

        super().__init__()
        self.setAcceptDrops(True)
        self.setText("Enter the Sender's IP Address \nDrop Files Here...")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #3b3b3b; color: white; padding: 50px; border: 2px dashed #555; font-size: 16px;")

    # to get paths of files
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # drop event function
    def dropEvent(self, event: QDropEvent):

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_paths.append(file_path)
        
        self.setText(f"Files dropped:\n" + "\n".join(file_paths))
        print("All dropped files:", file_paths)

class MainWindow(QWidget):
    def __init__(self):

        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(642, 700, 400, 300)
        self.setStyleSheet("background-color: #000;")
        
        # the custom FileDropWidget Layout
        main_layout = QVBoxLayout()
        self.file_drop_widget = FileDropWidget()
        main_layout.addWidget(self.file_drop_widget)


        # input field
        ip_layout = QHBoxLayout()
        ip_label = QLabel("Enter Receiver's IP :")
        ip_label.setStyleSheet("color: white;font-size: 14px;")
        ip_layout.addWidget(ip_label) 
        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText("")
        self.ip_input.setStyleSheet("background-color: #3b3b3b; color: #fff; padding: 5px;border: 1px solid #000; ") 
        self.ip_input.setFixedWidth(250) 
        self.ip_input.setFixedHeight(30) 
        ip_layout.addWidget(self.ip_input)  
        ip_layout.addStretch()

        main_layout.addLayout(ip_layout)


        # Create a send button to send the data
        send_button = QPushButton("Send", self)
        send_button.setStyleSheet("background-color: #344e72; color: white; padding: 10px;")
        send_button.clicked.connect(self.send_data)  # Connect the button's clicked signal
        main_layout.addWidget(send_button)


        # Create a close button to close the window
        close_button = QPushButton("Close", self)
        close_button.setStyleSheet("background-color: #555; color: white; padding: 10px;")
        close_button.clicked.connect(self.close)  # Connect the button's clicked signal to close the window
        main_layout.addWidget(close_button)


        self.setLayout(main_layout)
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def send_data(self):

        if self.ip_input.text() == '':
            self.ip_input.setPlaceholderText("Please enter the IP address")
            return
        elif len(file_paths) == 0:
            self.file_drop_widget.setText("Please drop files to send")
            return
        

        global SERVER_IP 
        SERVER_IP = self.ip_input.text()
        print(f"IP Address: {SERVER_IP}")
        print(f"Files to send: {file_paths}")

        #start the Sender side
        try:
            self.file_drop_widget.setText("Sending files...")
            QApplication.processEvents()
            start_client()
            self.file_drop_widget.setText("Files sent successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.file_drop_widget.setText("An error occurred. Please try again.\n(not connected to the server)")



# Root
app = QApplication(sys.argv)

# Main frame
window = MainWindow()
window.show()

# Run frame event loop
sys.exit(app.exec_())






