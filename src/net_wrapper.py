import xmlrpclib
import pickle
'''
network layer wrapper for xmlrpc code
'''
class BadLogin(Exception):
    def __init__(self, msg):
        self.msg = msg

class NoDataFile(Exception):
    def __init__(self, msg):
        self.msg = msg

class Session_manager(object):
    def __init__(self, url, user, pw):
        url = url.replace('//', '//'+user + ':' + pw + '@', 1)
        print url
        self.session = xmlrpclib.Server(url)
        print self.session
        self.data_file = None
#        self.pw = pw # TODO encrypt password
        self.user = self.session.get_userid(user)
#        if self.user == -1:
#            raise BadLogin("Bad username or password")
        
    def send_data(self, array):
        self.data = pickle.dumps(array)
        self.data_file = self.session.send_data(self.data)
        
    def send_job(self, job_def):
        if self.data_file  is None:
            raise ENoData('No data file has been sent for this job')
        else:
            job_id = self.session.send_job(job_def, self.data_file, self.user)
            return job_id
        
    def get_status(self, job_id):
        return self.session.get_status(job_id, self.user)
        
    def get_result(self, job_id):
        return self.session.get_result(job_id, self.user)
    
    def get_server_status(self):
        return self.session.server_status()

def connect(url, username, pw):
    return Session_manager(url, username, pw)

if __name__ == '__main__':
    import numpy
    session = connect('http://localhost:8000', 'jfrelinger', 'secret')
    print session.get_server_status()
    foo = numpy.zeros((4,4))
    session.send_data(foo)
    print session.data_file
    #print session.get_status(1)
