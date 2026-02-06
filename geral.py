import streamlit as st
import numpy as np
from streamlit_modal import Modal
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import requests
import conexao.databasePeewe as db
from datetime import datetime
import re

UFs = [
'AC-Acre','AL-Alagoas','AP-Amapá','AM-Amazonas','BA-Bahia','CE-Ceará','DF-Distrito Federal','ES-Espirito Santo',
'GO-Goiás','MA-Maranhão','MS-Mato Grosso do Sul','MT-Mato Grosso','MG-Minas Gerais','PA-Pará','PB-Paraíba','PR-Paraná',
'PE-Pernambuco','PI-Piauí','RJ-Rio de Janeiro','RN-Rio Grande do Norte','RS-Rio Grande do Sul','RO-Rondônia','RR-Roraima',
'SC-Santa Catarina','SP-São Paulo','SE-Sergipe','TO-Tocantins',]

constPesquisar = 'Precisa-se de 3 caracteres ou o caracter especial ''*'''

class filtros:
    def __init__(self, campo: str, valor: str, tipo: str):
        self.campo = campo
        self.valor = valor
        self.tipo = tipo


def formatar_telefone(numero):
    """
    Formata um número de telefone aplicando a máscara (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.
    Remove todos os caracteres não numéricos antes de formatar.
    """
    if not numero:
        return ""
    numeros_limpos = re.sub(r'\D', '', numero)
    numeros_limpos = numeros_limpos[:11]

    if len(numeros_limpos) <= 2:
        return f'({numeros_limpos}'
    elif len(numeros_limpos) <= 6:
        return f'({numeros_limpos[:2]}) {numeros_limpos[2:]}'
    elif len(numeros_limpos) <= 10:
        return f'({numeros_limpos[:2]}) {numeros_limpos[2:6]}-{numeros_limpos[6:]}'
    else:
        return f'({numeros_limpos[:2]}) {numeros_limpos[2:7]}-{numeros_limpos[7:]}'


def clear_text():
    st.session_state["meu_input_texto"] = ""

# # Se o usuário clicar em um botão dentro da tabela, a ação será registrada aqui
# def handle_action(row_id, action):
#     if 'log_acoes' not in st.session_state:
#         st.session_state.log_acoes = []
#     st.session_state.log_acoes.append(f"[{action}] ID: {row_id} (Re-execução de app)")

# CÓDIGO JAVASCRIPT/HTML PARA OS BOTÕES DE AÇÃO (Renderizador)
# Este JS chama a função handle_action do Python com a linha ID e a ação desejada
action_buttons_html = """
function(params) {
    var row_id = params.data.ID;
    
    // Funções chamadas no escopo pai (Streamlit)
    var edit_btn = `<button onclick="window.parent.handle_action(${row_id}, 'EDITAR')" style="background-color:#4CAF50; color:white; border:none; padding: 5px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 12px; cursor: pointer; margin-right: 5px; border-radius: 5px;">Editar</button>`;
    
    var delete_btn = `<button onclick="window.parent.handle_action(${row_id}, 'EXCLUIR')" style="background-color:#f44336; color:white; border:none; padding: 5px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 12px; cursor: pointer; border-radius: 5px;">Excluir</button>`;
    
    return edit_btn + delete_btn;
}
"""    


def maxCodigo(tabela, campo):
    SQL = 'SELECT MAX('+campo+')+1 FROM '+tabela
    db.cursor.execute(SQL)

    for row in db.cursor.fetchall():
        maximo = row[0]
    if db.cursor.rowcount > 0:
        return maximo
    else:
        return 0

def safe(v):
    """
    Converte '', 'NULL' e None -> None
    Mantém os demais valores intactos
    """
    if v is None:
        return None
    if isinstance(v, str) and v.strip().upper() == "NULL":
        return None
    if v == "":
        return None
    return v

def paginarMostrar(df,colunasInvisiveis, KEY:str=''):
    PAGE_SIZE = 10 # Número de linhas por página que queremos mostrar por vez

    if df is None or df.empty:
        return None  # ou uma mensagem no Streamlit 

    # --- Inicialização do Estado da Sessão ---
    if KEY:
        if 'page'+KEY not in st.session_state:
            st.session_state['page' + KEY] = 1
    else:
        if 'page' not in st.session_state:
            st.session_state.page = 1

    # --- Lógica de Paginação ---
    total_rows = len(df)
    total_pages = int(np.ceil(total_rows / PAGE_SIZE))

    def next_page():
        # Garante que não ultrapasse a última página
        if KEY:
            if st.session_state['page' + KEY] < total_pages:
                st.session_state['page' + KEY] += 1
        else:    
            if st.session_state.page < total_pages:
                st.session_state.page += 1

    def prev_page():
        # Garante que não vá abaixo da primeira página
        if KEY:
            if st.session_state['page' + KEY] > 1:
                st.session_state['page' + KEY] -= 1
        else:    
            if st.session_state.page > 1:
                st.session_state.page -= 1

####Código novo
    if KEY:
        if st.session_state['page' + KEY] > total_pages:
            st.session_state['page' + KEY] = total_pages
            if total_pages == 0:
                st.session_state['page' + KEY] = 1 
    else:    
        if st.session_state.page > total_pages:
            st.session_state.page = total_pages
            if total_pages == 0:
                st.session_state.page = 1 
####            

    # --- Preparação e Exibição do AgGrid ---    

    # 1. FATIA O DATAFRAME para a página atual (Lógica Manual)
    if KEY:
        start_index = (st.session_state['page' + KEY] - 1) * PAGE_SIZE
    else:    
        start_index = (st.session_state.page - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    df_page = df.iloc[start_index:end_index]

    # 2. Configuração do AgGrid
    gb = GridOptionsBuilder.from_dataframe(df_page)

    # Se o DataFrame fatiado estiver vazio (caso total_pages seja 0)
    if df_page.empty and total_rows > 0:
        st.error("Erro de Paginação: DataFrame fatiado está vazio.")        
        return    

    # IMPORTANTE: Desabilita a paginação interna do AgGrid
    gb.configure_grid_options(enablePagination=False) 

    # --- Configuração das Colunas (Para ocultar/adicionar ações) ---
    column_defs = []
    
    # Configura todas as colunas existentes para serem visíveis e interativas
    for col in df_page.columns:
        # Define as colunas que devem ser ocultadas        
        if col == 'ID' or col == 'Código': # ID e STATUS agora estão invisíveis
        #if col == colunaInvisivel:
             column_defs.append({
                "headerName": col,
                "field": col,
                "hide": True, # <--- COMANDO PARA OCULTAR
            })             
        else: # Colunas visíveis
            column_defs.append({
                "headerName": col,
                "field": col,
                "sortable": True,
                "filter": True,
                "resizable": True,
            })           


    # Adiciona a coluna de AÇÕES com os botões
    # column_defs.append({
    #     "headerName": "Ações",
    #     "field": "Acoes",
    #      "cellRenderer": action_buttons_html, # Renderer customizado com os botões
    #     "minWidth": 180,
    #     "maxWidth": 180,
    #     "resizable": False,
    #     "sortable": False 
    # })
    
    gb.configure_columns(column_defs)
    for coluna in colunasInvisiveis:
        gb.configure_column(coluna, hide=True)
    gb.configure_selection('single', use_checkbox=True, suppressRowClickSelection=True)        
    gridOptions = gb.build()

    # --- Interface de Navegação (Botões e Status) ---
    
    # st.markdown("---")
    grid_response = AgGrid(
            df_page, 
            gridOptions=gridOptions, 
            allow_unsafe_jscode=True,
            height=350, 
            width='100%', 
            fit_columns_on_grid_load=True,
             update_mode=GridUpdateMode.MODEL_CHANGED # Garante que atualiza ao mudar a página
        ) 

    # Layout dos botões e status
    col_prev, col_status, col_next = st.columns([1, 1, 1])

    if KEY:
        with col_prev:
            st.button(
            # st.form_submit_button(
                "⬅️ Anterior", 
                on_click=prev_page, 
                disabled=(st.session_state['page' + KEY] == 1),
                key=KEY+'p'
            )

        with col_next:
            st.button(
            # st.form_submit_button(
                "Próximo ➡️", 
                on_click=next_page, 
                disabled=(st.session_state['page' + KEY] == total_pages),
                key=KEY+'n'
            )

        with col_status:
            if KEY:
                st.markdown(f"**Página {st.session_state['page' + KEY]} de {total_pages}**") 
            else:    
                st.markdown(f"**Página {st.session_state.page} de {total_pages}**") 
    else:    

        with col_prev:
            st.button(
            # st.form_submit_button(
                "⬅️ Anterior", 
                on_click=prev_page, 
                disabled=(st.session_state.page == 1)
            )

        with col_next:
            st.button(
            # st.form_submit_button(
                "Próximo ➡️", 
                on_click=next_page, 
                disabled=(st.session_state.page == total_pages)
            )

        with col_status:
            if KEY:
                st.markdown(f"**Página {st.session_state['page' + KEY]} de {total_pages}**") 
            else:    
                st.markdown(f"**Página {st.session_state.page} de {total_pages}**") 

    return grid_response

@st.dialog("Confirmação")
def caixaDialogoSimNao(mensagem: str, msgBotaoOk: str, msgBotaoCancel:str):
    st.warning("⚠️ "+mensagem)
    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("✅ "+msgBotaoOk, use_container_width=True):
            st.session_state.caixaDialogoSimNao = True          
    with col2:
        if st.button("❌ "+msgBotaoCancel, use_container_width=True, type="primary"):
            st.session_state.caixaDialogoSimNao = False            
    if "caixaDialogoSimNao" in st.session_state:
        if st.session_state.caixaDialogoSimNao == True:
            st.rerun()
        elif not st.session_state.caixaDialogoSimNao:
            st.rerun()

@st.dialog("Informação") 
def caixaDialogoInformacao(mensagem: str, msgBotaoOk: str):
    st.warning("⚠️ "+mensagem)
    col1,col2,col3 = st.columns(3, gap="small")
    with col2:
        if st.button("✅ "+msgBotaoOk, use_container_width=True):
            st.session_state.caixaDialogoInformacao = True
            st.rerun()
    if "caixaDialogoInformacaoo" in st.session_state:
        if st.session_state.caixaDialogoInformacao == True:
            st.rerun()
        # elif not st.session_state.caixaDialogoInformacao:
        #     st.rerun()

def consultar_cep_viacep(cep):
    # Formata o CEP para conter apenas números
    cep = cep.replace('-', '').replace('.', '')     
    url = f"https://viacep.com.br/ws/{cep}/json/"    
    try:
        response = requests.get(url)
        data = response.json()        
        # Verifica se houve erro na consulta (ex: CEP inválido)
        if 'erro' in data and data['erro']:
            return "Erro: CEP não encontrado ou inválido."        
        return data        
    except requests.exceptions.RequestException as e:
        return f"Erro na requisição: {e}"        
    
def encontrar_index_por_codigo(lista_opcoes, codigo_desejado):
    if not lista_opcoes:
        return 0
    codigo_desejado = str(codigo_desejado)
    for index, item in enumerate(lista_opcoes):
        item_codigo = str(item.get('codigo', ''))
        if item_codigo == codigo_desejado:
            return index

def consultarEmpmaComboTipo(tipo:str, comando:str):
    if len(comando) == 0:
        SQL = 'SELECT CD_EMPMA, NM_EMPMA FROM EMPMA WHERE CD_EMPMA >= 1000 AND ID_EMPMA_TIPO = ? ORDER BY NM_EMPMA'
    else:
        SQL = comando            
    if tipo != '':
        db.cursor.execute(SQL,(tipo,))        
    else:    
        db.cursor.execute(SQL)
    rows = db.cursor.fetchall()   
    return [{'codigo':r[0], 'nome':r[1]} for r in rows]

def get_codigo_selecionado(response):
    # Verifica se a resposta existe e contém 'selected_rows'
    if response and isinstance(response, dict):
        df = response.get("selected_rows")
        # Verifica se df é um DataFrame e tem ao menos uma linha
        if df is not None and not df.empty:
            return int(df.iloc[0]["Codigo"])  # pega o código da primeira linha
    return 0

def consultarCombo(tabela):
    import controller.clienteController as cli
    import controller.responsavelController as resp
    import controller.trabalhoController as trab
    if tabela == 'cliente':
        combo = cli.consultarClientes()
    elif tabela == 'trabalho':
        combo = trab.consultarTrabalho()
    elif tabela == 'responsavel':
        combo = resp.consultarResponsavel()
    return [{'codigo': r.codigo, 'nome': r.nome} for r in combo]


# def preencherComboEmpresa(tipo, comandoSQL = '', mensagemVazio = ''):
def preencherComboEmpresa(tabela, mensagemVazio):
    # resultado = consultarEmpmaComboTipo(tipo, comando=comandoSQL)
    resultado = consultarCombo(tabela=tabela)
    if mensagemVazio == '':
        novo_objeto = {'codigo': None, 'nome': '>> SELECIONE UM FORNECEDOR <<'}
    else:
        novo_objeto = {'codigo':None, 'nome': mensagemVazio}
    resultado.insert(0, novo_objeto)    
    return resultado


def formatar_data(data_iso):
    if not data_iso:
        return ""
    return datetime.fromisoformat(data_iso).strftime("%d/%m/%Y %H:%M")