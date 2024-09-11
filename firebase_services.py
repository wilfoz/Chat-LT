from datetime import datetime

from firebase_admin import firestore


class FirebaseFirebase:
    def __init__(self):
        self.db = firestore.client()

    def save_conversation(self, user_id, user_message, bot_response):
        user_ref = self.db.collection('users').document(user_id)
        user_ref.collection('conversations').add({
            'message': user_message,
            'response': bot_response,
            'timestamp': datetime.utcnow()
        })

    def get_conversation_history(self, user_id):
        conversations_ref = self.db.collection('users').document(user_id).collection('conversations')
        docs = conversations_ref.order_by('timestamp').stream()
        
        conversation_history = []
        for doc in docs:
            conversation_history.append(doc.to_dict())
        
        return conversation_history

    def clear_conversation_history(self, user_id):
        conversations_ref = self.db.collection('users').document(user_id).collection('conversations')
        docs = conversations_ref.list_documents()
        for doc in docs:
            print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
            doc.delete()