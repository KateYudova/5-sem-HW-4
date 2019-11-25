import socket
import csv
import os
import time
import threading
import multiprocessing
from pynlp import StanfordCoreNLP
import pickle
from collections import Counter
"""
server
"""
def tmp1(l):
    if l[14].isdigit():
        return int(l[14])
    else:
        return 0
def tmp(l):
    if l[8] == "":
        return 0
    else:
        return int(l[8])
def tw_top10(ls):
    """
    Top10 common tweet
    """
    return(reversed(sorted(ls, key = tmp)))
def cou(ls):
    """
    Country
    """
    cou_tw = set()
    cou_retw = set()
    for i in ls:
        if i[6][:2] == "RT":
            cou_retw.add(i[11])
        else:
            cou_tw.add(i[11])
    return list(cou_tw), list(cou_retw)
def auth_top10(ls):
    """
    Top10 authors
    """
    i = 0
    flw = []
    flws = list(reversed(sorted(ls, key = tmp1)))[:10]
    for j in flws:
        flw.append([])
        flw[i].append(j[4])
        flw[i].append(j[14])
    return flw
def wrd_top10(ls):
    """
    Top10 common words
    """
    tw = []
    for i in ls:
        tw.extend(i[6].split())
    tw_top = Counter(tw)
    tmp = tw_top.most_common(10)
    tmp1 = []
    for i in range(len(tmp)):
        tmp1.append([])
        tmp1[i].append(tmp[i][0])
        tmp1[i].append(tmp[i][1])
    return tmp1

def process_request(con, adr):
    print("connected client: ", adr)
    ls = b""
    d_com = con.recv(4096)
    d_com = d_com.decode("utf8").split(' ')
    leng = int(d_com[1])
    i = 0
    while i < leng:
        dat =con.recv(1024)
        ls += dat
        i += 1024
    ls1 = pickle.loads(ls)
    if d_com[0].upper() == "STAT":
        if len(ls1) < 10:
            err =  "Need more data"
            con.sendall(err.encode("utf8"))
        else:
            wrd_top = wrd_top10(ls1)
            tw_top = (list(tw_top10(ls1)))[:10]
            tw_top10_n = []
            for i in range(len(tw_top)):
                tw_top10_n.append([])
                tw_top10_n[i].append(tw_top[i][6])
                tw_top10_n[i].append(tw_top[i][3])
                tw_top10_n[i].append(tw_top[i][8])
            auth_top = auth_top10(ls1)
            cou_tw, cou_retw = cou(ls1)
            d_cli = [["popular words ", "number of words"]]
            d_cli.extend(wrd_top)
            d_cli.extend([])
            d_cli.extend([["tweet content", "author", "RT"]])
            d_cli.extend(tw_top10_n)
            d_cli.extend([["author", "followers"]])
            d_cli.extend(auth_top)
            d_cli.extend([["country (tweet)"], cou_tw])
            d_cli.extend([["country (retweet)"], cou_retw])
            msg = pickle.dumps(d_cli)
            size = len(msg)
            con.sendall((str(size)).encode("utf8"))
            time.sleep(2)
            con.sendall(msg)
    if d_com[0].upper() == "ENTI":
        nlp = StanfordCoreNLP(annotators = 'entitymentions')
        p = []
        ls1 = str(ls1)
        ls1 = ls1.split(',')
        for row in ls1:
            doc = nlp(row)
            for entity in doc.entities:
                p.append(str(entity) + ' ' + '(' + str(entity.type) + ')')
        p = "".join(p)
        print(p)
        msg = pickle.dumps(p)
        size = len(msg)
        con.sendall((str(size)).encode("utf8"))
        time.sleep(2)
        con.sendall(msg)
    con.close()

def worker(sock):
    while True:
        con, adr = sock.accept()
        print("pid", os.getpid())
        thr = threading.Thread(target = process_request, args = (con, adr))
        thr.start()

with socket.socket() as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 30001))# max port 65535
    sock.listen()
    workers_count = 3
    workers_list = [multiprocessing.Process(target = worker, args = (sock, )) for _ in range(workers_count)]
    for i in workers_list:
        i.start()
    for j in workers_list:
        j.join()
