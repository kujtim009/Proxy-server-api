import os
import re
import socket
import threading
import time
import tldextract
import requests
import urllib
import random
from flask import Flask
from flask import request
from colorama import init, Fore, Back, Style
init(convert=True)

app = Flask(__name__)


class GetProxy(threading.Thread):
    def __init__(self, proxy_, urlSite, threadNum):
        threading.Thread.__init__(self)
        self.api = "34d266e5-4ef1-42c3-9bd3-077e41f5c21c"

        self.urlSite = urlSite
        self.proxy_ = proxy_
        self.timeout = 10
        self.threadNum = threadNum
        self.headers = {
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            'referer': "https://www.yahoo.com/",
            'accept-encoding': "gzip, deflate, sdch, br",
            'accept-language': "en-US,en;q=0.8,hr;q=0.6",
            'cache-control': "no-cache",
        }
        self.found = False

        self.url = "http://gimmeproxy.com/api/getProxy?api_key=%s" % self.api

        self.lock = threading.Lock()
        self.retry_times = 0
        self.domainReadyList_max = 10
        self.domainReadyFull = False
        socket.setdefaulttimeout(10)


    def getIpFromResponse(self, content):
        pattern = re.search(r'"ipPort"\s*:\s*"([^"]+)"', content, re.I | re.S)
        if pattern:
            proxy = pattern.group(1)
            proxy = "http://%s" % proxy
            return proxy
        else:
            print("Error response proxy no pattern match.")
            return None

    def saveLinks(self, proxy):
        with open("ProxyListNotWorking.txt", "a+") as l:
                l.write("%s\n" % proxy)
                l.flush()
                l.close()
        return

    def domainReadyList_filename(self, url):
        filename = ""
        urlElements = tldextract.extract(url)
        if urlElements.subdomain:
            filename = urlElements.subdomain + "-" + urlElements.domain
        else:
            filename = urlElements.domain
        return filename
    
    def domainReadyList_save(self, proxy, url):
        filename = self.domainReadyList_filename(url)
        exists = False;
        f = open("Tested_proxy/{}.txt".format(filename),"r+")
        d = f.readlines()
        f.seek(0)
        for i in d:
            f.write(i)
            if i.strip() == proxy:
                exists = True;
        if not exists:
            f.write(proxy + "\r")        
        f.truncate()
        f.flush()
        f.close()   

    def domainReadyList_count(self, url):
        filename = self.domainReadyList_filename(url)
        num_lines = sum(1 for line in open("Tested_proxy/{}.txt".format(filename)))
        return num_lines

    def domainReadyList_getProxy(self, url):
        filename = self.domainReadyList_filename(url)
        if os.path.isfile("Tested_proxy/{}.txt".format(filename)):
            f=open("Tested_proxy/{}.txt".format(filename))
            lines=f.readlines()
            f.flush()
            f.close()
            if len(lines)>=1:
                return random.choice(lines).strip()
            else:
                return None
        else:
            open("Tested_proxy/{}.txt".format(filename),"w+")
            return None

    def domainreadyList_delete(self, url, proxy_delete):
        filename = self.domainReadyList_filename(url)
        f = open("Tested_proxy/{}.txt".format(filename),"r+")
        d = f.readlines()
        f.seek(0)
        for i in d:
            if i.strip() != proxy_delete:
                f.write(i)
        f.truncate()
        f.flush()
        f.close()
        
    def saveLink(self, proxy):
        with open("ProxyListWorking.txt", "a+") as l:
                l.write("%s\n" % proxy)
                l.flush()
                l.close()
        return

    def run(self):
        # print('Running thread: %s' % self.urlSite)
        self.found = False
        if len(self.urlSite) > 60:
            url_to_print = self.urlSite[:60].strip()
        else:
            url_to_print = self.urlSite.strip()

        while not self.found:
            try:
                with self.lock:

                    with requests.Session() as s:
                    #####################################################
                            
                        try:
                            ready_proxy = self.domainReadyList_getProxy(self.urlSite)
                            if ready_proxy is not None:
                                print(Fore.CYAN + 'Testing: %s for: %s' % (ready_proxy, url_to_print))
                                proxies = {'http': ready_proxy, 'https': ready_proxy}
                                r = s.get(self.urlSite, headers=self.headers, proxies=proxies, timeout=self.timeout, verify=True)
                                if r.status_code == 200:
                                    print(Fore.GREEN + 'OK: %s' % ready_proxy.strip())
                                    self.proxy_ = ready_proxy 
                                    self.found = True
                                else:
                                    self.domainreadyList_delete(self.urlSite, ready_proxy)
                        except Exception as e:
                            self.domainreadyList_delete(self.urlSite, ready_proxy)
                       
                    ######################################################
            
                        while not self.domainReadyFull:
                            response = s.get(self.url, timeout=self.timeout)
                            if response.status_code == 200:
                                content = response.text

                                proxy = self.getIpFromResponse(content)
                                if re.match(r'http://[\d.:]+', proxy):
                                    
                                    print(Fore.RED + 'Testing: %s -> %s' % (proxy, url_to_print))
                                    self.saveLinks(proxy)
                                    self.retry_times += 1
                                    if self.retry_times > 200:
                                        self.found = True

                                    try:
                                        proxies = {'http': proxy, 'https': proxy}
                                        r = s.get(self.urlSite, headers=self.headers, proxies=proxies, timeout=self.timeout, verify=True)
                                        if r.status_code == 200:
                                            print(Fore.GREEN + 'OK: %s' % proxy.strip())
                                            self.saveLink(proxy)
                                            self.domainReadyList_save(proxy, self.urlSite)
                                    except Exception as e:
                                        pass
                            if self.domainReadyList_count(self.urlSite) >= self.domainReadyList_max:
                                self.domainReadyFull = True    
                            

            except Exception as e:
                pass


@app.route("/getProxy", methods=['GET'])
def hello():
    url = request.args.get('url')
    if url:
        proxy = None
        time.sleep(2)
        try:
            th_list = []
            number_of_threads = 4
            for t in range(number_of_threads):
                th = GetProxy(proxy, url, t)
                th.daemon = True
                th.start()
                th_list.append(th)

            p = None
            found = False

            while not found:
                for thread in th_list:
                        proxy_ = thread.proxy_
                        if proxy_:
                            p = proxy_
                            found = True
                            break
                time.sleep(0.5)

            for thread in th_list:
                if thread.isAlive():
                    thread.found = True

            return p

        except Exception as e:
            print(e)

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=50501, threaded=True)
    # app.run(host="127.0.0.1", port=50501, threaded=True)
    print('Server has started on localhost port 50501 ..')
