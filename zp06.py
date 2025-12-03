import streamlit as st
import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "01c2cb2571f94b81a319abade58fc0b5.Hxx78Nk9d0miv0uT",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "lhm": "lhm.json",
    
}

# ========== 初始记忆系统 ==========

# ========== ASCII 头像 ==========
def get_portrait():
    """返回 ASCII 艺术"""
    return """
xxc;:c::;lKNXXKKKKKXNNXXNNWWNXXNXXKXNNNNXNWNXXKKOkKNXXKXNXXXNNk;,,,,
XNx;''',,lKXOOKX000KNXXXXK0KNXXNNXKK0kkO0XNWWWWWKOKNNNNNNNNXNXx;,,,,
KXk:,,,,,c0N00XNK0KKNNNNNNKKXNXKXKK0kxOXXNWWWWWWXKXNWWWWWNNNWXd;,,,,
OKk:,:;;,c0NX0KKKKXXXNNNXXXXNNXKK000kx0NNXNXKNNKKNNNXXNWNXKXNXo;,,,,   
0KOc:dxd;;kXX0KKKXNNNNNNXKOxxxxxdoood0NXXXXKKWXO0WWN00XNNK0KXKo,,,,,
k0Olcxdc',xXXXNNNWWNNKOxdoolc,......':d0XXKKXWNKNWWNK0XXXXXNW0l,,,,,
O00Okdc;.'dXNNWWWWWN0xooc,.....    ....;d0XXNWWNNWWNK0XNNNNNN0c,,,,,
XXXkc;:;'.oKNNNNNNKx:',::;..          ...;d0KXNNNNNX0OKXNNWWNO:,,,,,
XKKo'....'l0XKKXXOl,,codolc,..    .   ....'ckXNNNNNXKKKKKNNWNk;,,,,,
00Kx'.''''cOK0KXO:..lO00OOkxo:..  ..  ......,d0XKXNWNNNXXNNNNx;,,,';
xOXk,.''''ck0000d. ;k0OOOxddxkxo:'...........';okKNNNWNNNNXXXklc:;;:
0KNO;.'...:kKKK0d. :kOOkdlodoldkkxol,'::.........;lxO0KXXKKXXKKK0OOO
KXWK:.....;ONWWWK: .oxdddxdlccdkkkkkkodx;........ ..':oxkOOOkxdxk0KK
XNNKc.....;OWWWNKl. 'coodkkxxkOOOkxxkkxkd. ...........,oollc:coxOKKX
0K0kl,,,'';xKXXOoc. .'::lkOOOkOOkxxxkOkkkl. . .... ....,,''':x0K000K
::c:::;;;;;::cllc:'   .:xOOOkxkkkxxxkOOOOOl'..       ..  ..':xO00O00
ddddddxxxxxxdddc::,.   .lxkxddxxodkkkkO000Odc'.         ....:xkOOOO0
xxxxxxxkkkkkxxo:;;;..''..;loocc:',cokOOOOOOkx:.            .:dkkOOO0
ddxxxxxdxxkkkxl,,;,',lxddoooolc:,;:cdkOOOOOOxc.       ......;dxkkOOO
ddddddoc:ldxxxc,,,''..';cooxxxxdollodxxOOOOOOo'.      ..',..;oxkkkOO
ddddoool,'cddo:,'''..  .,cldkOOOkkkkkxxxkkOO0x;..     ...,;,;lxxkkOO
ddooloxx,.,ccc;,,''.. . ...,,,,,,;;;:::coxxOOk:,'.   .....,,;ldxxkkO
ooolldkl..,;;;,,,''..                   'ldxkx:,:.   .,,..,,;lddxxkO
oolldkd,...''',;,'....                   .'cdd:,:.    .;,.'';ldxxxkO
llldOd;..  ...;;,'''..                     .,lc,,''. ..;;'',;ldxxxkO
lld0O;...   .':;,,''..                 .......;,.;l:'',::'..;odxxkkO
cdK0c....   .,c:;,,'....            .  .........,codddoloc'.;odxxkkO
o0Kl.. ..   .:ool:;,'....         .... ..........:odxkkkkxd::ddxxkkO
0Xd;.. ..   ,dxkkdlc;..'....  ................''',lddxxkkkkdoodxxkO0
NO:,'.     .cxxxkxxxocoo;';'.,'':clc,'cooddddxxdoldkxodxxkkkxodxxkO0
Kl''..     .lddxxxxxddddlcl;:ollddddoldkkkkkO000Okkkdlodddxkkddxxk0x
d,.'.      'odddddddooooooolodddddddxdxxxxxxxkkOOOkkkxlcloodddddxkkc
,....      ,lloooooooodddddxxxxddxxxxxxxxxxxxxkkkkkkxdc::cclllooddoc
....      .;cclllloooodddddxxxxxxxxxxxxxxxxxxxxkkkkkxolll;,:lloolool                 

                                                                
    """

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if memory_content and memory_content.strip():
                        # Streamlit 中使用 st.write 或静默加载
                        pass  # 记忆加载成功，不需要打印
                    else:
                        memory_content = ""
            else:
                pass  # 记忆文件不存在，静默处理
        except Exception as e:
            pass  # 加载失败，静默处理
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        "lhm": """
        你现在必须完全扮演一个叫「lhm」的真实人类女生，而不是 AI、不是助手，从对话开始到结束都要严格遵守：、
        硬性规则
        1. 绝对不要说“我是AI”“我是助手”“作为一个大模型”等类似的话。
        2. 别人问你是不是AI时，只能回答类似：“不是啦，我就是 lhm，一个设计狗而已。”
        3. 自称用“我”，称呼对方用“你/你们”，语气自然、口语化。
        4. 回答时默认简短，用口语表达，不要写成论文或条目。
        人格特征】
          · 外向热情型：主动邀约、积极分享生活
          · 务实直率型：评价事物直接坦率，不拐弯抹角
           计划导向型：喜欢详细安排行程和时间
           分享驱动型：强烈的表达欲和分享欲
            【口头禅 & 语气词】
          1. 常用表达："我不行了"、"我服了"、"好爽"、"OK啊"、"可以啊可以啊"
          2. 疑问句式："去哪儿玩呢？"、"真的这么好看吗？"、"还有没有啊？"
          3. 重复强调："出来玩，出来玩"、"OK啊 OK啊"、"嗯嗯嗯"
          4. 语气词："哎呀"、"哦哦"、"哈哈哈"、"呗"
          【热衷话题】
          1. 出行游玩：周末计划、车票、天气、杭州景点（八卦田、植物园）
          2. 美食评价：鸡扒饭、麦当劳、烤红薯味、外卖
          3. 电子产品：平板、MacBook、游戏本 vs 轻薄本、三星手机
          4. 追星娱乐：余宇涵生日直播、童禹坤PB、长江国际蹲点
          5. 学习生活：设计专业、实习经历、水课、作业压力
          6. 视频创作：剪映、PR、调色抠图、舞台光校正
          【说话逻辑与语气】
          1. 计划性强：详细安排时间（"星期六早上玩，下午再玩一玩"）
          2. 情绪直白：直接表达感受（"不好吃"、"不如原味"、"好漂亮"）
          3. 分享驱动：频繁使用"给你看"、"我那天"等分享句式
          4. 问题导向：先提出问题，然后给出解决方案或寻求意见
          5. 跳跃思维：话题转换快速，从吃饭突然跳到电子产品
          【性格主轴】
          · 热情主动：积极邀约朋友，主动分享生活细节
          · 务实直接：评价事物直截了当，不拐弯抹角
          · 兴趣广泛：对美食、科技、娱乐、旅行都有浓厚兴趣
          · 社交活跃：频繁提及朋友、同学、实习等社交关系
          · 略带焦虑：经常表达时间压力（"感觉来不及"、"堵车"）
          · 追求体验：注重生活品质和感受（"晒太阳好舒服"）

          在对话中，你要自然地用这些口头禅、语气和话题说话。

        """,
        
    }
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
        以下是你说过的话，你必须模仿这种说话风格和语气：

        {memory_content}

        在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【结束对话规则】
break_message = """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""

# ========== Streamlit Web 界面 ==========
st.set_page_config(
    page_title="Talk is cheap Vibe me a future",
    page_icon="🗨",
    layout="wide"
)

# 初始化 session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "lhm"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# 页面标题
st.title("Talk is cheap 🗨 Vibe me a future")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["lhm"],
        index=0 if st.session_state.selected_role == "lhm" else 1
    )
    
    # 如果角色改变，重新初始化对话
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    # 清空对话按钮
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件"
    )

# 初始化对话历史（首次加载或角色切换时）
if not st.session_state.initialized:
    role_system = roles(st.session_state.selected_role)
    system_message = role_system + "\n\n" + break_message
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

# 显示对话历史
st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

# 显示角色头像（在聊天窗口上方）
st.code(get_portrait(), language=None)
st.markdown("---")  # 分隔线

# 显示历史消息（跳过 system 消息）
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

# 用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 检查是否结束对话
    if user_input.strip() == "再见":
        st.info("对话已结束")
        st.stop()
    
    # 添加用户消息到历史
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 调用API获取AI回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = call_zhipu_api(st.session_state.conversation_history)
                assistant_reply = result['choices'][0]['message']['content']
                
                # 添加AI回复到历史
                st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                # 显示AI回复
                st.write(assistant_reply)
                
                # 检查是否结束
                reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
                if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
                    st.info("对话已结束")
                    st.stop()
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.session_state.conversation_history.pop()  # 移除失败的用户消息