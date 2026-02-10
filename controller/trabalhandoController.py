import model.trabalhando as trabalhando
from typing import List
from datetime import datetime
import conexao.databasePeewe as dtb
from peewee import OperationalError
from peewee import fn, JOIN
import geral as ger
import model.cliente as cli
import model.trabalho as trb

def consultarTrabalhoGet(cd):
    return trabalhando.Trabalhando.get_or_none(trabalhando.Trabalhando.cd_trabalhando == cd)  

def consultaTrabalhoDet(cd):
    cliente = cli.Cliente.alias()
    trabalh = trb.Trabalho.alias()

    filtros = []

    if cd >= 1:
        filtros.append(
            trabalhando.Trabalhando.cd_trabalhando == cd
        )

    try:
        dtb.db.connect(reuse_if_open=True)

        query = (
            trabalhando.Trabalhando
            .select(
                cliente.nm_cliente,
                trabalh.nm_trabalho,
                fn.ROUND(
                    trabalhando.Trabalhando.vl_trabalho.cast('numeric'), 2
                ).alias('Valor'),
                trabalhando.Trabalhando.dt_inicio.alias('DataInicio'),
                trabalhando.Trabalhando.dt_finalizado.alias('DataFim'),
                trabalhando.Trabalhando.id_status,
                trabalhando.Trabalhando.cd_responsavel,
                trabalhando.Trabalhando.cd_trabalhando.alias('Codigo')
            )
            .join(cliente, on=(trabalhando.Trabalhando.cd_cliente == cliente.cd_cliente))
            .join(trabalh, on=(trabalhando.Trabalhando.cd_trabalho == trabalh.cd_trabalho))
            .distinct()
        )

        if filtros:
            query = query.where(*filtros)

        query = query.order_by(trabalhando.Trabalhando.dt_inicio).dicts()
        print(query.sql())

        return list(query)

    # except OperationalError as e:
    #     print(f"❌ Erro ao conectar: {e}")
    #     return []
    except Exception as e:
        raise


    finally:
        if not dtb.db.is_closed():
            dtb.db.close()


# def consultaTrabalhoDet(cd):
#     cliente = cli.Cliente.alias()
#     trabalh = trb.Trabalho.alias()

#     filtros = []

#     if cd >= 1:
#         filtros.append(
#             trabalhando.Trabalhando.cd_trabalhando == cd
#         )

#     try:
#         dtb.db.connect(reuse_if_open=True)

#         query = (
#             trabalhando.Trabalhando
#             .select(
#                 cliente.nm_cliente,
#                 trabalh.nm_trabalho,
#                 fn.FORMAT(trabalhando.Trabalhando.vl_trabalho, 2).alias('Valor'),
#                 trabalhando.Trabalhando.dt_inicio.alias('DataInicio'),
#                 trabalhando.Trabalhando.dt_finalizado.alias('DataFim'),
#                 trabalhando.Trabalhando.id_status,
#                 trabalhando.Trabalhando.cd_responsavel,                
#                 trabalhando.Trabalhando.cd_trabalhando.alias('Codigo')
#             )
#             .join(cliente, on=(trabalhando.Trabalhando.cd_cliente == cliente.cd_cliente))
#             .join(trabalh, on=(trabalhando.Trabalhando.cd_trabalho == trabalh.cd_trabalho))
#             # .where(trabalhando.Trabalhando.id_finalizado != True)
#             .distinct()
#         )

#         if filtros:
#             query = query.where(*filtros)

#         query = query.order_by(trabalhando.Trabalhando.dt_inicio).dicts()

#         return list(query)


#     except OperationalError as e:
#         print(f"❌ Erro ao conectar: {e}")
#         return []

#     finally:
#         if not dtb.db.is_closed():
#             dtb.db.close()

def consultarTrabalhosPesquisa(flt: list[ger.filtros]):
    cliente = cli.Cliente.alias()
    trabalh = trb.Trabalho.alias()

    filtros = []

    for no in flt:
        if no.campo == 'procurar' and no.valor and no.valor != '%':
            filtros.append(
                cliente.nm_cliente.contains(no.valor) |
                trabalh.nm_trabalho.contains(no.valor)
            )

    try:
        dtb.db.connect(reuse_if_open=True)

        query = (
            trabalhando.Trabalhando
            .select(
                cliente.nm_cliente,
                trabalh.nm_trabalho,
                fn.ROUND(
                    trabalhando.Trabalhando.vl_trabalho.cast('numeric'), 2
                ).alias('Valor'),
                trabalhando.Trabalhando.dt_inicio.alias('DataInicio'),
                trabalhando.Trabalhando.dt_finalizado.alias('DataFim'),
                trabalhando.Trabalhando.id_status,
                trabalhando.Trabalhando.cd_responsavel,
                trabalhando.Trabalhando.cd_trabalhando.alias('Codigo')
            )
            .join(cliente, on=(trabalhando.Trabalhando.cd_cliente == cliente.cd_cliente))
            .join(trabalh, on=(trabalhando.Trabalhando.cd_trabalho == trabalh.cd_trabalho))
            .distinct()
        )

        if filtros:
            query = query.where(*filtros)

        query = query.order_by(trabalhando.Trabalhando.dt_inicio).dicts()

        return list(query)

    except OperationalError as e:
        print(f"❌ Erro ao conectar: {e}")
        return []

    finally:
        if not dtb.db.is_closed():
            dtb.db.close()


# def consultarTrabalhosPesquisa(flt: list[ger.filtros]):
#     cliente = cli.Cliente.alias()
#     trabalh = trb.Trabalho.alias()

#     filtros = []

#     for no in flt:
#         if no.campo == 'procurar' and no.valor and no.valor != '%':
#             filtros.append(
#                 cliente.nm_cliente.contains(no.valor) |
#                 trabalh.nm_trabalho.contains(no.valor)
#             )

#     try:
#         dtb.db.connect(reuse_if_open=True)

#         query = (
#             trabalhando.Trabalhando
#             .select(
#                 cliente.nm_cliente,
#                 trabalh.nm_trabalho,
#                 fn.FORMAT(trabalhando.Trabalhando.vl_trabalho, 2).alias('Valor'),
#                 trabalhando.Trabalhando.dt_inicio.alias('DataInicio'),
#                 trabalhando.Trabalhando.dt_finalizado.alias('DataFim'),
#                 trabalhando.Trabalhando.id_status,
#                 trabalhando.Trabalhando.cd_responsavel,
#                 trabalhando.Trabalhando.cd_trabalhando.alias('Codigo')
#             )
#             .join(cliente, on=(trabalhando.Trabalhando.cd_cliente == cliente.cd_cliente))
#             .join(trabalh, on=(trabalhando.Trabalhando.cd_trabalho == trabalh.cd_trabalho))
#             # .where(trabalhando.Trabalhando.id_finalizado != True)
#             .distinct()
#         )

#         if filtros:
#             query = query.where(*filtros)

#         query = query.order_by(trabalhando.Trabalhando.dt_inicio).dicts()

#         return list(query)


#     except OperationalError as e:
#         print(f"❌ Erro ao conectar: {e}")
#         return []

#     finally:
#         if not dtb.db.is_closed():
#             dtb.db.close()
   

def delete(codigo):
    """
    Exclui um trabalho pelo código. Retorna True se excluiu, False caso não exista ou haja erro.
    """
    try:
        dtb.db.connect(reuse_if_open=True)
        trab = consultarTrabalhoGet(codigo)

        if not trab:
            return False

        # Usa transação atômica
        with dtb.db.atomic():
            trab.delete_instance()  # delete_instance() é a forma correta no Peewee

        return True

    except OperationalError as e:
        print(f"❌ Erro de banco de dados ao excluir: {e}")
        return False

    finally:
        if not dtb.db.is_closed():
            dtb.db.close()

    
def persistir(trabalhandoLocal: trabalhando.Trabalhando):
    try:
        with dtb.db.atomic():
             dtb.db.transaction()
            #  if trabalhandoLocal.cd_trabalhando >= 1:
             if trabalhandoLocal.cd_trabalhando != None:
                trabalhandoLocal.save()
             else:
                trabalhandoLocal.save(force_insert=True)
             dtb.db.commit()
             return True
    except OperationalError as e:
        print(f"❌ Erro ao salvar na tabela trabalhando: {e}")
        dtb.db.rollback()
        return False
    
    finally:
        if not dtb.db.is_closed():
            dtb.db.close()