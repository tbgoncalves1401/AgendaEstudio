import streamlit as st
from datetime import datetime, timedelta
import model.cliente as cli
import pandas as pd
import locale
import controller.clienteController as cliController
import geral as gr
import re

# ---------------- LOCALE ----------------
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    if "salvar" not in st.session_state:
        st.session_state.salvar = False        
except:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

def enviar_whatsapp(numero, mensagem):
    import pywhatkit as kit
    kit.sendwhatmsg_instantly(
        phone_no=numero,
        message=mensagem,
        wait_time = 15,
        tab_close = True
    )    

# def logarZap():
#     from playwright.sync_api import sync_playwright

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(storage_state="whatsapp.json")
#         page = context.new_page()

#         page.goto("https://web.whatsapp.com")
#         print("📲 Faça login no WhatsApp Web (QR Code)...")

#         page.wait_for_selector("div[contenteditable='true']", timeout=0)
#         context.storage_state(path="whatsapp.json")

#         print("✅ Login salvo")
#         browser.close()

# def enviar_whatsapp(numero, mensagem):
#     from playwright.sync_api import sync_playwright
#     import urllib.parse
#     import time

#     mensagem = urllib.parse.quote(mensagem)

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         context = browser.new_context(storage_state="whatsapp.json")
#         page = context.new_page()

#         url = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem}"
#         page.goto(url)

#         # espera a caixa de mensagem
#         page.wait_for_selector("div[contenteditable='true']", timeout=30000)
#         time.sleep(2)

#         # ENTER para enviar
#         page.keyboard.press("Enter")
#         time.sleep(3)

#         browser.close()

# ---------------- SESSION STATE ----------------
defaults = {
    "codigo": 0,
    "contador":0,
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
def salvar_cliente(codigo, dados_form)->bool:
    if codigo > 0:
        # Busca o objeto existente
        cliente_obj = cliController.consultarClientedGet(codigo)
    else:
        # Cria um novo objeto
        cliente_obj = cli.Cliente()
        # cliente_obj.cd_cliente = 0

    # Atribui os valores vindos do formulário (dados_form é um dicionário)
    cliente_obj.nm_cliente = dados_form['nm_cliente']
    cliente_obj.ds_email = dados_form['ds_email']
    cliente_obj.ds_telefone = dados_form['ds_telefone']
    cliente_obj.dt_aniversario = dados_form['dt_aniversario']
    # Se estiver usando Peewee ou similar, o controller precisa dar o .save()
    return cliController.persistir(cliente_obj) 

# ---------------- FUNÇÕES AUXILIARES ----------------
def get_codigo_selecionado(response):
    # Verifica se a resposta existe e contém 'selected_rows'
    if response and isinstance(response, dict):
        df = response.get("selected_rows")
        # Verifica se df é um DataFrame e tem ao menos uma linha
        if df is not None and not df.empty:
            return int(df.iloc[0]["Codigo"])  # pega o código da primeira linha
    return 0


def limparCampos():
    st.session_state.update({
        "pesquisou": False,
        "codigo": 0,
        "novoRegistro": False,
        "alterarRegistro": False,
        "excluirRegistro": False,
        "persistir": False,
        "procurar": "",
        "dataIni": datetime.today() - timedelta(days=30),
        "dataFim": datetime.today()
    })

# ---------------- CONSULTA ----------------
def pesquisarCliente():
    # limparCampos()
    if len(st.session_state.procurar) < 3 and st.session_state.procurar != '*':
        st.error(gr.constPesquisar, icon="❌")
        st.session_state['pesquisou'] = False
    else:        
        filtros = []

        if st.session_state.procurar:
            valor = st.session_state.procurar
            filtros.append(gr.filtros("procurar", "%" if valor == "*" else f"{valor}", "string"))

        dados = cliController.consultarClientePesquisa(filtros) or []

        rows = []
        for item in dados:
            rows.append({
                "Nome": item['nm_cliente'],
                "Codigo": item['cd_cliente'],                
                "Telefone": gr.formatar_telefone(item['ds_telefone']),
                "E-Mail": item['ds_email']
            })

        return pd.DataFrame(rows)

# ---------------- FORMULÁRIO ----------------
# @st.dialog("Detalhes do Cliente") # Opcional: transforma o formulário em uma janela flutuante
# def formulario(codigo=0):
#     # 1. Carregar dados se for edição
#     if codigo > 0 :#and "dados_carregados" not in st.session_state:
#         cliente = cliController.consultarClientedGet(codigo)
#     else:
#         cliente = cli.Cliente()

#     with st.form("form_registro", clear_on_submit=False):
#         st.subheader("Edição de Cliente" if codigo > 0 else "Novo Cliente")
#         nome = st.text_input("Nome do cliente", value = cliente.nm_cliente or '')       
#         email = st.text_input("E-mail", value = cliente.ds_email or '', max_chars=180, placeholder="exemplo@email.com", help="Informe um endereço de e-mail válido")    
#         telefone = st.text_input("Telefone", value = cliente.ds_telefone or '', max_chars=20, placeholder="(99)99999-9999", help="Informe um celular válido para receber mensagem via WathsApp")
#         aniversario = st.date_input('Aniversário', value=cliente.dt_aniversario or datetime.today() , format='DD/MM/YYYY', min_value=datetime(1900, 1, 1))

#         btn_salvar = st.form_submit_button("💾 Gravar")
#         if btn_salvar:    
#             ok = False
#             if not nome:
#                 st.error("Campo Nome do cliente vazio!!!", icon="❌")
#             elif not email:
#                 st.error("Campo E-Mail vazio!!!", icon="❌")
#             elif not telefone:
#                 st.error("Campo Telefone vazio!!!", icon="❌")
#             if email:
#                 padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#                 if not re.match(padrao, email):
#                     st.error("E-mail inválido !", icon="❌")
#                 else:
#                     ok = True    
#             if ok:
#                 # Organiza os dados para a função de salvar
#                 pacote_dados = {
#                     "nm_cliente": nome,
#                     "ds_email": email,
#                     "ds_telefone": telefone,
#                     "dt_aniversario":aniversario
#                 }
                
#                 if salvar_cliente(codigo, pacote_dados):
#                     st.success("Salvo com sucesso!")
#                     # Limpa estados para fechar o formulário e resetar busca
#                     if "dados_carregados" in st.session_state:
#                         del st.session_state.dados_carregados
#                     st.session_state.alterarRegistro = False
#                     st.session_state.novoRegistro = False
#                     st.session_state.codigo = -1
#                     st.rerun()
#                 else:    
#                     st.error("Cliente não foi salvo!", icon="❌")

# ---------------- FORMULÁRIO ----------------
@st.dialog("Detalhes do Cliente")
def formulario(codigo=0):
    # 1. Carregar dados se for edição
    if codigo > 0:
        cliente = cliController.consultarClientedGet(codigo)
        # ### NOVO ###: Formata o telefone que vem do banco para exibição inicial
        telefone_inicial = gr.formatar_telefone(cliente.ds_telefone or "")
    else:
        cliente = cli.Cliente()
        telefone_inicial = "" # Para um novo cliente, o campo começa vazio

    with st.form("form_registro", clear_on_submit=False):
        st.subheader("Edição de Cliente" if codigo > 0 else "Novo Cliente")
        
        nome = st.text_input("Nome do cliente", value=cliente.nm_cliente or '')
        email = st.text_input("E-mail", value=cliente.ds_email or '', max_chars=180, placeholder="exemplo@email.com", help="Informe um endereço de e-mail válido")
        
        telefone_digitado = st.text_input(
            "Telefone", 
            value=telefone_inicial, 
            max_chars=20, 
            placeholder="(99)99999-9999", 
            help="Informe um celular válido para receber mensagem via WathsApp"
        )
        
        aniversario = st.date_input('Aniversário', value=cliente.dt_aniversario or datetime.today(), format='DD/MM/YYYY', min_value=datetime(1900, 1, 1))

        btn_salvar = st.form_submit_button("💾 Gravar")
        
        if btn_salvar:
            ok = False
            telefone_limpo = re.sub(r'\D', '', telefone_digitado) # Limpa o que foi digitado

            if not nome:
                st.error("Campo Nome do cliente vazio!!!", icon="❌")
            elif not email:
                st.error("Campo E-Mail vazio!!!", icon="❌")
            elif not telefone_digitado:
                st.error("Campo Telefone vazio!!!", icon="❌")
            elif len(telefone_limpo) < 10: # Valida o número de dígitos
                st.error("Número de telefone inválido ou incompleto!", icon="❌")
            elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                st.error("E-mail inválido !", icon="❌")
            else:
                ok = True
                
            if ok:
                # Organiza os dados para a função de salvar
                pacote_dados = {
                    "nm_cliente": nome,
                    "ds_email": email,
                    "ds_telefone": telefone_limpo,  # Salva o valor já limpo (só números)
                    "dt_aniversario": aniversario
                }
                
                if salvar_cliente(codigo, pacote_dados):
                    st.success("Salvo com sucesso!")
                    
                    # Limpa estados para fechar o formulário e resetar busca
                    # (Seu código de reset existente)
                    if "dados_carregados" in st.session_state:
                        del st.session_state.dados_carregados
                    st.session_state.alterarRegistro = False
                    st.session_state.novoRegistro = False
                    st.session_state.codigo = -1
                    st.rerun()
                else:
                    st.error("Cliente não foi salvo!", icon="❌")




# ---------------- TELA ----------------
st.title("Cliente")

with st.form("Cliente"):
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

enviarZap = False#st.button('Enviar', on_click=lambda: st.session_state.update({"enviarZap": True}))

response = None

if st.session_state.pesquisou:
    df = pesquisarCliente()
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

elif enviarZap and st.session_state.contador == 0:
    telefone = '27996340081'
    enviar = cliController.consultarClientes()
    enviarZap = False
    novoRegistro = False
    alterarRegistro = False  
    logar = False         
    for envio in enviar:
        telefone = envio.ds_telefone
        mensagem = 'Oi '+envio.nm_cliente+', teste de envio de mensagem pelo Zap usando pyhton! *Não responda!!!*'
        st.session_state.contador = st.session_state.contador +1
        enviar_whatsapp("+55"+telefone, mensagem=mensagem+"🎯")    


elif ('excluirRegistro' in st.session_state and st.session_state.excluirRegistro):
    if "caixaDialogoSimNao" in st.session_state:
        del st.session_state.caixaDialogoSimNao
    if not response or 'selected_rows' not in response or response['selected_rows'] is None:
        gr.caixaDialogoInformacao(mensagem='Não existe nada selecionado no grid!', msgBotaoOk='Ok')
    elif(response['selected_rows'].iloc[0].Codigo >=1):
        codigo = response['selected_rows'].iloc[0].Codigo
        gr.caixaDialogoSimNao(mensagem='Deseja realmente excluir o cliente selecionado?', msgBotaoOk='Sim, excluir', msgBotaoCancel='Cancelar exclusão')
    st.session_state.excluir = False         
    del st.session_state.excluirRegistro

if "caixaDialogoSimNao" in st.session_state:
    selected = response.get('selected_rows')
    if selected is not None and len(selected) > 0:          
        if (selected.iloc[0].Codigo >= 1) and st.session_state.caixaDialogoSimNao:
            del st.session_state.caixaDialogoSimNao
            cliController.delete(response['selected_rows'].iloc[0].Codigo)            
            st.rerun()            


