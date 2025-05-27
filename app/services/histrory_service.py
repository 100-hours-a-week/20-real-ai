from app.core.chat_history import get_session_history

async def save_chat_history(user_id: str, question: str, answer: str):
    history = get_session_history(user_id)
    history.add_user_message(question)
    history.add_ai_message(answer)