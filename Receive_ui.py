#Ui side imports
import sys
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QPoint



# Receiver code
import socket
from Encryption import aes_decrypt


# Path to save the received files
path = ""
# List to store the saved file names
saved_files = []



# Server IP address and port
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 12345


# Encryption key to decryt
ENCRYPTION_KEY = b'Sixteen byte key'



# 1) to receive the file from sender (and decrypt it)
def handle_client_connection(client_socket):
    try:
        file_name = client_socket.recv(1024).decode()
        
        # acknowledgment for file name
        client_socket.sendall(b'ACK')
        
        file_size = int(client_socket.recv(1024).decode())
        
        # acknowledgment for file size
        client_socket.sendall(b'ACK')
        
        # To save the file
        with open(f'{path}/received_{file_name}', 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:

                # the encrypted chunk
                encrypted_chunk = client_socket.recv(1040)
                if not encrypted_chunk:
                    print("File transfer failed due to empty chunk")
                    break
                
                # Decrypting the chunk
                chunk = aes_decrypt(encrypted_chunk, ENCRYPTION_KEY)
                
                # Write the chunk
                f.write(chunk)

                bytes_received += len(chunk)
        
        # Add the file name to saved_files list
        global saved_files
        saved_files.append(file_name)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    
    finally:
        client_socket.close()

# 2) start_server And establish connection
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    client_socket, addr = server_socket.accept()

    # Receive the number of files to be received
    num_files = int(client_socket.recv(1024).decode())
    client_socket.sendall(b'ACK')
    client_socket.close()
    
    # count the number of files received
    file_counter = 0
    
    while file_counter < num_files:
        client_socket, addr = server_socket.accept()
        handle_client_connection(client_socket)
        file_counter += 1

    server_socket.close()









#Ui side code and definitions
class FileReceiveWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Select a folder to save received file...")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #3b3b3b; color: white; padding: 10px; border: 2px dashed #555; font-size: 16px;")

    def update_file_name(self, file_name):
        self.setText(f"Saved files:\nreceived_{file_name}")
        self.adjustSize()


# Main window Frame Class
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(642, 700, 400, 300)
        self.setStyleSheet("background-color: #000;")  # Set the background color to black

        main_layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        folder_label = QLabel("Select folder to save files")
        folder_label.setStyleSheet("color: white; font-size: 14px;")
        folder_layout.addWidget(folder_label)


        # "Browse" button
        browse_button = QPushButton("Browse")
        browse_button.setStyleSheet("background-color: #344e72; color: white; padding: 5px; font-size: 14px;")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_button)

        # Add the folder layout to the main layout
        main_layout.addLayout(folder_layout)
        self.file_Receive_widget = FileReceiveWidget()
        main_layout.addWidget(self.file_Receive_widget)

        # Add "Receive" button
        self.receive_button = QPushButton("Receive")
        self.receive_button.setStyleSheet("background-color: #344e72; color: white; padding: 10px; font-size: 14px;")
        self.receive_button.clicked.connect(self.receive_files)
        main_layout.addWidget(self.receive_button)

        # Add "Close" button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #555; color: white; padding: 10px; font-size: 14px;")
        close_button.clicked.connect(self.close_window)
        main_layout.addWidget(close_button)

        # Set the layout
        self.setLayout(main_layout)
        self.old_pos = None

        # State to track the button press
        self.receive_pressed_once = False

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:

            self.file_Receive_widget.setText(f"Folder selected:\n{folder_path}\nPress 'Receive' to start to connect sender...")
            print(f"Folder selected: {folder_path}")
            global path
            path = folder_path  

    def receive_files(self):

        if not self.receive_pressed_once:

            # First press to start the server
            self.receive_pressed_once = True

            # if empty path
            if path == "":
                self.file_Receive_widget.setText("No folder selected")
                self.file_Receive_widget.adjustSize()
                self.receive_pressed_once = False
            
            # if path is not empty
            elif path != "":
                self.file_Receive_widget.setText("Listening For the Sender...\n Hit Send (From sender side)")
                self.file_Receive_widget.adjustSize()
                QApplication.processEvents()
                
                try:

                    # Run start_server in a separate thread
                    server_thread = threading.Thread(target=start_server)
                    server_thread.start()

                    # Wait for the server to receive all files
                    server_thread.join()
                    
                except Exception as e:
                    print(f"An error occurred: {e}")
                    self.file_Receive_widget.setText("An error occurred. Please try again.")
                    self.file_Receive_widget.adjustSize()
                    self.receive_pressed_once = False
                
                finally:
                    self.file_Receive_widget.setText("Files received and saved successfully\n\nPress 'Received' to see receive file names")
                    self.file_Receive_widget.adjustSize()
        
        
        else:
            # Second press to display the saved files
            if saved_files:
                self.file_Receive_widget.update_file_name("\nreceived_".join(saved_files))
                self.file_Receive_widget.adjustSize()
                print("Saved files:")
                for file in saved_files:
                    print(f"- {file}")
            else:
                self.file_Receive_widget.setText("No file saved yet")
                self.file_Receive_widget.adjustSize()
                print("No files received.")


    def close_window(self):
        self.close()


    # For dragging frame by mouse
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


# Create the application
app = QApplication(sys.argv)

# Create the main window and show it
window = MainWindow()
window.show()

# Run the application's event loop
sys.exit(app.exec_())



