import csv
import sys
import requests
from concurrent import futures
"""
web client
"""
class Coms:
    serv_com = {'STAT', 'ENTI'}
    def is_serv_c(cmd): return cmd.upper() in Coms.serv_com


def rcv_st(text, com, path):
    flag = True
    am = cur_am = 0
    size = res = ''
    while True:
        if not am:
            if ' ' in text:
                arg, tmp, text = text.partition(' ')
                am = int(arg)
            if am:
                if not size:
                    if ' ' in text:
                        arg, tmp, text = text.partition(' ')
                        size = int(arg)
                    else:
                        continue
            flag = True
            if len(text) == size:
                size = cur_size = 0
                cur_am += 1
                res += text + ' '
                if com.upper() == "STAT":
                    res += "(!)"
                text = ''
            elif len(text) > size:
                flag = False
                res += text[:size] + ' '
                if com.upper() == "STAT":
                    res += "(!)"
                text = text[size:]
                size = cur_size = 0
                cur_am += 1
            if cur_am == am:
                break
        if com.upper() == "STAT":
            res = "(!)" + res
        tmp = res.split("<>")
        for i, j in enumerate(tmp):
            if com.upper() == "STAT":
                tmp[i] = j.split("(!)")
            if com.upper() == "ENTI":
                tmp[i] = j.split()
            if not tmp[i]:
                del(tmp[i])
        if com.upper() == "STAT":
            tmp[0][0] = "authors"
            tmp[1][0] = "popular tweets and their authors"
            tmp[2][0] = "countries of RT"
            tmp[3][0] = "countries with orig tweets"
            tmp[4][0] = "popular words"
        csw_w(tmp, path)
        
def csv_w(d, path):
    with open(path, "w", newline = '') as csv_f:
        writer = csv.writer(csv_f, delimeter = ';')
        for i in d:
            writer.writerow(i)

def w_c(com, arg, p, port):
    to_send = com + arg + ' '
    with open('dataSet.csv', encoding='ISO8859-1', newline='') as File:
        reader = csv.reader(File, delimiter = ';')
        for i, row in enumerate(reader):
            msg = str(row)
            l = str(len(msg.encode('ISO8859-1')))
            to_send += l + ' '
            to_send += msg
            if i == int(arg) - 1:
                break
    r = requests.post("http://localhost:" + str(port), data = (to_send).encode("ISO8859-1"))
    rcv_st(r.content.decode("ISO8859-1"), com, p)

com = input("Command = ")
arg = input("Tweets: ")
path = "web.csv"
port = "7000"
if Coms.is_serv_c(com):
    cmd = w_c(com, arg, path, port)
else:
    print("error")
