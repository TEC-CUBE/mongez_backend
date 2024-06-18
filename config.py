import datetime
from core.aws.aws_ssm import fetch_ssm_config
## dev
DATABASE_CONNECTION = f'mysql+pymysql://root:v9b4k4q3@localhost:3306/hotel_local'
## farag
#DATABASE_CONNECTION = f'mysql+pymysql://root:v9b4k4q3@localhost:3306/hotel_farag'
class Config(object):
    ##dev
    SQLALCHEMY_DATABASE_URI = DATABASE_CONNECTION
    ##prod
    #SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://sas:sas123@localhost:3306/Netcube_local'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #JWT_SECRET_KEY = fetch_ssm_config('/teccube/venice/secret_key')
    JWT_SECRET_KEY = 'Qml0Y2hBc3NOaWdnYTEyI0BVTldHVkJYTmxram5scw=='

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30 )
    UPLOAD_FOLDER = "app/uploads"
    DOWNLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "pdf"]
    MAX_CONTENT_LENGTH = 1024 * 1024 * 16 # 16M