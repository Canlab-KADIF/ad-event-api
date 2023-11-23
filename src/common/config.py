class JWTConfig:
    # openssl rand -base64 32
    SECRET = 'MJB7mpBP8vD1NHMC1KDhddDZhRzbZgWYOOtrSLvnONI='


class MySqlConfig:
    # 개발 환경
    HOST = '106.245.229.11'
    PORT = 3306
    DATABASE = 'pothole'
    USER = 'pothole'
    PASSWORD = 'pothole!@#'
    # 운영환경
    HOST_PRODUCT = '106.245.229.11'
    PORT_PRODUCT = 3306
    DATABASE_PRODUCT = 'pothole'
    USER_PRODUCT = 'pothole'
    PASSWORD_PRODUCT = 'pothole!@#'

class commonCode:
    iconList = ['fa-arrows', 'fa-ban', 'fa-bar-chart-o', 'fa-calendar', 'fa-check-circle-o', 'fa-download', 'fa-edit', 'fa-file-o', 'fa-list', 'fa-floppy-o', 'fa-search', 'fa-th-large', 'fa-trash']

class FileUrl:
    Local = 'http://192.168.0.243:5001/'
    Server = 'http://106.245.229.11:5001/'

class FilePath:
    # 파일이 보여지게 하기 위해선 statice 폴더로 생성을 해야한다.
    rootDir = '/home/pothole/api/'
    fileDir = 'static/files/'





