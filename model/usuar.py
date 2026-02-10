from conexao.databasePeewe import db
from peewee import Model, DateField, CharField, AutoField

class BaseModel(Model):
    class Meta:
        database = db

class Usuar(BaseModel):
    cd_usuar = AutoField()
    nm_usuar = CharField(max_length=15,  index=True)
    ds_senha   = CharField(max_length=20)
    class Meta:
        table_name = 'usuar'  
        indexes = ((('nm_usuar', 'dds_senhaa'), True), )        