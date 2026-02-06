import model.trabalho as trabalho
from typing import List
from datetime import datetime
import conexao.databasePeewe as dtb
from peewee import OperationalError
import geral as ger

def consultartrabalhoGet(cd):
    return trabalho.Trabalho.get_or_none(trabalho.Trabalho.cd_trabalho == cd)  

def consultarTrabalho():
    return trabalho.Trabalho.select(trabalho.Trabalho.cd_trabalho.alias('codigo'), trabalho.Trabalho.nm_trabalho.alias('nome')).where(trabalho.Trabalho.cd_trabalho >= 1).order_by(trabalho.Trabalho.nm_trabalho)

def consultarTrabalhoPesquisa(flt: list[ger.filtros]):
    filtros = []
    for no in flt:
        if (no.campo == 'procurar' and no.valor) and no.valor != '%':
            filtros.append(
                trabalho.Trabalho.nm_trabalho.contains(no.valor) |
                trabalho.Trabalho.ds_trabalho.contains(no.valor)   
            )

    try:
        dtb.db.connect(reuse_if_open=True)

        query = trabalho.Trabalho.select()

        if filtros:
            query = query.where(*filtros)
        query = query.order_by(trabalho.Trabalho.nm_trabalho)

        costumerList = [{
            "cd_trabalho": row.cd_trabalho,
            "nm_trabalho": row.nm_trabalho,
            "ds_trabalho": row.ds_trabalho,
            "qt_tempo":row.qt_tempo
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
    try:        
        print('DELETAR')
        dtb.db.connect(reuse_if_open=True)        
        dtb.db.transaction()
        trb = consultartrabalhoGet(codigo)
        if trb:
            trb.delete()
            dtb.db.commit()
            dtb.db.close()        
            return True
        else:
            return False
    except OperationalError as e:
        dtb.db.rollback()
        print(f"❌ Erro de banco de dados ao excluir: {e}")
        return False
    
def persistir(trabalhoLocal: trabalho.Trabalho):
    try:
        with dtb.db.atomic():
             dtb.db.transaction()
             if trabalhoLocal.cd_trabalho >= 1:
                trabalhoLocal.save()
             else:
                trabalhoLocal.save(force_insert=True)
             dtb.db.commit()
             return True
    except OperationalError as e:
        print(f"❌ Erro ao salvar cliente: {e}")
        dtb.db.rollback()
        return False
    
    finally:
        if not dtb.db.is_closed():
            dtb.db.close()