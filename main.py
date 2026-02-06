import streamlit as st;


st.set_page_config(page_title="Agenda", layout="wide")

def menu_page():
    # st.markdown("""
    # <style>
    # header {visibility: hidden;}
    # .top-banner {
    #     position: sticky;
    #     top: 0;
    #     background-color: #5a8bed;
    #     padding: 15px;
    #     color: white;
    #     font-size: 24px;
    #     z-index: 1000;
    # }
    # </style>

    # <div class="top-banner">
    #     🐆 SISTEMA DE MARCAÇÃO AGENDA ESTÚDIO GRUTA
    # </div>
    # """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .banner {
            background-color: #dfe88e; /* Cor de fundo */
            padding: 20px;             /* Espaçamento interno */
            color: black;              /* Cor do texto */
            font-size: 24px;           /* Tamanho da fonte */
            border-radius: 10px;       /* Bordas arredondadas */
            margin-bottom: 20px;       /* Margem inferior */
            text-align: center;        /* Alinha o texto ao centro */
        }
        </style>

        <div class="banner">
        🐆 SISTEMA PARA MARCAÇÃO DE AGENDA ESTÚDIO GRUTA 🐆
        </div>
    """, unsafe_allow_html=True)

    
    limpar = st.empty()
    limpar.empty()
    st.cache_data.clear()
    st.cache_resource.clear()
    # if "pesquisou" not in st.session_state:       
    #     st.title("Menu Principal")    
    # st.title("Menu Principal")
    # st.write('Bem-vindo, '+st.session_state['username'].title()+'!') # Opcional: armazenar o nome de usuário
    pages = {
        'Geral':[
            st.Page('paginas/responsavelCadastrar.py', title='Cadastrar Responsável'),
             st.Page('paginas/clienteCadastrar.py', title='Cadastrar Cliente'),
             st.Page('paginas/trabalhoCadastrar.py', title='Cadastrar Trabalho'),
             st.Page('paginas/trabalhandoCadastrar.py', title='Agendar Trabalho')
        ],
        'Consulta':[
            st.Page('paginas/consultarAgenda.py', title='Consulta agenda')
        ]    
    }        
    pg = st.navigation(pages)
    pg.run()

    # if st.sidebar.button('rotulo_sair'):
    #     st.session_state['authenticated'] = False
    #     st.session_state['username'] = ''
    #     st.rerun()
    

# Lógica principal do aplicativo
# if st.session_state['authenticated']:

# st.set_page_config(layout="wide")
menu_page()