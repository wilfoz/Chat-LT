import streamlit as st
from langchain.prompts import PromptTemplate
from streamlit import session_state as ss

from configs import get_config
from modules.nav import MenuButtons
from pages.account import get_roles

if 'authentication_status' not in ss:
    st.switch_page('pages/account.py')

MenuButtons(get_roles())
st.header('Debug')


def debug_page():
    st.header('Página de debug', divider=True)
    prompt_template = get_config('prompt')
    prompt_template = PromptTemplate.from_template(prompt_template)

    if not 'ultima_resposta' in st.session_state:
        st.error('Realize uma pergunta para o modelo para visualizar o debug')
        st.stop()
    
    ultima_resposta = st.session_state['ultima_resposta']

    contexto_docs = ultima_resposta['source_documents']
    contexto_list = [doc.page_content for doc in contexto_docs]
    contexto_str = '\n\n'.join(contexto_list)

    chain = st.session_state['chain']
    memory = chain.memory
    chat_history = memory.buffer_as_str

    with st.container(border=True):
        prompt = prompt_template.format(
            chat_history=chat_history,
            context=contexto_str,
            question=''
        )
        st.code(prompt)

if ss.authentication_status:
    debug_page()
else:
    st.write('Please log in on login page.')