import model.cliente as cliente
from typing import List
from datetime import datetime
import conexao.databasePeewe as dtb
from peewee import OperationalError
import geral as ger

def consultarClientedGet(cd):
    return cliente.Cliente.get_or_none(cliente.Cliente.cd_cliente == cd)  

def consultarClientes():
    return cliente.Cliente.select(cliente.Cliente.cd_cliente.alias('codigo'), cliente.Cliente.nm_cliente.alias('nome')).where(cliente.Cliente.cd_cliente >= 1).order_by(cliente.Cliente.nm_cliente)


def consultarClientePesquisa(flt: list[ger.filtros]):
    filtros = []
    for no in flt:
        if (no.campo == 'procurar' and no.valor) and no.valor != '%':
            filtros.append(
                cliente.Cliente.nm_cliente.contains(no.valor) |
                cliente.Cliente.ds_email.contains(no.valor)   |
                cliente.Cliente.ds_telefone.contains(no.valor)
            )

    try:
        dtb.db.connect(reuse_if_open=True)

        query = cliente.Cliente.select()

        if filtros:
            query = query.where(*filtros)
        query = query.order_by(cliente.Cliente.nm_cliente)#.dicts()    

        costumerList = [{
            "cd_cliente": row.cd_cliente,
            "ds_email": row.ds_email,
            "ds_telefone": row.ds_telefone,
            "nm_cliente": row.nm_cliente
        } for row in query]

        return costumerList

    except OperationalError as e:
        print(f"❌ Erro ao conectar: {e}")
        return []
    finally:
            # ✅ Garante que o banco feche após processar tudo
            if not dtb.db.is_closed():
                dtb.db.close()   

def delete(codigo: int) -> bool:
    try:
        with dtb.db.atomic():
            cnt = consultarClientedGet(codigo)
            if cnt:
                cnt.delete_instance()
                return True
            return False
    except OperationalError as e:
        print(f"❌ Erro de banco de dados ao excluir: {e}")
        return False


def persistir(clienteLocal: cliente.Cliente):
    try:
        with dtb.db.atomic():
             dtb.db.transaction()
             if clienteLocal.cd_cliente != None:
                clienteLocal.save()
             else:
                clienteLocal.save(force_insert=True)
             return True
    except OperationalError as e:
        print(f"❌ Erro ao salvar cliente: {e}")
        dtb.db.rollback()
        return False
    
    finally:
        if not dtb.db.is_closed():
            dtb.db.commit()
            dtb.db.close()