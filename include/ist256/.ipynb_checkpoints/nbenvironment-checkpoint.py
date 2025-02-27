import os 
import ipykernel
import requests 
import json

class NbEnvironment(object):
    
    def __init__(self):
        self.__settings = self.__load_settings()
        self.__netid = self.__find_netid()
        self.__notebook_path = self.__find_notebook_path()
        self.__service_prefix = self.__find_service_prefix()
        self.__course = self.__find_course()
        self.__git_folder = self.__find_git_folder()
        self.__bucket = self.__find_bucket()
        self.__filename = self.__find_filename()
        self.__lesson = self.__find_lesson()
        

    @property
    def properties(self):
        '''
        Return all properties as a dictrionary
        '''
        tmp = {}
        for key in self.__dict__.keys():
            tmp[key.replace('_NbEnvironment__','')] = self.__dict__[key]
        return tmp
        
    @property 
    def netid(self):
        return self.__netid

    @property 
    def notebook_path(self):
        return self.__notebook_path

    @property 
    def service_prefix(self):
        return self.__service_prefix
    
    @property 
    def course(self):
        return self.__course
    
    @property 
    def git_folder(self):
        return self.__git_folder
    
    @property 
    def bucket(self):
        return self.__bucket
    
    @property
    def filename(self):
        return self.__filename
    
    @property
    def lesson(self):
        return self.__lesson
    
    
    def __load_settings(self):
        if os.path.exists(".settings"):
            with open(".settings","r") as f:
                settings = json.load(f)
                return settings
        else:
            return {}

    def __find_bucket(self):
        return f"{self.__course}-{self.__git_folder}"
            
    def __find_git_folder(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 3 and items[0] == 'library':
            return self.__settings.get('git-folder',items[2])
        else:
            raise Error('This notebook file is not in a git folder under the course folder.')

    def __find_lesson(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 4 and items[0] == 'library':
            return items[-2]
                
    def __find_filename(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 4 and items[0] == 'library':
            return items[-1]
    
    def __find_course(self):
        items = self.__notebook_path.split('/')
        if len(items) >= 2 and items[0] == 'library':
            return items[1]
        else:
            raise Error('This notebook file must be in a course folder.')
            
    def __find_service_prefix(self):
        return os.environ.get('JUPYTERHUB_SERVICE_PREFIX')

    def __find_netid(self):
        netid = os.environ.get('JUPYTERHUB_USER')
        if os.environ.get('JUPYTERHUB_CLIENT_ID').find(netid)>=0 and os.environ.get('JUPYTERHUB_SERVICE_PREFIX').find(netid)>=0:
            return netid
        else:
            raise Error('Unable to locate a netid for this user.')
            
    def __find_notebook_path(self):
        connection_file = os.path.basename(ipykernel.get_connection_file())
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]
        token = os.environ.get("JUPYTERHUB_API_TOKEN")
        netid = self.__netid
        response = requests.get(f'http://127.0.0.1:8888/user/{netid}/api/sessions?token={token}')
        response.raise_for_status()
        sessions = response.json()    
        for sess in sessions:
            if sess['kernel']['id'] == kernel_id:
                return sess['notebook']['path']
