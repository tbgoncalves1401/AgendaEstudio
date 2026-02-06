from datetime import datetime
from conexao.databasePeewe import db
from peewee import Model, DateField, CharField, AutoField, DateTimeField

class BaseModel(Model):
    class Meta:
        database = db

class Responsavel(BaseModel):
    cd_responsavel = AutoField()
    nm_responsavel = CharField(max_length=100, index=True)
    ds_email = CharField(max_length=180, unique=True)
    ds_telefone = CharField(max_length=20, unique=True)
    dt_nascimento = DateField(null=True)
    dt_cadastro = DateTimeField(null=False, default=datetime.now)  # ✅ aqui
    dt_alteracao = DateTimeField(null=True)
    dt_inativo = DateTimeField(null=True)

    class Meta:
        table_name = 'responsavel'


# from datetime import date
# from conexao.databasePeewe import db
# from peewee import Model, DateField, CharField, AutoField, DateTimeField

# class BaseModel(Model):
#     class Meta:
#         database = db

# class Responsavel(BaseModel):
#     cd_responsavel = AutoField()
#     nm_responsavel = CharField(max_length=100,  index=True)
#     ds_email   = CharField(max_length=180, unique=True)
#     ds_telefone= CharField(max_length=20,  unique=True)
#     dt_nascimento = DateField(null=True)
#     dt_cadastro = DateTimeField(null=False, default=date.now)
#     dt_alteracao = DateTimeField(null=True)
#     dt_inativo = DateTimeField(null=True)
#     class Meta:
#         table_name = 'responsavel'