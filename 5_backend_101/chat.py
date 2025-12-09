from api import call_zhipu_api
from roles import get_break_rules
from jsonbin import save_latest_reply

def chat_once(history, user_input, role_prompt, bin_id=None, access_key=None):
    history.append({"role": "user", "content": user_input})
    
    system_message = role_prompt + "\n\n" + get_break_rules()
    api_messages = [{"role": "system", "content": system_message}] + history[1:]
    
    result = call_zhipu_api(api_messages)
    reply = result['choices'][0]['message']['content']
    
    history.append({"role": "assistant", "content": reply})
    
    if bin_id and access_key:
        save_latest_reply(reply, bin_id, access_key)
    
    return reply
