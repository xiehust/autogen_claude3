import streamlit as st
import autogen
import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from autogen import UserProxyAgent,AssistantAgent,GroupChatManager
import random 
import os
import shutil
from utils import print_messages,print_formatted_messages

st.set_page_config(page_title="autogen_claude3", page_icon="📈")




# SEED = random.randint(1,999)
SEED = 551
DOCKER_IMG ="my-python-app"
avatars = {
    'user1':'👩‍💻',
    'user2':'img/avataaars-user-2.svg',
    'assistant1':'img/avataaars-engineer.svg',
    'assistant2':'img/avataaars-engineer-2.svg',
    'assistant3':'img/avataaars-manager.svg',
    'assistant4':'img/avataaars-analysit.svg',
    'assistant5':'img/avataaars-engineer-3.svg',
    'assistant6':'img/avataaars-engineer-4.svg',
}

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

sys_template = """You will be acting as an IELTS examiner, use the  IELTS TASK 1 Writing band descriptors standards to rate the IELTS essay. 
    """
human_template = """
    here is the writing task and essay:
        <essay>
        {text}
        </essay>
        1. Please rate the IELTS essay in Task Achievement, Coherence and Cohesion, Lexical Resource, Grammatical Range and Accuracy seperately,
            please put the scores are enclosed in tag <scores></scores>, and explain the assessment.
           then cacluate the average score of those scores, and response in <average_score></average_score>.
        for example:
        <scores>
            <task_achievement>
                <score>6.5</score>
                <explain>xxxxxx</explain>
            </task_achievement>
            <coherence_cohesion>
                <score>6.5</score>
                <explain>xxxxxx</explain>
            </coherence_cohesion>
            <lexical_resource>
                <score>7.0</score>
                <explain>xxxxxx</explain>
            </lexical_resource>
            <grammatical_range_accuracy>
                <score>8.0</score>
                <explain>xxxxxx</explain>
            </grammatical_range_accuracy>
        </scores>
        <average_score>
         7.0
        </average_score>
    2.  Provide suggestions in xml tag <suggestions></suggestions>,please follow the instructions listed below:
        1) Provide improvement suggestions paragraph by paragraph, format it in the sub xml tag for example <paragraph_1>, <paragraph_2>,  <paragraph_3>
            please also provide an example of how to improve writing.
        2) Provide specific tips for improving scores, format it in the sub xml tag <tips>
        3) Vocabulary improvement: Find repetitive words in your essay and provide corresponding advanced vocabulary to make your writing more authentic and easily improve the score,
            format it in the sub xml tag <vocabulary_improvement>
        4) Provide improvement suggestions based on target score: Based on the essay provided by the student, give specific gaps to the target score and improvement suggestions,
        format it in the sub xml tag <target_score_suggestions>

"""
    
    # 3. Translate the scores and suggestions to Chinese, and response in a sub xml tag <translation>
    # 3. Reply "TERMINATE" in the end.
def setup_ielts_agents(st_session,llm_config):
    # create an AssistantAgent named "assistant"
    assistant = AssistantAgent(
        name="assistant",
        llm_config=llm_config,
         code_execution_config=False,
        system_message=sys_template,
    )
    assistant.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages, 
        config={"session_messages": st_session,"avatar":"🤖"},
    )
    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = UserProxyAgent(
        name="user_proxy",
        llm_config=llm_config,
         code_execution_config=False,
        human_input_mode="NEVER",
        system_message="""Please translate examiner's response to Chinese, 
        only translate the content in tags <paragraph_x>, <tips>, <target_score_suggestions> but don't translate the cited examples and titles""",
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    )
    user_proxy.register_reply(
        [autogen.Agent, None],
        reply_func=print_formatted_messages, 
        config={"session_messages": st_session,"avatar":"🧑‍💻"},
    )
    return user_proxy,assistant





models = {
    "claude-3-sonnet":"claude-3-sonnet",
    "gpt-3.5-turbo-16k-0613":"gpt-3.5-turbo-16k-0613",

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
    user_proxy,assistant = setup_ielts_agents(st.session_state.messages,llm_config)    

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
                    message=human_template.format(text = input_text['content']))


if __name__ == "__main__":
    asyncio.run(main())