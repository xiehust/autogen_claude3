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


def setup_chatgroups(st_session,llm_config):
    user_proxy = UserProxyAgent(
        name="User",
        llm_config=llm_config,
        description="You will be acting as a human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
        code_execution_config=False,
        # code_execution_config={"last_n_messages": 3, "work_dir": ".coding", "use_docker": False,},
        human_input_mode="NEVER",
    )
    user_proxy.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🧒"},#https://emojicopy.com/
    )
    


    engineer = AssistantAgent(
        name="Engineer",
        llm_config=llm_config,
        code_execution_config=False,
        description='''You will be acting as an software Engineer. You follow an  plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
    Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    ''',
    )
    
    engineer.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🐵"},
    )
    
    
    scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=llm_config,
    description="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
    )

    scientist.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🐶"},#https://emojicopy.com/
    )
    
    planner = AssistantAgent(
        name="Planner",
        code_execution_config=False,
        # max_consecutive_auto_reply=1,
        description='''Planner. Suggest a plan. Revise the plan based on feedback from admin and Critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
    ''',
        llm_config=llm_config,
    )
    planner.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🐨"},
    )
    

    
    executor =AssistantAgent(
        name="Executor",
        llm_config=llm_config,
        description="You will be acting as an code Executor. Execute the code written by the engineer and report the result.",
        human_input_mode="NEVER",
        code_execution_config={"last_n_messages": 3, "work_dir": ".coding", "use_docker": False,},
    )
    
    executor.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":'🐰'},
    )
    
    critic = autogen.AssistantAgent(
    name="Critic",
    description="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
    llm_config=llm_config,
    )
    
    critic.register_reply(
         [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":'🐻'},
    )
    
    groupchat = GroupChat(agents=[user_proxy,   planner,engineer, scientist, executor,critic ], messages=[], max_round=50)
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config,)
    
    manager.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":'🦁'},
    )
    
    return user_proxy,manager





models = {
        "claude-3-haiku":"claude-3-haiku",
    "claude-3-sonnet":"claude-3-sonnet",
    "gpt-4-1106-preview":"gpt-4-1106-preview",
    "gpt-4-turbo-2024-04-09":"gpt-4-turbo-2024-04-09",
    "gpt-3.5-turbo-16k":"gpt-3.5-turbo-16k"
}
async def main():
    global SEED
    st.title("💬 Group Chat(Autogen)")
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
    user_proxy,assistant = setup_chatgroups(st.session_state.messages,llm_config)    

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