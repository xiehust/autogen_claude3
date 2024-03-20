import streamlit as st
import autogen
import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from autogen import UserProxyAgent,AssistantAgent,GroupChatManager,GroupChat
import random 
import os
import shutil
from utils import print_messages,print_formatted_messages

st.set_page_config(page_title="autogen_claude3", page_icon="📈")




# SEED = random.randint(1,999)
SEED = 551
# DOCKER_IMG ="my-python-app"



def setup_llm_config(model_name):
    global SEED
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        filter_dict={
            "model": [model_name],
        },
    )
    llm_config={
            # "seed": SEED,  # seed for caching and reproducibility
                "config_list": config_list,  # a list of OpenAI API configurations
                # "temperature": 0.5,  # temperature for sampling
                # "timeout": 120,
            }
    return llm_config

def setup_assistant_agents(st_session,llm_config):
    # create an AssistantAgent named "assistant"
    assistant = AssistantAgent(
        name="assistant",
        llm_config=llm_config,
        
    )
    
    assistant.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🧑‍🎓"},#https://emojicopy.com/
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = UserProxyAgent(
        name="user_proxy",
        llm_config=llm_config,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            "last_n_messages": 1, 
            "work_dir": ".coding",
            "use_docker": True,  # set to True or image name like "python:3" to use docker
        },
    )
    
    user_proxy.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🧒"},#https://emojicopy.com/
    )
        
    return user_proxy,assistant


models = {
    "claude-3-sonnet":"claude-3-sonnet",
}

async def main():
    global SEED
    st.title("💬 Exam Score(Autogen)")
    user_proxy = None
    assistant = None
    with st.sidebar:
        # chat_mode = st.selectbox("Choose a chat mode", agent_setup_funcs.keys())
        model_name = st.selectbox("Choose a model", models.keys())
        st.success(f"Using seed number:{SEED}")
        if st.button('clear history cache'):
            st.session_state.messages = []
            if user_proxy:
                user_proxy.reset()
            if assistant:
                assistant.reset()
            try:
                shutil.rmtree('./.cache')
            except:
                pass

    ##initilize llm config
    llm_config = setup_llm_config(model_name=model_name)
    
    ##initilize st session messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    ##initilize agents
    user_proxy,assistant = setup_assistant_agents(st.session_state.messages,llm_config)    

    chat_placeholder = st.empty()
    with chat_placeholder.container(): 
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What date is today?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            input_text = st.session_state.messages[-1]
            user_proxy.initiate_chat(
                    assistant,
                    message=input_text['content'])


if __name__ == "__main__":
    asyncio.run(main())