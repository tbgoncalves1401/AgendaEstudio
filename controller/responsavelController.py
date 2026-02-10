import model.responsavel as responsavel
from typing import List
from datetime import datetime
import conexao.databasePeewe as dtb
from peewee import OperationalError
from peewee import JOIN
import geral as ger


def consultarResponsavelGet(cd):
    return responsavel.Responsavel.get_or_none(responsavel.Responsavel.cd_responsavel == cd)  

def consultarResponsavel():
    return responsavel.Responsavel.select(responsavel.Responsavel.cd_responsavel.alias('codigo'), responsavel.Responsavel.nm_responsavel.alias('nome')).where(responsavel.Responsavel.cd_responsavel >= 1).order_by(responsavel.Responsavel.nm_responsavel)

def consultarResponsavelPesquisa(flt: list[ger.filtros]):
    
    filtros = []

    for no in flt:
        if no.campo == 'procurar' and no.valor and no.valor != '%':
            filtros.append(
                responsavel.Responsavel.nm_responsavel.contains(no.valor) |
                responsavel.Responsavel.ds_email.contains(no.valor) |
                responsavel.Responsavel.ds_telefone.contains(no.valor)
            )
    
    try:
        dtb.db.connect(reuse_if_open=True)
        
        query = responsavel.Responsavel.select()
        
        if filtros:
            query = query.where(*filtros)         
        # query = query.order_by(responsavel.Responsavel.nm_responsavel).dicts()    
        # return list(query)
        costumerList = [{
            "nm_responsavel": row.nm_responsavel,
            "cd_responsavel": row.cd_responsavel,
            "ds_telefone": row.ds_telefone,
            "ds_email": row.ds_email,            
            "dt_inativo":row.dt_inativo
        } for row in query]        
        return costumerList        

    except OperationalError as e:        
        print(f"❌ Erro ao conectar: {e}")
        return []
    finally:
            # ✅ Garante que o banco feche após processar tudo            
            if not dtb.db.is_closed():
                dtb.db.close()                  
   
def delete(codigo):
    """
    Exclui um trabalho pelo código. Retorna True se excluiu, False caso não exista ou haja erro.
    """
    try:
        dtb.db.connect(reuse_if_open=True)
        resp = consultarResponsavelGet(codigo)

        if not resp:
            return False

        # Usa transação atômica
        with dtb.db.atomic():
            resp.delete_instance()  # delete_instance() é a forma correta no Peewee

        return True

    except OperationalError as e:
        print(f"❌ Erro de banco de dados ao excluir: {e}")
        return False

    finally:
        if not dtb.db.is_closed():
            dtb.db.close()
    
def persistir(responsavelLocal: responsavel.Responsavel):
    try:
        with dtb.db.atomic():
             dtb.db.transaction()
             if responsavelLocal.cd_responsavel != None:
                responsavelLocal.save()
             else:
                responsavelLocal.save(force_insert=True)
             dtb.db.commit()
             return True
    except OperationalError as e:
        print(f"❌ Erro ao salvar na tabela responsável: {e}")
        dtb.db.rollback()
        return False
    
    finally:
        if not dtb.db.is_closed():
            dtb.db.close()