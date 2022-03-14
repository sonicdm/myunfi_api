import configparser
import os
from pathlib import Path
from unfi_api.api.admin_backend import user

# read config from settings.ini
config = configparser.ConfigParser()
settings_module_dir = os.path.dirname(__file__)
# parent folder
main_folder = os.path.dirname(settings_module_dir)
# settings file is located in relative path ../settings.ini
settings_file = os.path.join(main_folder, 'settings.ini')
config.read(settings_file)

username = config.get('DEFAULT', 'username')
password = config.get('DEFAULT', 'password')
auto_download = config.getboolean('DEFAULT', "auto_download", fallback=False)
auto_save = config.getboolean('DEFAULT', "auto_save", fallback=False)
auto_login = config.getboolean('DEFAULT', "auto_login", fallback=False)
default_save_path = config.get('DEFAULT', "default_save_path", fallback=os.path.join(os.path.expanduser('~'), 'Downloads'))
thread_type = config.get('DEFAULT', 'thread_type', fallback='thread')


search_chunk_size = config.getint('SEARCH', 'search_chunk_size', fallback=1700)


session_defaults =  dict(
    auto_download=auto_download,
    auto_save=auto_save,
    auto_login=auto_login,
    search_chunk_size=search_chunk_size,
    default_save_path=default_save_path
)

def save_settings():
    config['DEFAULT']['auto_download'] = str(auto_download)
    config['DEFAULT']['auto_save'] = str(auto_save)
    config['DEFAULT']['auto_login'] = str(auto_login)
    config['SEARCH']['search_chunk_size'] = str(search_chunk_size)
    config['DEFAULT']['default_save_path'] = str(default_save_path)
    config['DEFAULT']['username'] = str(username)
    config['DEFAULT']['password'] = str(password)
    
    with open(settings_file, 'w') as configfile:
        config.write(configfile)
    configfile.close()
    
    
def reload_settings():
    global auto_download
    global auto_save
    global auto_login
    global search_chunk_size
    global username
    global password
    global default_save_path
    config.read(settings_file)
    username = config.get('DEFAULT', 'username', fallback=os.getenv('UNFI_USER'))
    password = config.get('DEFAULT', 'password', fallback=os.getenv('UNFI_PASSWORD'))
    auto_download = config.getboolean('DEFAULT', "auto_download", fallback=False)
    auto_save = config.getboolean('DEFAULT', "auto_save", fallback=False)
    auto_login = config.getboolean('DEFAULT', "auto_login", fallback=False)
    default_save_path = config.get('DEFAULT', "default_save_path", fallback=os.path.join(os.path.expanduser('~'), 'Downloads'))
    
def reset_to_default():
    global auto_download
    global auto_save
    global auto_login
    global search_chunk_size
    auto_download = session_defaults['auto_download']
    auto_save = session_defaults['auto_save']
    auto_login = session_defaults['auto_login']
    search_chunk_size = session_defaults['search_chunk_size']
    save_settings()

def get_default_settings():
    return session_defaults
    
def get_settings():
    return dict(
        auto_download=auto_download,
        auto_save=auto_save,
        auto_login=auto_login,
        search_chunk_size=search_chunk_size,
        default_save_path=default_save_path,
        username=username,
        password=password
    )

def update_settings(settings:dict):
    ### update global settings from dict values
    global auto_download
    global auto_save
    global auto_login
    global default_save_path
    global username
    global password
    auto_download = settings.get('auto_download', auto_download)
    auto_save = settings.get('auto_save', auto_save)
    default_save_path = settings.get('default_save_path', default_save_path)
    auto_login = settings.get('auto_login', auto_login)
    username = settings.get('username', username)
    password = settings.get('password', password)
    
    
    
    