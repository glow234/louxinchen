def should_exit_by_user(user_input):
    exit_words = ['再见', '退出', '结束', 'bye', 'exit']
    return user_input.strip() in exit_words

def should_exit_by_ai(ai_reply):
    reply_cleaned = ai_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
    if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
        return True
    return False
