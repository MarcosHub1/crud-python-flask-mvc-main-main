import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Formato: mysql+pymysql://USUARIO:SENHA@HOST/NOME_DO_BANCO
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flaskuser:1234@localhost/crud_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False