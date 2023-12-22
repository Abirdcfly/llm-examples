import streamlit as st
import requests
import json
import pprint
import sseclient
import time

with st.sidebar:
    server_url = st.text_input("服务 graphql-server/go-server 请求地址, 默认为 https://portal.172.22.96.136.nip.io/kubeagi-apis/chat", key="url")
    conversion_id = st.text_input("如果想继续的话，可以输入上次的conversion_id，留空表示新对话", key="conversion_id")
    token = st.text_input("需要输入token", key="token")
    app_name = st.text_input("应用名称", key="app_name")
    app_namespace = st.text_input("应用namespace", key="app_namespace")

requests.urllib3.disable_warnings()
st.title("💬 简单对话界面")
st.caption("🚀 聊聊聊，聊出个未来！")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello, I am  🤖 From KubeAGI"}]

if "first_show" not in st.session_state:
    st.session_state["first_show"] = True

if not server_url:
    server_url = "https://portal.172.22.96.136.nip.io/kubeagi-apis/chat"

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

headers = {'Accept': 'text/event-stream', 'Authorization': 'Bearer ' + token}
if prompt := st.chat_input():
    response = requests.post(server_url, json={"query":prompt,"response_mode":"streaming","conversion_id":conversion_id,"app_name":app_name, "app_namespace":app_namespace}, stream=True, headers=headers, verify=False)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    client = sseclient.SSEClient(response)
    with st.chat_message("assistant"):
        msg_all = ""
        message_placeholder = st.empty()
        for event in client.events():
            data = json.loads(event.data)
            msg = data["message"]
            msg_all += msg
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(msg_all + " ▌")
            conversion_id = data["conversion_id"]
        message_placeholder.markdown(msg_all)
    st.session_state.messages.append({"role": "assistant", "content": msg_all})
        #st.chat_message("assistant").write(msg_all)

    if st.session_state["first_show"]:
        st.info('这次聊天的 conversion_id 是： '+conversion_id, icon="ℹ️")
        st.session_state["first_show"] = False

