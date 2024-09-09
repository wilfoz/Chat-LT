import streamlit as st
from streamlit import session_state as ss

from Chat import FILE_FOLDER, Chat
from firebase_services import get_conversation_history, save_conversation
from modules.nav import MenuButtons
from pages.account import get_id, get_roles

if 'authentication_status' not in ss:
    st.switch_page('pages/account.py')
    
MenuButtons(get_roles())
ss['authenticated_user'] = get_id(ss['username'])


class HomePage:
    def __init__(self):
        user = ss['authenticated_user']
        self.user_id = [*user.values()][0]
        self.agent = Chat(self.user_id)

    def display_sidebar(self):
        uploaded_pdfs = st.file_uploader(
            'Adicione seus arquivos PDF', 
            type=['pdf'], 
            accept_multiple_files=True
        )
        if uploaded_pdfs:
            self._clear_old_files()
            self._save_uploaded_pdfs(uploaded_pdfs)
        
        label_botao = 'Inicializar ChatBot' if 'chain' not in st.session_state else 'Atualizar ChatBot'
        if st.button(label_botao, use_container_width=True):
            if not list(FILE_FOLDER.glob('*.pdf')):
                st.error('Adicione arquivos PDF para inicializar o chatbot.')
            else:
                self.agent.initialize_chain()
                st.session_state['agent'] = self.agent
                st.success('ChatBot inicializado!')

    def _clear_old_files(self):
        for arquivo in FILE_FOLDER.glob('*.pdf'):
            arquivo.unlink()

    def _save_uploaded_pdfs(self, uploaded_pdfs):
        for pdf in uploaded_pdfs:
            with open(FILE_FOLDER / pdf.name, 'wb') as f:
                f.write(pdf.read())

    def display_chat_window(self):
        st.header(f'🤖 Bem-vindo ao Chat LT', divider=True)

        if 'agent' not in st.session_state:
            st.error('Faça o upload de PDFs para começar!')
            st.stop()

        agent = st.session_state['agent']

        container = st.container()
        agent.add_to_memory(self.user_id)
        for chat in agent.memory.chat_memory.messages:
            if chat.type == 'human':
                container.chat_message('human').markdown(f"Você: {chat.content}")
            else:
                container.chat_message('ai').markdown(f"Bot: {chat.content}")
        
        # Input de nova mensagem
        nova_mensagem = st.chat_input('Converse com seus documentos...')
        if nova_mensagem:
            container.chat_message('human').markdown(nova_mensagem)
            resposta = agent.chat_chain.invoke({'question': nova_mensagem})
            st.session_state['ultima_resposta'] = resposta
            container.chat_message('ai').markdown(resposta['answer'])

            # Salva a conversa no Firebase
            save_conversation(self.user_id, nova_mensagem, resposta['answer'])

        # Botão para limpar o histórico
        if st.button('Limpar Histórico'):
            agent.clear_history()
            st.success('Histórico limpo!')
            st.rerun()

    def run(self) -> None:
        with st.sidebar:
            self.display_sidebar()
        self.display_chat_window()


if __name__ == '__main__':
    if ss.authentication_status:
        page = HomePage()
        page.run()
    else:
        st.write('Por favor, faça login na página de login.')
