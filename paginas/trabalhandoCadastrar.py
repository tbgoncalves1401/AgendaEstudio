import streamlit as st
from datetime import datetime
from model.trabalhando import Trabalhando
import pandas as pd
import locale
import controller.trabalhandoController as trbController
import geral as gr

# ---------------- LOCALE ----------------
# try:
#     locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
#     if "salvar" not in st.session_state:
#         st.session_state.salvar = False        
# except:
#     locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

# ---------------- SESSION STATE ----------------
defaults = {
    "codigo": 0,
    "pesquisou": False,
    "persistir": False,
    "novoRegistro": False,
    "alterarRegistro": False,
    "excluirRegistro": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- CRUD ----------------
def salvar_trabalho(codigo, dados_form)->bool:
    if codigo > 0:
        # Busca o objeto existente
        trabalho_obj = trbController.consultarTrabalhoGet(codigo)
    else:
        # Cria um novo objeto
        trabalho_obj = Trabalhando()
    # Atribui os valores vindos do formulário (dados_form é um dicionário)
    trabalho_obj.cd_trabalho = dados_form['cd_trabalho']
    trabalho_obj.cd_cliente = dados_form['cd_cliente']
    trabalho_obj.cd_responsavel = dados_form['cd_responsavel']
    trabalho_obj.vl_trabalho = dados_form['vl_trabalho']
    trabalho_obj.dt_inicio = dados_form['dt_inicio']

    # Se estiver usando Peewee ou similar, o controller precisa dar o .save()
    return trbController.persistir(trabalho_obj) 

def limparCampos():
    st.session_state.update({
        "pesquisou": False,
        "novoRegistro": False,
        "alterarRegistro": False,
        "excluirRegistro": False,
        "persistir": False,
        "procurar": ""})

# ---------------- CONSULTA ----------------
def pesquisarTrabalho():
    # limparCampos()
    if len(st.session_state.procurar) < 3 and st.session_state.procurar != '*':
        st.error(gr.constPesquisar, icon="❌")
        st.session_state['pesquisou'] = False
    else:        
        filtros = []

        if st.session_state.procurar:
            valor = st.session_state.procurar
            filtros.append(gr.filtros("procurar", "%" if valor == "*" else f"{valor}", "string"))

        dados = trbController.consultarTrabalhosPesquisa(filtros) or []

        rows = []
        for item in dados:
            rows.append({
                "Cliente": item['nm_cliente'],
                "Trabalho agendado": item['nm_trabalho'],                
                "Data para execução": item['DataInicio'],
                "Valor": item['Valor'],
                "Codigo": item['Codigo']
            })

        return pd.DataFrame(rows)

# ---------------- FORMULÁRIO ----------------
@st.dialog("Detalhes da Agenda de Trabalho") # Opcional: transforma o formulário em uma janela flutuante
def formulario(codigo=0):
    # ---------------- SESSION STATE ----------------
    comboCliente = gr.preencherComboEmpresa('cliente', '>> SELECIONE UM CLIENTE <<')
    comboResponsavel = gr.preencherComboEmpresa('responsavel', '>> SELECIONE UM RESPONSÁVEL <<')
    comboTrabalho = gr.preencherComboEmpresa('trabalho', '>> SELECIONE UM TRABALHO <<')

    # 1. Carregar dados se for edição
    if codigo > 0 :#and "dados_carregados" not in st.session_state:
        trabalho = trbController.consultarTrabalhoGet(codigo)
    else:       
        trabalho = Trabalhando()

    with st.form("form_registro", clear_on_submit=False):
        st.subheader("Edição da Agenda de trabalho" if codigo > 0 else "Nova Agenda de Trabalho")
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
                    st.session_state.alterarRegistro = False
                    st.session_state.novoRegistro = False
                    st.session_state.codigo = -1
                    st.rerun()
                else:    
                    st.error("Trabalho não foi salvo!", icon="❌")

# ---------------- TELA ----------------
st.title("Agendar trabalho")

with st.form("Trabalho"):
    # st.header("**Consultar**")

    bt1, bt2, bt3, bt4 , bt5= st.columns([2, 2, 1, 1, 11])
    with bt1:
        st.form_submit_button("🔍 Pesquisar", on_click=lambda: st.session_state.update({"pesquisou": True}))
    with bt2:
        st.form_submit_button("🧹 Limpar", on_click=limparCampos)

    col1, col2, col3 = st.columns([1, 2, 2])
    col1.text_input(label='Procurar:', key='procurar')
####
b1, b2, b3, b4 = st.columns([1, 1, 1, 8])
novoRegistro = b1.button("📄 Cadastrar", on_click=lambda: st.session_state.update({"novoRegistro": True}))
alterarRegistro = b2.button("✏️ Alterar", on_click=lambda: st.session_state.update({"alterarRegistro": True}))
excluirRegistro = b3.button('🗑️ Excluir', on_click=lambda: st.session_state.update({"excluirRegistro": True}))

response = None

if st.session_state.pesquisou:
    df = pesquisarTrabalho()
    if df is not None and not df.empty:
        response = gr.paginarMostrar(df, ["Codigo"])
        selected = response.get('selected_rows')

        if selected is not None and len(selected) > 0:
            st.session_state.codigo = selected.iloc[0].Codigo
            
    else:
        novoRegistro = False
        alterarRegistro = False
        logar = False
        enviarZap = False
        
if novoRegistro:
    novoRegistro = False
    alterarRegistro = False
    enviarZap = False
    logar = False
    formulario(0)        

elif alterarRegistro:    
    novoRegistro = False
    alterarRegistro = False
    enviarZap = False
    logar = False
    selected = response.get('selected_rows')
    if selected is not None and len(selected) > 0 and st.session_state.codigo > 0:
        formulario(st.session_state.codigo)
    else:
        gr.caixaDialogoInformacao(mensagem='Selecione um registro para alterar.', msgBotaoOk='Ok')

elif ('excluirRegistro' in st.session_state and st.session_state.excluirRegistro):
    if "caixaDialogoSimNao" in st.session_state:
        del st.session_state.caixaDialogoSimNao
    if not response or 'selected_rows' not in response or response['selected_rows'] is None:
        gr.caixaDialogoInformacao(mensagem='Não existe nada selecionado no grid!', msgBotaoOk='Ok')
    elif(response['selected_rows'].iloc[0].Codigo >=1):
        codigo = response['selected_rows'].iloc[0].Codigo
        gr.caixaDialogoSimNao(mensagem='Deseja realmente excluir o agendamento selecionado?', msgBotaoOk='Sim, excluir', msgBotaoCancel='Cancelar exclusão')
    st.session_state.excluir = False         
    del st.session_state.excluirRegistro

if "caixaDialogoSimNao" in st.session_state:
    selected = response.get('selected_rows')
    if selected is not None and len(selected) > 0:          
        if (selected.iloc[0].Codigo >= 1) and st.session_state.caixaDialogoSimNao:
            del st.session_state.caixaDialogoSimNao
            trbController.delete(response['selected_rows'].iloc[0].Codigo)            
            st.rerun()            


