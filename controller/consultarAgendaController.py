import model.trabalhando as trabalhando
import model.cliente as cnt
import model.trabalho as trb
import model.responsavel as resp
from typing import List
from datetime import datetime, timedelta, time
import conexao.databasePeewe as dtb
from peewee import OperationalError
from peewee import fn, JOIN
import geral as ger
import calendar

def status(idtrb):
    import controller.trabalhandoController as t
    trb = t.consultarTrabalhoGet(idtrb).id_status or None
    return trb

def getCliente(cdCli):
    import controller.clienteController as cl
    cli = cl.consultarClientedGet(cdCli) or None
    return cli

def confirmarExecucao(idtrb):
    import controller.trabalhandoController as t    
    try:        
        with dtb.db.atomic():                          
             dtb.db.transaction()
             trb = t.consultarTrabalhoGet(idtrb)
             trb.id_status = 'E'
             trb.dt_finalizado = datetime.now()
             trb.save()
             dtb.db.commit()
             return True
    except OperationalError as e:
        print(f"❌ Erro ao confirmar execução de trabalho: {e}")
        dtb.db.rollback()
        return False    

def confirmarCancelamento(idtrb):
    import controller.trabalhandoController as t    
    try:        
        with dtb.db.atomic():                          
             dtb.db.transaction()
             trb = t.consultarTrabalhoGet(idtrb)
             trb.id_status = 'C'
             trb.dt_finalizado = datetime.now()
             trb.save()
             dtb.db.commit()
             return True
    except OperationalError as e:
        print(f"❌ Erro ao confirmar cancelamento de trabalho: {e}")
        dtb.db.rollback()
        return False    

def consultarAgenda(opcao):
    # print('opção:', str(opcao))
    filtros = []
    cliente = cnt.Cliente.alias()
    trabalh = trb.Trabalho.alias()
    responsavel = resp.Responsavel.alias()
    hoje = datetime.now() 
    inicio_hoje = datetime.combine(hoje.date(), time.min)
    fim_hoje = datetime.combine(hoje.date(), time.max)

    if (opcao == 1): # Hoje
        filtros.append(trabalhando.Trabalhando.dt_inicio.between(inicio_hoje, fim_hoje))

    elif (opcao == 2): # Amanhã
        amanha = hoje + timedelta(days=1)
        inicio_amanha = datetime.combine(amanha.date(), time.min)
        fim_amanha = datetime.combine(amanha.date(), time.max)
        filtros.append(trabalhando.Trabalhando.dt_inicio.between(inicio_amanha, fim_amanha))

    elif (opcao == 3): # Próximos 7 dias (Semana)
        fim_semana = hoje + timedelta(days=7)
        filtros.append(trabalhando.Trabalhando.dt_inicio.between(hoje, fim_semana))

    elif (opcao == 4): # Próxima Quinzena
        fim_quinzena = hoje + timedelta(days=15)
        filtros.append(trabalhando.Trabalhando.dt_inicio.between(hoje, fim_quinzena))
    elif (opcao >= 5): # Mês, Bimestre, Trimestre, Semestre, Ano
        data_inicio = hoje.replace(day=1, hour=0, minute=0, second=0)
        mes = hoje.month
        ano = hoje.year

        if opcao == 5: # Mês Atual
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            data_fim = hoje.replace(day=ultimo_dia, hour=23, minute=59, second=59)
        
        elif opcao == 6: # Bimestre
            mes_inicio = mes if mes % 2 != 0 else mes - 1
            data_inicio = hoje.replace(month=mes_inicio, day=1, hour=0)
            mes_fim = mes_inicio + 1
            ultimo_dia = calendar.monthrange(ano, mes_fim)[1]
            data_fim = hoje.replace(month=mes_fim, day=ultimo_dia, hour=23)

        elif opcao == 7: # Trimestre
            trimestre_atual = (mes - 1) // 3
            data_inicio = hoje.replace(month=(trimestre_atual * 3) + 1, day=1, hour=0)
            mes_fim = (trimestre_atual * 3) + 3
            ultimo_dia = calendar.monthrange(ano, mes_fim)[1]
            data_fim = hoje.replace(month=mes_fim, day=ultimo_dia, hour=23)

        elif opcao == 8: # Semestre
            mes_inicio = 1 if mes <= 6 else 7
            data_inicio = hoje.replace(month=mes_inicio, day=1, hour=0)
            mes_fim = 6 if mes <= 6 else 12
            ultimo_dia = calendar.monthrange(ano, mes_fim)[1]
            data_fim = hoje.replace(month=mes_fim, day=ultimo_dia, hour=23)

        elif opcao == 9: # Ano
            data_inicio = hoje.replace(month=1, day=1, hour=0)
            data_fim = hoje.replace(month=12, day=31, hour=23)

        # O segredo do filtro "Entre" está aqui:
        filtros.append((trabalhando.Trabalhando.dt_inicio >= data_inicio) & 
                       (trabalhando.Trabalhando.dt_inicio <= data_fim))

    try:
        dtb.db.connect(reuse_if_open=True)

        from peewee import SQL

        # query = (
        #     trabalhando.Trabalhando
        #     .select(
        #         cliente.nm_cliente,
        #         trabalh.nm_trabalho,
        #         responsavel.nm_responsavel,
        #         trabalhando.Trabalhando.id_status,
        #         trabalhando.Trabalhando.cd_trabalhando,
        #         fn.FORMAT(trabalhando.Trabalhando.vl_trabalho, 2).alias('Valor'),
        #         trabalhando.Trabalhando.dt_inicio.alias('DataInicio'),
        #         fn.TIMESTAMPADD(
        #             SQL('HOUR'),
        #             trabalh.qt_tempo,
        #             trabalhando.Trabalhando.dt_inicio
        #         ).alias('DataPrevisaoFim'),
        #           trabalhando.Trabalhando.cd_trabalhando.alias('Codigo')
        #     )
        #     .join(cliente, on=(trabalhando.Trabalhando.cd_cliente == cliente.cd_cliente))
        #     .join(trabalh, on=(trabalhando.Trabalhando.cd_trabalho == trabalh.cd_trabalho))
        #     .join(responsavel, on=(trabalhando.Trabalhando.cd_responsavel == responsavel.cd_responsavel))
        #     # .where(trabalhando.Trabalhando.id_finalizado != True)
        #     .distinct())
        query = (
            trabalhando.Trabalhando
        .select(
            cliente.nm_cliente,
            trabalh.nm_trabalho,
            responsavel.nm_responsavel,
            trabalhando.Trabalhando.id_status,
            trabalhando.Trabalhando.cd_trabalhando,

            fn.TO_CHAR(
                trabalhando.Trabalhando.vl_trabalho,
                'FM999999990.00'
            ).alias('Valor'),

            trabalhando.Trabalhando.dt_inicio.alias('DataInicio'),

            (
                trabalhando.Trabalhando.dt_inicio +
                (trabalh.qt_tempo * SQL("INTERVAL '1 hour'"))
            ).alias('DataPrevisaoFim'),

            trabalhando.Trabalhando.cd_trabalhando.alias('Codigo')
        )
            .join(cliente, on=(trabalhando.Trabalhando.cd_cliente == cliente.cd_cliente))
            .join(trabalh, on=(trabalhando.Trabalhando.cd_trabalho == trabalh.cd_trabalho))
            .join(responsavel, on=(trabalhando.Trabalhando.cd_responsavel == responsavel.cd_responsavel))
            # .where(trabalhando.Trabalhando.id_finalizado != True)
            .distinct())        


        if filtros:
            query = query.where(*filtros)
        query = query.order_by(trabalhando.Trabalhando.dt_inicio).dicts()    
        return list(query)

    except OperationalError as e:
        print(f"❌ Erro ao conectar: {e}")
        return []
    finally:
            # ✅ Garante que o banco feche após processar tudo
            if not dtb.db.is_closed():
                dtb.db.close()   