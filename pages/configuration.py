import json

import streamlit as st
from streamlit import session_state as ss

from configs import get_config
from modules.nav import MenuButtons
from pages.account import get_roles
from utils import PASTA_ARQUIVOS, cria_chain_conversa

if 'authentication_status' not in ss:
    st.switch_page('pages/account.py')

MenuButtons(get_roles())
st.header('Configuration')


def config_page():
    st.header('Página de configuração', divider=True)

    model_name = st.text_input('Modifique o modelo', value=get_config('model_name'))
    retrieval_search_type = st.text_input('Modifique o tipo de retrieval', value=get_config('retrieval_search_type'))
    retrieval_kwargs = st.text_input('Modifique os parâmetros de retrieval', value=json.dumps(get_config('retrieval_kwargs')))
    prompt = st.text_area('Modifique o prompt padrão', height=350, value=get_config('prompt'))

    if st.button('Salvar parâmetros', use_container_width=True):
        retrieval_kwargs = json.loads(retrieval_kwargs.replace("'", '"'))
        st.session_state['model_name'] = model_name
        st.session_state['retrieval_search_type'] = retrieval_search_type
        st.session_state['retrieval_kwargs'] = retrieval_kwargs
        st.session_state['prompt'] = prompt
        st.rerun()
    
    if st.button('Atualizar ChatBot', use_container_width=True):
        if len(list(PASTA_ARQUIVOS.glob('*.pdf'))) == 0:
            st.error('Adicione arquivos .pdf para inicializar o chatbot')
        else:
            st.success('Inicializando o ChatBot...')
            cria_chain_conversa()
            st.rerun()


if ss.authentication_status:
    config_page()
else:
    st.write('Please log in on login page.')
