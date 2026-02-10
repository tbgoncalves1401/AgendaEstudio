import streamlit as st
from datetime import datetime, timedelta
# import pandas as pd
# import locale
import geral as gr
import controller.consultarAgendaController as consultarAgendaController
import controller.trabalhandoController as trbController
import controller.trabalhoController as trabalhoController
from model.trabalhando import Trabalhando
from streamlit_calendar import calendar
import requests
import urllib.parse


# ---------------- LOCALE ----------------
# try:
#     locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
#     if "salvar" not in st.session_state:
#         st.session_state.salvar = False        
# except:
#     locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# def enviar_whatsapp(numero, mensagem):
#     import pywhatkit as kit
#     kit.sendwhatmsg_instantly(
#         phone_no=numero,
#         message=mensagem,
#         wait_time = 15,
#         tab_close = True
#     )    

def enviar_whatsapp(numero, mensagem):
    # mensagem = urllib.parse.quote(mensagem)
    # url = (
    #     "https://api.callmebot.com/whatsapp.php"
    #     f"?phone={numero}"
    #     f"&text={mensagem}"
    #     f"&apikey=SEU_API_KEY"
    # )
    # requests.get(url)
    mensagem_codificada = urllib.parse.quote(mensagem, safe='')

    return f"https://wa.me/55{numero}?text={mensagem_codificada}"

from datetime import datetime, timedelta

from datetime import datetime, timedelta

# ---------------- SESSION STATE ----------------
defaults = {
    "codigo": 0,
    "pesquisou": False,
    "confirmarExecução": False,
    "confirmarCancelamento": False,
    "remarcarAgenda": False,
    "agendar": False,
    "evento_selecionado": False,
    "enviarZap": False
}

if "evento_selecionado" not in st.session_state:
    st.session_state.evento_selecionado = None

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def limparCampos():
    st.session_state.update({
        "pesquisou": False,
        "evento_selecionado": False,
        "enviarZap": False,
        "codigo": 0
    })

def riscar_texto(texto):
    return ''.join(c + '\u0336' for c in texto)

def salvar_trabalho(codigo, dados_form)->bool:    
    if codigo > 0:
        trabalho_obj = trbController.consultarTrabalhoGet(codigo)
        trabalho_obj.cd_responsavel = dados_form['cd_responsavel']    
        trabalho_obj.dt_inicio = dados_form['dt_inicio']        
    else:
        trabalho_obj = Trabalhando()
        # trabalho_obj.cd_trabalhando = 0
        trabalho_obj.cd_responsavel = dados_form['cd_responsavel']    
        trabalho_obj.dt_inicio = dados_form['dt_inicio']        
        trabalho_obj.cd_trabalho = dados_form['cd_trabalho']
        trabalho_obj.cd_cliente = dados_form['cd_cliente']
        trabalho_obj.vl_trabalho = dados_form['vl_trabalho']
    return trbController.persistir(trabalho_obj) 

# ---------------- FORMULÁRIO ----------------
@st.dialog("Detalhes da Agenda de Trabalho") # Opcional: transforma o formulário em uma janela flutuante
def formulario(codigo=0):    
    comboResponsavel = gr.preencherComboEmpresa('responsavel', '>> SELECIONE UM RESPONSÁVEL <<')

    # 1. Carregar dados se for edição
    if codigo > 0 :#and "dados_carregados" not in st.session_state:
        trabalho = trbController.consultaTrabalhoDet(codigo)
    else:
        trabalho = Trabalhando()    
        comboCliente = gr.preencherComboEmpresa('cliente', '>> SELECIONE UM CLIENTE <<')
        comboResponsavel = gr.preencherComboEmpresa('responsavel', '>> SELECIONE UM RESPONSÁVEL <<')
        comboTrabalho = gr.preencherComboEmpresa('trabalho', '>> SELECIONE UM TRABALHO <<')        
    with st.form("form_registro", clear_on_submit=False):
        st.subheader("Edição da Agenda de trabalho" if codigo > 0 else "Nova Agenda de Trabalho")
        if codigo > 0 :
            for item in trabalho:
                st.text_input("Nome do trabalho", value=item['nm_trabalho'] , disabled=True)
                st.text_input("Nome do cliente", value=item['nm_cliente'] , disabled=True)
                indexResponsavel = item['cd_responsavel']
                v_valor = item['Valor']
                v_data = item['DataInicio']
                indexResponsavel = int(gr.encontrar_index_por_codigo(comboResponsavel, indexResponsavel if codigo > 0 else None))
                v_responsavel = st.selectbox("Nome do responsável", comboResponsavel, format_func=lambda item: item["nome"], index=indexResponsavel)
                v_valor = st.number_input('Valor', value=v_valor, disabled= True)
                v_dataInicio = st.date_input('Data de início', value=v_data or datetime.today(), format='DD/MM/YYYY', min_value=datetime(1900, 1, 1))
                v_hora = st.time_input("Hora de início", value=(v_data.time()), step=60)                
        else:
            indexTrabalho = int(gr.encontrar_index_por_codigo(comboTrabalho, trabalho.cd_trabalho_id if codigo > 0 else None))
            v_trabalho = st.selectbox("Nome do trabalho", comboTrabalho, format_func=lambda item: item["nome"], index=indexTrabalho)
            indexCliente = int(gr.encontrar_index_por_codigo(comboCliente, trabalho.cd_cliente if codigo > 0 else None))
            v_cliente = st.selectbox("Nome do cliente", comboCliente, format_func=lambda item: item["nome"], index=indexCliente)
            indexResponsavel = int(gr.encontrar_index_por_codigo(comboResponsavel, trabalho.cd_responsavel if codigo > 0 else None))                                       
            v_responsavel = st.selectbox("Nome do responsável", comboResponsavel, format_func=lambda item: item["nome"], index=indexResponsavel)
            v_valor = st.number_input('Valor', min_value=0.0, value=trabalho.vl_trabalho or 0.0)
            v_dataInicio = st.date_input('Data de início', value=trabalho.dt_inicio or datetime.today(), format='DD/MM/YYYY', min_value=datetime(1900, 1, 1))
            v_hora = st.time_input("Hora de início", value=(trabalho.dt_inicio.time() if getattr(trabalho, 'dt_inicio', None)else '00:00'), step=60)
        btn_salvar = st.form_submit_button("💾 Gravar")
        if btn_salvar:
            if codigo >0:
                pacote_dados = {
                    "cd_responsavel": v_responsavel['codigo'],
                    "dt_inicio":datetime.combine(v_dataInicio, v_hora)
                }
            else:
                ok = True
                if not v_trabalho:
                    st.error("Campo Trabalho do cliente vazio!!!", icon="❌")
                    ok = False
                elif not v_cliente:
                    st.error("Campo Cliente vazio!!!", icon="❌")
                    ok = False
                if ok:
                    # Organiza os dados para a função de salvar
                    pacote_dados = {
                        "cd_trabalho": v_trabalho['codigo'],
                        "cd_cliente": v_cliente['codigo'],
                        "cd_responsavel": v_responsavel['codigo'],
                        "vl_trabalho":v_valor,
                        "dt_inicio":datetime.combine(v_dataInicio, v_hora)
                    }                    
                
            if salvar_trabalho(codigo, pacote_dados):
                st.success("Salvo com sucesso!")
                # Limpa estados para fechar o formulário e resetar busca
                if "dados_carregados" in st.session_state:
                    del st.session_state.dados_carregados
                st.rerun()
            else:    
                st.error("Trabalho não foi salvo!", icon="❌")

# ---------------- CONSULTA ----------------
def pesquisarAgenda(selecao):
    dados = consultarAgendaController.consultarAgenda(selecao)

    if dados:
        calendar_events = []
        for item in dados:        
            titulo = item.get("nm_responsavel")+'-> '+item.get("nm_trabalho")+' para o cliente: '+item.get("nm_cliente")

            if item.get("id_status") == "C":
                # titulo = "❌ " + riscar_texto(titulo)
                titulo = "🔕 " + riscar_texto(titulo)
            elif item.get("id_status") == "E":
                titulo = "✔️ " + titulo

            evento = {
                "title": titulo,
                "start": item.get("DataInicio").isoformat(),
                "end": item.get("DataPrevisaoFim").isoformat(),
                "id": item.get("cd_trabalhando"),
                "status":str(item.get("id_status"))
            }

            calendar_events.append(evento)

        return calendar_events
    else:
        return None

# ---------------- TELA ----------------
st.title("Consultar agenda")

with st.form("consultaAgenda"):

    bt1, bt2, bt3, bt4 , bt5= st.columns([2, 2, 2, 1, 11])
    with bt1:
        st.form_submit_button("🔍 Pesquisar", on_click=lambda: st.session_state.update({"pesquisou": True}))
    with bt2:
        st.form_submit_button("🧹 Limpar", on_click=limparCampos)
    with bt3:
        st.form_submit_button("📅 Nova agenda", on_click=lambda: st.session_state.update({"agendar": True}))

    col1, col2, col3 = st.columns([1, 2, 2])
    novo_objeto = [{'codigo': 0, 'nome': '>> SELECIONE UMA OPÇÃO <<'},
                   {'codigo': 1, 'nome': 'Hoje'},
                   {'codigo': 2, 'nome': 'Amanhã'},
                   {'codigo': 3, 'nome': 'Semana'},
                   {'codigo': 4, 'nome': 'Quinzena'},
                   {'codigo': 5, 'nome': 'Mês'},
                   {'codigo': 6, 'nome': 'Bimestre'},
                   {'codigo': 7, 'nome': 'Trimestre'},
                   {'codigo': 8, 'nome': 'Semestre'},
                   {'codigo': 9, 'nome': 'Ano'}
                  ]

    opcao = col1.selectbox('Agenda de', novo_objeto,format_func=lambda item: item["nome"], index=0)  


if "mes_atual" not in st.session_state:
    st.session_state.mes_atual = datetime.today().month
    st.session_state.ano_atual = datetime.today().year

agenda = []
state = None
if opcao['codigo'] >=1 and st.session_state.pesquisou:
    agenda = pesquisarAgenda(opcao['codigo'])
    if agenda:
        st.session_state.agenda_raw = {ev["id"]: ev for ev in agenda}

if agenda:   
    st.session_state.agenda_raw = {ev["id"]: ev for ev in agenda}
    calendar_options = {
        "editable": True,
        "selectable": True,
        "initialView": "dayGridMonth",
        "initialDate": datetime(st.session_state.ano_atual, st.session_state.mes_atual, 1).isoformat(),
        "locale": "pt-br",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "buttonText": {
            "today": "Hoje",
            "month": "Mês",
            "week": "Semana",
            "day": "Dia",
            "list": "Lista"
        }
    }

    state = calendar(events=agenda, options=calendar_options)

if state and state.get("dateClick"):
    st.session_state.evento_selecionado = None

if state and state.get("eventClick"):
    ev_click = state["eventClick"]["event"]
    ev_id = ev_click.get("id")

    ev_full = st.session_state.agenda_raw.get(ev_id) 

    st.session_state.evento_selecionado = {
        "id": ev_id,
        "title": ev_click.get("title"),
        "start": ev_click.get("start"),
        "end": ev_click.get("end")
    }

if "agendar" in st.session_state and st.session_state.agendar:
    formulario(-1)
    st.session_state.agendar = False    

if st.session_state.evento_selecionado:
    ev = st.session_state.evento_selecionado

    with st.expander("📌 Detalhes do agendamento", expanded=True):

        st.markdown(f"**Evento:** {ev['title']}")
        inicio = gr.formatar_data(ev["start"])
        fim = gr.formatar_data(ev["end"])      
        st.markdown(f"**Início:** {inicio}")
        st.markdown(f"**Fim:** {fim}") 
        cd = int(ev['id'])
        # status = consultarAgendaController.status(cd)      
        aux = trbController.consultarTrabalhoGet(cd)
        status = aux.id_status

        if status == 'A':
            col1, col2, col3, col4, col5 = st.columns([3, 4, 3, 3, 10])

            confirmarExecucao = col1.button("✔️ Confirmar execução", on_click=lambda: st.session_state.update({"confirmarExecução": True}))
            confirmarCancelamento = col2.button("🔕 Cancelar agendamento", on_click=lambda: st.session_state.update({"confirmarCancelamento": True}))
            remarcarAgenda = col3.button("😬 Remarcar", on_click=lambda: st.session_state.update({"remarcarAgenda": True}))
            if  datetime.fromisoformat(ev['start']) > datetime.now().astimezone():#Só vai enviar mensagem se a data de início da tarefa for maior que a data atual
                # enviarZap = col4.button("📲 WhatsApp", on_click=lambda: st.session_state.update({"enviarZap": True}))
                enviarZap = col4.button("📲 Gerar WhatsApp", on_click=lambda: st.session_state.update({"enviarZap": True}))

            if confirmarExecucao:
                consultarAgendaController.confirmarExecucao(cd)
                st.rerun()
            elif confirmarCancelamento:
                gr.caixaDialogoSimNao(mensagem='Deseja realmente cancelar a agenda?', msgBotaoOk='Sim', msgBotaoCancel='Não')
                # del st.session_state.confirmarCancelamento                
            elif remarcarAgenda:
                formulario(cd) 
            elif enviarZap:
                import re
                # cliente = re.sub(r"\D", "", consultarAgendaController.getCliente(aux.cd_cliente))
                cliente = consultarAgendaController.getCliente(aux.cd_cliente)
                trabalho = trabalhoController.consultartrabalhoGet(aux.cd_trabalho)            
                # enviar_whatsapp(numero='+55'+re.sub(r"\D", "", cliente.ds_telefone),mensagem= 'Olá '+cliente.nm_cliente+', aqui é do *Estúdio Gruta*. Lembrete de '+trabalho.nm_trabalho+' *'+
                #                                                             str(aux.dt_inicio.strftime('%d/%m/%Y'))+' às '+str(aux.dt_inicio.strftime('%H:%M'))+"* 🎯")
                envio = enviar_whatsapp(numero= re.sub(r"\D", "", cliente.ds_telefone),mensagem= 'Olá '+cliente.nm_cliente+', aqui é do *Estúdio Gruta*. Lembrete de '+trabalho.nm_trabalho+' *'+
                                                                            str(aux.dt_inicio.strftime('%d/%m/%Y'))+' às '+str(aux.dt_inicio.strftime('%H:%M'))+"*")
                st.markdown(f"[📲 Abrir WhatsApp]({envio})", unsafe_allow_html=True)

            if "caixaDialogoSimNao" in st.session_state and st.session_state.caixaDialogoSimNao:
                consultarAgendaController.confirmarCancelamento(cd)
                del st.session_state.caixaDialogoSimNao
                st.rerun()    
            else:
                st.session_state.confirmarCancelamento = False
                if "caixaDialogoSimNao" in st.session_state:
                    del st.session_state.caixaDialogoSimNao