import streamlit as st
import os
import subprocess
import psutil

# 设置配置文件路径
CONFIG_FILE = os.path.join('gpt_academic', 'config_private.py')
process = None
process_pid = None
update_process = None
update_process_pid = None

# 读取配置文件
def read_config():
    config = {}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
        exec(file.read(), config)
    config.pop('__builtins__', None)  # 移除 __builtins__ 键
    return config

# 保存配置文件
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
        for key, value in config.items():
            if key == '__builtins__':
                continue
            if key == 'API_URL_REDIRECT':
                file.write(f'{key} = {value}\n')
            elif key in ['AZURE_CFG_ARRAY'] and value == "{}":
                file.write(f'{key} = {value}\n')
            elif key == 'AUTHENTICATION':
                if not value or value == ['']:
                    file.write(f'{key} = []\n')
                else:
                    formatted_value = ', '.join([f'("{item.split(",")[0]}", "{item.split(",")[1]}")' for item in value])
                    file.write(f'{key} = [{formatted_value}]\n')
            elif isinstance(value, str):
                file.write(f'{key} = "{value}"\n')
            elif isinstance(value, list):
                file.write(f'{key} = {value}\n')
            elif isinstance(value, dict):
                file.write(f'{key} = {value}\n')
            else:
                file.write(f'{key} = {value}\n')

# 启动程序
def start_program():
    global process, process_pid
    if process is None:
        # 更改为你启动 Python 虚拟环境和主程序的路径
        venv_python = os.path.join('Python', 'App', 'Python', 'python.exe')
        main_script = os.path.join('gpt_academic', 'main.py')

        process = subprocess.Popen(
            ['cmd.exe', '/c', 'start', 'cmd.exe', '/k', venv_python, main_script],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        process_pid = process.pid

# 关闭程序
def stop_program():
    global process, process_pid
    if process is not None:
        try:
            parent = psutil.Process(process_pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
        except psutil.NoSuchProcess:
            pass
        process = None
        process_pid = None

# 启动更新程序
def start_update():
    global update_process, update_process_pid
    if update_process is None:
        venv2_python = os.path.join('Python', 'App', 'Python', 'python.exe')
        update_script = os.path.join('update.py')
        update_process = subprocess.Popen(
            ['cmd.exe', '/c', f'start cmd.exe /k {venv2_python} {update_script}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        update_process_pid = update_process.pid

# 主应用函数
def main():
    config = read_config()

    st.header("学术GPT配置文件编辑器", divider='rainbow')

    tabs = st.tabs(["快速配置", "模型配置", "高级设置"])

    with tabs[0]:
        st.header("快速配置")
        config['API_KEY'] = st.text_input("API密钥", config.get('API_KEY', ''))
        config['USE_PROXY'] = st.checkbox("使用代理", config.get('USE_PROXY', False))
        if config['USE_PROXY']:
            st.markdown(''':blue-background[[协议]://  [地址]  :[端口]]''')
            st.markdown(''':blue-background[例如：socks5h://localhost:11284或http://127.0.0.1:7890]''')
            proxies = config.get('proxies', {})
            if proxies is None:
                proxies = {}
            config['proxies'] = {
                "http": st.text_input("HTTP代理", proxies.get('http', '')),
                "https": st.text_input("HTTPS代理", proxies.get('https', ''))
            }
        else:
            config['proxies'] = None

        # 提取当前API_URL_REDIRECT中的reverse-proxy-url
        current_api_url_redirect = config.get('API_URL_REDIRECT', {})
        if current_api_url_redirect:
            current_reverse_proxy_url = list(current_api_url_redirect.values())[0].split('/v1/')[0]
        else:
            current_reverse_proxy_url = ""

        reverse_proxy_url = st.text_input("API重定向代理URL", current_reverse_proxy_url)
        st.markdown(''':blue-background[例如 https://api.openai.com]''')
        if reverse_proxy_url:
            api_url_redirect = {
                "https://api.openai.com/v1/chat/completions": reverse_proxy_url + "/v1/chat/completions"
            }
            config['API_URL_REDIRECT'] = api_url_redirect
            st.text(f'API_URL_REDIRECT: {api_url_redirect}')

        config['DEFAULT_WORKER_NUM'] = st.number_input("API请求频率（每分钟）", value=config.get('DEFAULT_WORKER_NUM', 3))

        available_themes = config.get('AVAIL_THEMES', [])
        default_theme = config.get('THEME', 'Default')
        if default_theme not in available_themes:
            available_themes.append(default_theme)

        config['THEME'] = st.selectbox("主题", available_themes, index=available_themes.index(default_theme))
        # Default available LLM models
        default_avail_llm_models = [
            "qianfan", "deepseekcoder", "spark", "sparkv2", "sparkv3", "sparkv3.5",
            "qwen-turbo", "qwen-plus", "qwen-max", "qwen-local",
            "moonshot-v1-128k", "moonshot-v1-32k", "moonshot-v1-8k",
            "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0125", "gpt-4o-2024-05-13",
            "claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-2.1", "claude-instant-1.2",
            "moss", "llama2", "chatglm_onnx", "internlm", "jittorllms_pangualpha", "jittorllms_llama",
            "yi-34b-chat-0205", "yi-34b-chat-200k"
        ]

        # Load existing or default models
        available_llm_models = config.get('AVAIL_LLM_MODELS', default_avail_llm_models)
        config['AVAIL_LLM_MODELS'] = available_llm_models
        
        # Display the multi-select for available LLM models
        st.multiselect("可用的LLM模型", available_llm_models, default=available_llm_models)
        
        # Allow user to add or remove models
        with st.expander("可用模型高级设置"):
            new_model = st.text_input("添加新的LLM模型")
            if st.button("添加模型"):
                if new_model and new_model not in available_llm_models:
                    available_llm_models.append(new_model)
            
            remove_model = st.selectbox("移除LLM模型", [""] + available_llm_models)
            if st.button("移除模型") and remove_model:
                available_llm_models.remove(remove_model)

        config['LLM_MODEL'] = st.selectbox("默认LLM模型设置", available_llm_models, index=available_llm_models.index(config.get('LLM_MODEL', 'gpt-3.5-turbo')))
        
        multi_query_llm_models = st.multiselect("多查询LLM模型", available_llm_models, default=config.get('MULTI_QUERY_LLM_MODELS', '').split('&'))
        config['MULTI_QUERY_LLM_MODELS'] = '&'.join(multi_query_llm_models)

        config['WEB_PORT'] = st.number_input("Web端口", value=config.get('WEB_PORT', -1))
        st.markdown(''':blue-background[网页的端口, -1代表随机端口]''')
        config['AUTO_OPEN_BROWSER'] = st.checkbox("自动打开浏览器", config.get('AUTO_OPEN_BROWSER', True))
        config['MAX_RETRY'] = st.number_input("最大重试次数", value=config.get('MAX_RETRY', 2))


    with tabs[1]:
        st.header("模型配置")
        with st.expander("本地模型相关设置"):
            config['QWEN_LOCAL_MODEL_SELECTION'] = st.text_input("QWEN本地模型选择", config.get('QWEN_LOCAL_MODEL_SELECTION', 'Qwen/Qwen-1_8B-Chat-Int8'))
            st.markdown(''':blue-background[选择本地模型变体（只有当AVAIL_LLM_MODELS包含了对应本地模型时，才会起作用）
如果你选择Qwen系列的模型，那么请在上面填写中指定具体的模型
也可以是具体的模型路径]''')
            config['CHATGLM_PTUNING_CHECKPOINT'] = st.text_input("ChatGLM PTuning 检查点", config.get('CHATGLM_PTUNING_CHECKPOINT', ''))
            st.markdown(''':blue-background[如果使用ChatGLM2微调模型，请把 LLM_MODEL="chatglmft"，并在此处指定模型路径]''')
            st.text(" 本地LLM模型如ChatGLM的执行方式 CPU/GPU")
            config['LOCAL_MODEL_DEVICE'] = st.selectbox("本地模型设备", ["cpu", "cuda"], index=["cpu", "cuda"].index(config.get('LOCAL_MODEL_DEVICE', 'cpu')))
            config['LOCAL_MODEL_QUANT'] = st.selectbox("本地模型量化", ["FP16", "INT4", "INT8"], index=["FP16", "INT4", "INT8"].index(config.get('LOCAL_MODEL_QUANT', 'FP16')))
        with st.expander("阿里云相关设置"):
            st.markdown(''':blue-background[接入通义千问在线大模型 https://dashscope.console.aliyun.com]''')
            config['DASHSCOPE_API_KEY'] = st.text_input("阿里灵积云API_KEY", config.get('DASHSCOPE_API_KEY', ''))
            st.markdown(''':blue-background[阿里云实时语音识别 配置难度较高参考 https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md]''')
            config['ENABLE_AUDIO'] = st.checkbox("启用音频", config.get('ENABLE_AUDIO', False))
            config['ALIYUN_TOKEN'] = st.text_input("阿里云Token", config.get('ALIYUN_TOKEN', ''))
            config['ALIYUN_APPKEY'] = st.text_input("阿里云AppKey", config.get('ALIYUN_APPKEY', ''))
            config['ALIYUN_ACCESSKEY'] = st.text_input("阿里云AccessKey", config.get('ALIYUN_ACCESSKEY', ''))
            config['ALIYUN_SECRET'] = st.text_input("阿里云Secret", config.get('ALIYUN_SECRET', ''))
        with st.expander("百度千帆（LLM_MODEL=qianfan)"):
            config['BAIDU_CLOUD_API_KEY'] = st.text_input("百度云API密钥", config.get('BAIDU_CLOUD_API_KEY', ''))
            config['BAIDU_CLOUD_SECRET_KEY'] = st.text_input("百度云密钥", config.get('BAIDU_CLOUD_SECRET_KEY', ''))
            config['BAIDU_CLOUD_QIANFAN_MODEL'] = st.text_input("百度云千帆模型", config.get('BAIDU_CLOUD_QIANFAN_MODEL', 'ERNIE-Bot'))
            st.markdown(''':blue-background[ 可选 "ERNIE-Bot-4"(文心大模型4.0), "ERNIE-Bot"(文心一言), "ERNIE-Bot-turbo", "BLOOMZ-7B", "Llama-2-70B-Chat", "Llama-2-13B-Chat", "Llama-2-7B-Chat"]''')
        with st.expander("Slack Claude"):
            st.markdown(''':blue-background[如果需要使用Slack Claude，使用教程详情见 request_llms/README.md如果需要使用Slack Claude，使用教程详情见 [request_llms/README.md](https://github.com/binary-husky/gpt_academic/tree/master/request_llms)]''')
            config['SLACK_CLAUDE_BOT_ID'] = st.text_input("Slack Claude Bot ID", config.get('SLACK_CLAUDE_BOT_ID', ''))
            config['SLACK_CLAUDE_USER_TOKEN'] = st.text_input("Slack Claude 用户令牌", config.get('SLACK_CLAUDE_USER_TOKEN', ''))
        with st.expander("Azure"):
            st.markdown(r''':blue-background[如果需要使用AZURE（方法一：单个azure模型部署）详情请见额外文档 [docs\use_azure.md](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_azure.md)]''')
            config['AZURE_ENDPOINT'] = st.text_input("Azure API 端点", config.get('AZURE_ENDPOINT', 'https://你亲手写的api名称.openai.azure.com/'))
            config['AZURE_API_KEY'] = st.text_input("Azure API密钥", config.get('AZURE_API_KEY', ''))
            config['AZURE_ENGINE'] = st.text_input("Azure 模型名", config.get('AZURE_ENGINE', ''))
            st.markdown(r''':blue-background[如果需要使用AZURE（方法二：多个azure模型部署）详情请见额外文档 [docs\use_azure.md](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_azure.md)''')
            config['AZURE_CFG_ARRAY'] = st.text_input("AZURE_CFG_ARRAY", config.get('AZURE_CFG_ARRAY', '{}'))
        with st.expander("GPT-SOVITS"):
            st.markdown(''':blue-background[GPT-SOVITS 文本转语音服务的运行地址（将语言模型的生成文本朗读出来）]''')
            config['TTS_TYPE'] = st.selectbox("TTS类型", ["DISABLE", "EDGE_TTS", "LOCAL_SOVITS_API"], index=["DISABLE", "EDGE_TTS", "LOCAL_SOVITS_API"].index(config.get('TTS_TYPE', 'DISABLE')))
            config['GPT_SOVITS_URL'] = st.text_input("GPT Sovits URL", config.get('GPT_SOVITS_URL', ''))
            config['EDGE_TTS_VOICE'] = st.text_input("Edge TTS 语音", config.get('EDGE_TTS_VOICE', 'zh-CN-XiaoxiaoNeural'))
        with st.expander("讯飞星火大模型"):
            st.markdown(''':blue-background[接入讯飞星火大模型 https://console.xfyun.cn/services/iat]''')
            config['XFYUN_APPID'] = st.text_input("讯飞AppID", config.get('XFYUN_APPID', '00000000'))
            config['XFYUN_API_SECRET'] = st.text_input("讯飞API密钥", config.get('XFYUN_API_SECRET', 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'))
            config['XFYUN_API_KEY'] = st.text_input("讯飞API密钥", config.get('XFYUN_API_KEY', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'))
        with st.expander("智谱大模型"):
            st.markdown(''':blue-background[接入智谱大模型 https://maas.aminer.cn/]''')
            config['ZHIPUAI_API_KEY'] = st.text_input("智谱AI API密钥", config.get('ZHIPUAI_API_KEY', ''))
           # config['ZHIPUAI_MODEL'] = st.text_input("智谱AI 模型", config.get('ZHIPUAI_MODEL', ''))
        with st.expander("Claude API"):
            st.markdown(''':blue-background[Claude API KEY]''')
            config['ANTHROPIC_API_KEY'] = st.text_input("Anthropic API密钥", config.get('ANTHROPIC_API_KEY', ''))
        with st.expander("月之暗面"):
            st.markdown(''':blue-background[月之暗面 API KEY]''')
            config['MOONSHOT_API_KEY'] = st.text_input("Moonshot API密钥", config.get('MOONSHOT_API_KEY', ''))
        with st.expander("零一万物(Yi Model)"):
            st.markdown(''':blue-background[零一万物(Yi Model) API KEY]''')
            config['YIMODEL_API_KEY'] = st.text_input("Yimodel API密钥", config.get('YIMODEL_API_KEY', ''))
        with st.expander("Mathpix"):
            st.markdown(''':blue-background[Mathpix 拥有执行PDF的OCR功能，但是需要注册账号 https://accounts.mathpix.com]''')
            config['MATHPIX_APPID'] = st.text_input("Mathpix AppID", config.get('MATHPIX_APPID', ''))
            config['MATHPIX_APPKEY'] = st.text_input("Mathpix AppKey", config.get('MATHPIX_APPKEY', ''))
        with st.expander("DOC2X的PDF解析服务"):
            st.markdown(''':blue-background[DOC2X的PDF解析服务，注册账号并获取API KEY: https://doc2x.noedgeai.com/login]''')
            config['DOC2X_API_KEY'] = st.text_input("Doc2x API密钥", config.get('DOC2X_API_KEY', ''))
        with st.expander("Google Gemini"):
            st.markdown(''':blue-background[Google Gemini API-Key https://ai.google.dev/]''')
            config['GEMINI_API_KEY'] = st.text_input("Gemini API密钥", config.get('GEMINI_API_KEY', ''))
        with st.expander("自定义API密钥模式"):
            config['CUSTOM_API_KEY_PATTERN'] = st.text_input("自定义API密钥模式", config.get('CUSTOM_API_KEY_PATTERN', ''))


    with tabs[2]:
        st.header("高级设置")
        config['DEFAULT_FN_GROUPS'] = st.text_input("默认功能组", ','.join(config.get('DEFAULT_FN_GROUPS', []))).split(',')
        config['CHATBOT_HEIGHT'] = st.number_input("聊天机器人高度", value=config.get('CHATBOT_HEIGHT', 1115))
        config['CODE_HIGHLIGHT'] = st.checkbox("代码高亮", config.get('CODE_HIGHLIGHT', True))
        config['LAYOUT'] = st.selectbox("布局", ["LEFT-RIGHT", "TOP-DOWN"], index=["LEFT-RIGHT", "TOP-DOWN"].index(config.get('LAYOUT', 'LEFT-RIGHT')))
        config['DARK_MODE'] = st.checkbox("暗模式", config.get('DARK_MODE', True))
        config['TIMEOUT_SECONDS'] = st.number_input("超时秒数", value=config.get('TIMEOUT_SECONDS', 30))
        config['CONCURRENT_COUNT'] = st.number_input("设置gradio的并行线程数（不需要修改）", value=config.get('CONCURRENT_COUNT', 100))
        config['AUTO_CLEAR_TXT'] = st.checkbox("自动清除文本", config.get('AUTO_CLEAR_TXT', False))
        config['INIT_SYS_PROMPT'] = st.text_area("系统提示词", config.get('INIT_SYS_PROMPT', ''))
        config['ADD_WAIFU'] = st.checkbox("加一个live2d装饰", config.get('ADD_WAIFU', False))
        config['AUTHENTICATION'] = st.text_input("身份验证", ','.join(config.get('AUTHENTICATION', []))).split(',')
        config['CUSTOM_PATH'] = st.text_input("自定义路径", config.get('CUSTOM_PATH', '/'))
        config['SSL_KEYFILE'] = st.text_input("SSL密钥文件", config.get('SSL_KEYFILE', ''))
        config['SSL_CERTFILE'] = st.text_input("SSL证书文件", config.get('SSL_CERTFILE', ''))
        config['API_ORG'] = st.text_input("API组织", config.get('API_ORG', ''))
        config['HUGGINGFACE_ACCESS_TOKEN'] = st.text_input("Huggingface 访问令牌", config.get('HUGGINGFACE_ACCESS_TOKEN', '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'))
        config['GROBID_URLS'] = st.text_area("Grobid URLs", '\n'.join(config.get('GROBID_URLS', []))).split('\n')
        config['ALLOW_RESET_CONFIG'] = st.checkbox("允许重置配置", config.get('ALLOW_RESET_CONFIG', False))
        config['AUTOGEN_USE_DOCKER'] = st.checkbox("自动生成使用Docker", config.get('AUTOGEN_USE_DOCKER', False))
        config['PATH_PRIVATE_UPLOAD'] = st.text_input("私有上传路径", config.get('PATH_PRIVATE_UPLOAD', 'private_upload'))
        config['PATH_LOGGING'] = st.text_input("日志路径", config.get('PATH_LOGGING', 'gpt_log'))
        config['WHEN_TO_USE_PROXY'] = st.text_input("使用代理的场景", ','.join(config.get('WHEN_TO_USE_PROXY', []))).split(',')
        config['BLOCK_INVALID_APIKEY'] = st.checkbox("阻止无效的API密钥", config.get('BLOCK_INVALID_APIKEY', False))
        config['PLUGIN_HOT_RELOAD'] = st.checkbox("插件热重载", config.get('PLUGIN_HOT_RELOAD', False))
        config['NUM_CUSTOM_BASIC_BTN'] = st.number_input("自定义基础按钮数量", value=config.get('NUM_CUSTOM_BASIC_BTN', 4))

    with st.sidebar:
       # 目标 URL
        target_url = "https://space.bilibili.com/23751775"
        description = "作者: [小明同学要加油](https://space.bilibili.com/23751775)"

        # 使用 st.markdown 显示文本和超链接
        st.markdown(description, unsafe_allow_html=True)

        if st.button("保存配置"):
            if reverse_proxy_url:
                config['API_URL_REDIRECT'] = {
                    "https://api.openai.com/v1/chat/completions": reverse_proxy_url + "/v1/chat/completions"
                }
            save_config(config)
            st.success("配置已保存！")

        if st.button("启动程序"):
            start_program()
            st.success("程序已启动,请注意弹窗命令行窗口。如需停止请关闭弹出窗口。")
        with st.expander("其他功能"):
            if st.button("升级功能（非必要请勿点使用）"):
                start_update()
                st.success("升级程序已启动,请注意弹窗命令行窗口。")

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        st.error(f"配置文件{CONFIG_FILE}不存在，请确保文件路径正确。")
    else:
        main()
