import socket

HOST = ''
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    data = "bitch"
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data: continue
            conn.sendall(data)