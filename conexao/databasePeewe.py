import os
from dotenv import load_dotenv
from peewee import PostgresqlDatabase
from cryptography.fernet import Fernet

# Carrega as variáveis do arquivo .env para o ambiente do sistema
load_dotenv()

# 1. Recupera a Chave Mestra e a Senha Criptografada
secret_key = os.getenv('DB_SECRET_KEY').encode()
encrypted_password = os.getenv('DB_PASS_ENCRYPTED').encode()

# 2. Descriptografa a senha
cipher_suite = Fernet(secret_key)
decrypted_password = cipher_suite.decrypt(encrypted_password).decode()

db = PostgresqlDatabase(
    os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=decrypted_password,
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')), # Porta deve ser um número inteiro    
    sslmode='require'
)

# print("Conexão configurada com sucesso!")
# from peewee import MySQLDatabase#, OperationalError, Model, CharField, IntegerField

### Configurações do Banco de Dados LOCAL ###
# db_name = 'agendaestudio'
# db_user = 'root'
# db_password = 'bluegreen'
# db_host = 'localhost'
# db_port = 3306

# # Inicializando a instância do MariaDB
# db = MySQLDatabase(
#     db_name,
#     user=db_user,
#     password=db_password,
#     host=db_host,
#     port=db_port,
#     ssl={
#             'ca': '/caminho/para/skysql_chain.pem' # Opcional: se quiser verificar o certificado
#         }    
# )


# Tipo de Campo Peewee Tipo de Dado MariaDB (MySQL)	Descrição
# AutoField	        INTEGER (com AUTO_INCREMENT)	Chave primária inteira autoincrementável.
# BigAutoField	    BIGINT (com AUTO_INCREMENT)	Chave primária inteira grande autoincrementável.
# IntegerField	    INTEGER	Armazena números inteiros de 4 bytes.
# BigIntegerField	BIGINT	Armazena números inteiros grandes de 8 bytes.
# SmallIntegerField	SMALLINT	Armazena números inteiros pequenos de 2 bytes.
# BooleanField	    TINYINT(1)	Armazena valores booleanos (0 para False, 1 para True).
# CharField	        VARCHAR (com comprimento)	String de caracteres de comprimento variável.
# FixedCharField	CHAR (com comprimento)	String de caracteres de comprimento fixo.
# TextField	        LONGTEXT	Campo de texto longo, sem limite de 255 caracteres.
# DateField	        DATE	Armazena apenas a data.
# DateTimeField	    DATETIME	Armazena data e hora.
# TimeField	        TIME	Armazena apenas a hora.
# FloatField	    REAL ou FLOAT	Armazena números de ponto flutuante.
# DoubleField	    DOUBLE PRECISION ou DOUBLE	Armazena números de ponto flutuante de dupla precisão.
# DecimalField	    DECIMAL ou NUMERIC	Armazena números decimais exatos.
# BlobField	        BLOB	Armazena dados binários (como imagens ou arquivos pequenos).