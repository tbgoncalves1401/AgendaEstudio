import model.usuar as usuar
import conexao.databasePeewe as dtb
from peewee import OperationalError

def consultarUsuario(nm):
    return usuar.Usuar.get_or_none(usuar.Usuar.nm_usuar == nm)  