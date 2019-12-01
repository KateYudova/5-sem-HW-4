import os
import csv
import threading
import multiprocessing
from sys import getsizeof
from pynlp import StanfordCoreNLP
import selectors
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
"""
web server
"""
class Pop:
    def __init__(self):
        self.w = {}
        self.tw = {}
        self.a = {}
        for i in range(10):
            self.tw.update({-i: ('', '')})
            self.a.update({-i: ''})
        self.c_rt = set()
        self.c_orig = set()
class Cli:
    def __init__(self):
        self.a = 0
        self.cur_a = 0
        self.size = 0
        self.cur_size = 0
        self.buf = ''
        self.bum = []
        self.end = []
        self.stat_tw = Pop()
        self.com = ''
    def read(self, st):
        tmp = ''
        st = st.decode('ISO8859-1')
        flag = True
        while True:
            if flag:
                self.buf += st
                self.cur_size += len(st)
            flag = False
            if tmp:
                self.buf += tmp
                self.cur_size += len(tmp)
            if not self.com and len(self.buf) > 4:
                self.com = self.buf[:4]
                self.buf = self.buf[4:]
                self.end = []
            if self.com:
                if not self.a:
                    if ' ' in self.buf:
                        num, tmp, self.buf = self.buf.partition(' ')
                        self.a = int(num)
            if self.a:
                if not self.size:
                    if ' ' in self.buf:
                        num, tmp, self.buf = self.buf.partition(' ')
                        self.size = int(num)
                        self.cur_size = len(self.buf)
                        self.cur_a += 1
            if (not self.size) | (not self.com) | (not self.a):
                break
            if self.cur_size < self.size:
                tmp = ''
                break
            if self.cur_size == self.size:
                self.to_res()
                self.cl_buf()
    def to_res(self):
        self.bum.append(self, buf)
        if self.a == self.cur_a:
            if self.com.upper() == "ENTI":
                self.enti_s_cl()
            if self.com.upper() == "STAT":
                self.make_stat()
                self.s_stat()
            self.cl_all()
    def cl_all(self):
        self.cl_buf()
        self.bum = []
        self.star_tw = Pop()
        self.com = ''
        self.a = 0
    def cl_buf(self):
        self.buf = ''
        self.cur_size = self.size = 0
        if self.a == self.cur_a:
            self.com = ''
            self.a = self.cur_a = 0
    def s_stat(self):
        res = []
        res.append(str(self.a_stat() + 4) + ' ')
        for i in self.stat_tw.a:
            if i > 0:
                cur_a = self.stat_tw.a[i]
                res.append(str(len(cur_a)) + ' ')
                res.append(cur_a)
        res.append(str(len("<> ")) + ' ')
        res.append("<> ")
        for i in self.stat_tw.tw:
            if i > 0:
                tw, a = self.stat_tw.tw[i]
                res.append(str(len(tw)) + ' ')
                res.append(tw)
                res.append(str(len(a)) + ' ')
                res.append(a)
                res.append(str(len(str(i))) + ' ')
                res.append(str(i))
        res.append(str(len("<> ")) + ' ')
        res.append("<> ")
        for i in self.stat_tw.c_orig:
            res.append(str(len(i)) + ' ')
            res.append(str(i))
        res.append(str(len("<> ")) + ' ')
        res.append("<> ")
        for i in self.stat_tw.c_rt:
            res.append(str(len(i)) + ' ')
            res.append(str(i))
        res.append(str(len("<> ")) + ' ')
        res.append("<> ")
        if len(self.stat_tw.w) >= 10:
            for i in range(10):
                max_w = max(self.stat_tw.w, key = self.stat_tw.w.get)
                self.stat_tw.w.pop(max_w)
                res.append(str(len(max_w)) + ' ')
                res.append(max_w)
        else:
            for i in self.stat_tw.w:
                res.append(str(len(i)) + ' ')
                res.append(str(i))
        self.end = res
    def a_stat(self):
        tmp = 0
        if len(self.stat_tw.w) > 10:
            tmp += 10
        else:
            tmp += len(self.stat_tw.w)
        for i in self.stat_tw.tw:
            if i > 0:
                tmp += 3
        for i in self.stat_tw.a:
            if i > 0:
                tmp += 1
        for i in self.stat_tw.c_orig:
            tmp += 1
        for i in self.stat_tw.c_rt:
            tmp += 1
        return tmp
    def make_stat(self):
        for i, j in enumerate(self.bum):
            j = eval(j)
            self.bum[i] = j
            if not j[6]:
                return
            for k in j[6].split():
                tmp = self.stat_tw.w.get(k)
                if not tmp:
                    self.stat_tw.w.update({k:1})
                else:
                    self.stat_tw.w.update({k:tmp + 1})
            if j[8].isdigit():
                min_el = min(self.stat_tw.tw)
                if (int(j[8]) > min_el) and not (self.stat_tw.tw.get(int(j[8]))):
                    self.stat_tw.tw.pop(min_el)
                    self.stat_tw.tw.update({int(j[8]): (j[6], j[4])})
            if j[14].isdigit():
                min_el = min(self.stat_tw.a)
                if int(j[14]) > min_el:
                    self.stat_tw.a.pop(min_el)
                    self.stat_tw.a.update({int(j[14]): j[4]})
            if j[11] and j[11] != "Country":
                if j[6][:2] == "RT":
                    self.stat_tw.c_rt.update({j[11]})
                else:
                    self.stat_tw.c_orig.update({j[11]})
    def enti_s_cl(self):
        res = []
        res.append(str(len(self.bum)) + ' ')
        for i in self.bum:
            msg = self.nams(i)
            res.append(str(len(msg)) + ' ')
            res.append(msg)
        self.end = res
    def nams(self, st):
        return self.stan(st)
    def stan(self, tmp):
        nlp = StanfordCoreNLP(annotators='entitymentions')
        res = []
        tmp = tmp.split()
        for i in tmp:
            doc = nlp(i)
            for entity in doc.entities:
                res.append(str(entity) + ' ' + '(' + str(entity.type) + ')')
        res = " <> ".join(res) + "<> "
        return res
class ReqHeand(BaseHTTPRequestHandler):
    def __init__(self, req, cl_add, serv):
        self.user = Cli()
        BaseHTTPRequestHandler.__init__(self, req, cl_add, serv)
    def do_head(self):
        self._set_head()
    def _set_head(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.data_string = ''
    def _html(self, msg):
        content = f"<html><body><h1>{msg}</h1></body></html>"
        return content.encode("utf8")
    def do_GET(self):
        res = ''
        self._set_head()
        tmp = self.user.end
        for r in tmp:
            self.wfile.write((r.encode("ISO8859-1")))
    def do_POST(self):
        print("OK")
        cont_l = int(self.headers["Content-Length"])
        self.data_string = self.rfile.read(cont_l)
        self.user.read(self.data_string)
        self._set_head()
        string = ''
        for i in self.user.end:
            string += i
        self.wfile.write((string.encode("ISO8859-1")))
def beg(serv_class = ThreadingHTTPServer, hand_class = ReqHeand, addr = "localhost", port = 7000):
    try:
        serv_addr = (addr, port)
        httpd = serv_class(serv_addr, hand_class)
        print(f"Starting httpd server on {addr}:{port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
        print("\n Stop serv.")
beg()   
