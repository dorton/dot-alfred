# Include the Dropbox SDK libraries
from dropbox import client, session
import sys
from Tkinter import Tk, Frame, BOTH, Button, Label
import webbrowser
import os
import base64


APP_KEY = '1ev7nojjtzsf8my'
APP_SECRET = 'a03sjx2vde48wp3'
ACCESS_TYPE = 'dropbox'


class AuthWindow(Frame):
    def __init__(self, parent, url):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.initUI()
        self.url = url

    def initUI(self):
        self.parent.title("AlfredShare Auth")
        self.pack(fill=BOTH, expand=1)
        quitButton = Button(self, text="Quit", command=self.quit)
        quitButton.place(x=90, y=110)
        button = Button(self, text="Auth", command=self.openUrl)
        button.place(x=90, y=80)
        label = Label(self, text="Press on Auth button then press\n'Allow' button in browser,\nand then quit this app")
        label.place(x=20, y=10)

    def openUrl(self):
        webbrowser.open(self.url)


def setup(path=''):
    if path == '':
        path = os.path.join(findDropBox, 'Public')
    if findDropBox() in path:
        pathToShare = os.path.relpath(path, findDropBox())
    else:
        return 'Your folder not inside DropBox'
    try:
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = sess.obtain_request_token()
        url = sess.build_authorize_url(request_token)
        root = Tk()
        root.geometry("250x150+300+300")
        AuthWindow(root, url)
        root.mainloop()
        access_token = sess.obtain_access_token(request_token)
        f = open('settings', 'w')
        f.write(enc(access_token.key) + '\n' + enc(access_token.secret) + '\n' + enc(pathToShare))
        return 'Your workflow authorised!'
    except Exception, e:
        return e


def share(fileName, params=None, directDownload=False):
    if os.path.isdir(fileName) and findDropBox() not in fileName:
        return 'Sorry, I can share folders already uploaded to dropbox!'
    sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    try:
        f = open('settings', 'r')
        key = enc(f.readline().rstrip(), False)
        secret = enc(f.readline().rstrip(), False)
        pathToShare = enc(f.readline(), False)
        dropboxPath = findDropBox()
        sess.set_token(key, secret)
        cl = client.DropboxClient(sess)
        if dropboxPath in fileName:
            filePath = os.path.relpath(fileName, dropboxPath)
        else:
            f = open(fileName)
            response = cl.put_file(os.path.join(pathToShare, os.path.basename(fileName)), f)
            filePath = response['path']
        if directDownload is True and not os.path.isdir(fileName):
            result = cl.media(filePath)
        else:
            result = cl.share(filePath, params)
        return result['url']
    except Exception, e:
        return 'Run assetup before!'
        # return e


def findDropBox():
    host_db_path = os.path.join(os.path.expanduser('~'), '.dropbox/host.db')
    if os.path.exists(host_db_path):
        with open(host_db_path, 'r') as f:
            data = f.read().split()
        return base64.b64decode(data[1])
    else:
        return 'Install DropBox first!'

def enc(strToEnc, encode=True):
    if encode == True:
        return base64.b64encode(strToEnc)
    else:
        return base64.b64decode(strToEnc)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup()
    elif len(sys.argv) > 1:
        share(sys.argv[1])
