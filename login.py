import requests
import sys

from requests import cookies

class PocLogin():
    def __init__(self, args):
        try:
            self.SERVER = 'http://localhost:5000'
        except :
            print("Usage <url>\n")
            return 0

    def print_info(self, r):
        # ANSWERS
        print("\n====New ANSWER====")
        print('\nstatus     : ', r.status_code)
        print('headers    : ', r.headers)
        print('cookies    : ', r.cookies)
        print('html       : ', r.text)

    def run_poc(self):
        # New session
        session = requests.session()
        params = {}
        headers = {'user-agent': 'my-app/0.0.1', 'Content-Type': 'application/json'}
        # url = "/init"
        
        r = session.get(self.SERVER   , params=params, headers=headers)
        self.print_info(r)

        #Register
        data = {"username":"snowden","password":"russia"}
        url = "/register"
        s = session.post(self.SERVER + url, data=data)
        self.print_info(s)

        # Login
        data = {"username":"snowden","password":"russia"}
        url = "/login"
        print(data)
        r = session.post(self.SERVER + url, data=data)
        self.print_info(r)

            

    
if __name__ == '__main__':
    pocLogin = PocLogin(sys.argv[1:])
    pocLogin.run_poc()