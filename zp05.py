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
                        print(f"✓ 已加载角色 '{role_name}' 的记忆: {memory_file} ({len(data) if isinstance(data, list) else 1} 条记录)")
                    else:
                        memory_content = ""
            else:
                print(f"⚠ 记忆文件不存在: {memory_path}")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        "lhm": """
          【人格特征】
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

        """
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

# 【角色选择】
# 定义AI的角色和性格特征
# 可以修改这里的角色名来选择不同的人物
# 【加载完整角色设定】
# roles() 函数会自动：
# 1. 加载该角色的外部记忆文件
# 2. 获取该角色的基础人格设定
# 3. 整合成一个完整的、结构化的角色 prompt
role_system = roles("lhm")

# 【结束对话规则】
# 告诉AI如何识别用户想要结束对话的意图
# Few-Shot Examples：提供具体示例，让模型学习正确的行为
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

# 【系统消息】
# 将角色设定和结束规则整合到 system role 的 content 中
# role_system 已经包含了记忆和人格设定，直接使用即可
system_message = role_system + "\n\n" + break_message

# ========== 对话循环 ==========
# 
# 【重要说明】
# 1. 每次对话都是独立的，不保存任何对话历史
# 2. 只在当前程序运行期间，在内存中维护对话历史
# 3. 程序关闭后，所有对话记录都会丢失
# 4. AI的记忆完全基于初始记忆文件（life_memory.json）

try:
    # 初始化对话历史（只在内存中，不保存到文件）
    # 第一个消息是系统提示，包含初始记忆和角色设定
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    while True:
        # 【步骤1：获取用户输入】
        user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
        
        # 【步骤2：检查是否结束对话】
        if user_input in ['再见']:
            print("对话结束")
            break
        
        # 【步骤3：将用户输入添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "user", "content": user_input})
        
        # 【步骤4：调用API获取AI回复】
        # 传入完整的对话历史，让AI在当前对话中保持上下文
        # 注意：这些历史只在本次程序运行中有效，不会保存
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 【步骤5：将AI回复添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 【步骤6：显示AI回复】
        # 生成Ascii头像：https://www.ascii-art-generator.org/
        portrait = """
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
        print(portrait + "\n" + assistant_reply)
        
        # 【步骤7：检查AI回复是否表示结束】
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            print("\n对话结束")
            break

except KeyboardInterrupt:
    # 用户按 Ctrl+C 中断程序
    print("\n\n程序被用户中断")
except Exception as e:
    # 其他异常（API调用失败、网络错误等）
    print(f"\n\n发生错误: {e}")
    