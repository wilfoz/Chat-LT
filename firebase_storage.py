import streamlit as st
from firebase_admin import storage


class FirebaseStorage:
    
    def __init__(self):
        self.bucket = storage.bucket()

    def save_pdf(self, file, file_name):
        try:
            file.seek(0)
            blob = self.bucket.blob(f"arquivos/{file_name}")
            blob.upload_from_file(file)
            st.success(f"Arquivo {file_name} salvo com sucesso no Firebase Storage.")
        except Exception as e:
            st.error(f"Erro ao salvar arquivo: {str(e)}")

    def get_all_pdfs(self):
        try:
            blobs = self.bucket.list_blobs(prefix="arquivos/")
            pdf_files = []

            for blob in blobs:
                if blob.name.endswith(".pdf"):
                    pdf_files.append(blob.name)
                    
            return pdf_files
        except Exception as e:
            st.error(f"Erro ao listar arquivos PDF: {str(e)}")
            return []

    def delete_pdf(self, file_name):
        try:
            blob = self.bucket.blob(f"arquivos/{file_name}")
            blob.delete()
            st.success(f"Arquivo {file_name} excluído com sucesso do Firebase Storage.")
        except Exception as e:
            st.error(f"Erro ao excluir o arquivo PDF: {str(e)}")