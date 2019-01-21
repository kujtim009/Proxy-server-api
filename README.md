# Python-proxy-checker
Python proxy checker

Create an instance of GetProxy class and pass two arguments to constructor 
firstt argument is `Name` and  the second argument is `Url`.

I.E ```th1 = GetProxy('Udemy','http://www.udemy.com')```

after creating an instance of GetProxy class ,start the thread
using ```th1.start()```

You can create many instances of the GetProxy class.

by default if the proxy is working it will pause 2 mins. and will be stored in text file.
i.e `name_proxy.txt`

if the text file contains 50 proxy it will delete all proxies and generate new proxies.
