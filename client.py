import socket
import csv
import pickle
import json
import time
"""
client
"""
def csv_read(sock, file, num, com):
    i = 0
    reader = csv.reader(file, delimiter = ';')
    snd = pickle.dumps(list(reader)[1:num + 1])
    leng = len(snd)
    sock.sendall((com + ' ' + str(leng)).encode("utf8"))
    time.sleep(2)
    sock.sendall(snd)

with socket.create_connection(("127.0.0.1", 30001)) as sock:
    num = int(input("Number of tweet = "))
    com = input("Command : ")
    if com.upper() != "STAT" and com.upper() != "ENTI":
        com = input("Please, enter the correct command : ")
    with open("dataSet.csv", encoding = "ISO8859-1") as f:
        csv_read(sock, f, num, com)
    if (int(num) < 10) and (com.upper() == "STAT"):
        err =sock.recv(4096)
        print(err.decode("utf8"))
    else:
        ls = b""
        d_size = sock.recv(4096)
        d_size = int(d_size.decode("utf8"))
        i = 0
        while i < d_size:
            d = sock.recv(1024)
            ls += d
            i += 1024
        d_cli = pickle.loads(ls)
        if com.upper() == "ENTI":
            with open("enti.json", 'w') as fi:
                fi.write(json.dumps(d_cli))
        if com.upper() == "STAT":
            with open("statistics.csv", 'w', newline = "") as file:
                writer = csv.writer(file)
                writer.writerows(d_cli)
