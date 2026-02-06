import streamlit as st;
import Controllers.UsuarController as usu;
import Models.usuar as usuar;
import Services.geral as ger;

st.title('Acesso Vendere')
with st.form(key="acesso_vendere"):    
    input_user = st.text_input(label='Insira seu login:')
    input_password = st.text_input(label='Insira sua senha',type='password')
    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        input_button_submnit = st.form_submit_button(' Enviar ')

if input_button_submnit:
    usuario = usu.consultarUsuario(input_user)

    if usuario == None:   
        st.success('Usuário ou senha inválidos!', icon="❌")
    else:    
        usuar = usuario
        ger.userLoged = usuar
        senha = usu.de_cod_usu(int(usuar.cd_usuar), usuar.nm_usuar_senha)
        if senha == input_password:
            st.success('Usuário encontrado!', icon="✅")            
        else:
            st.success('Usuário ou senha inválidos!', icon="❌")