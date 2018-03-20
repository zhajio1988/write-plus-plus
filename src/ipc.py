"""
ipc.py - inter-process communication system for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
NOTE: Parts of this file are based on code from Editra
"""

import getopt
import os.path
import socket
import time
import wx

try:
    import threading
except ImportError:
    import dummy_threading as threading

class IPCServer(threading.Thread):
    port = 50000##49152
    def __init__(self, app):
        threading.Thread.__init__(self)
        self._app = app

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                try:
                    self.socket.bind(("localhost", IPCServer.port))
                except:
                    IPCServer.port += 1
                else:
                    break
            self.socket.listen(5)
        except socket.error:
            self.socket = None

        self.running = True

        self.setDaemon(True)    # Force thread to quit if program is aborted

    def run(self):
        while self.running:
            client, address = self.socket.accept()
            if not self.running:
                break
            args = [client.recv(4096).decode()]
            start = time.time()
            while len(args[-1]) == 4096 and time.time() < start + 2:
                args.append(client.recv(4096).decode())
            args = "".join(args).split("\0")
            if args == [""]:
                args = []
            options, args = getopt.getopt(args, "", ["session="])
            if len(options):
                session = options[0][1]
                if not os.path.isabs(session):  # Check if path is relative
                    session = os.path.join(self._app.cwd, session)
                wx.CallAfter(self._app.NewFrame, session)
            else:
                frame = self._app.frames[self._app.active]
                wx.CallAfter(self._app.ShowFrame, frame)
                for arg in args:
                    if os.path.exists(arg):
                        wx.CallAfter(frame.OpenFile, arg)
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.socket.close()

    def Quit(self):
        self.running = False
        transmit([])


def transmit(args):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost", IPCServer.port))
        client.send("\0".join(args).encode())
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except socket.error:
        return False
    return True
