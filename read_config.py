import sys

PATH = sys.path[0]

try:
    with open(PATH + '/xweb.conf', 'r',encoding="utf-8") as conf:
        conf_dict = eval(conf.read())
except Exception as e:
    exit(1)
else:
    # TODO 添加静态资源默认回调
    if "http_port" in conf_dict:
        PORT = conf_dict['http_port']
        print(PORT)
    if "network_protocol" in conf_dict:
        PROTOCOL = conf_dict['network_protocol']
        print(PROTOCOL)
    if "IP" in conf_dict:
        IP = conf_dict['IP']
        print(IP)
    if "TIMEOUT" in conf_dict:
        TIMEOUT = conf_dict['TIMEOUT']
        print(TIMEOUT)
    if "static_path" in conf_dict:
        STATIC_PATH = conf_dict['static_path']
        
        print(STATIC_PATH)
    if "static_url" in conf_dict:
        STATIC_URL = conf_dict['static_url'].strip('/')
        print(STATIC_URL)