import xml.etree.ElementTree as ET
import re
import streamlit as st


def extract_xml_tags(content: str,tag_name:str) ->str:
    def extract_content_from_xml(xml_string, tag_name=None):
        root = ET.fromstring(xml_string)
        content_list = []
        for element in root.iter(tag_name):
            content_list.append( f'**{element.tag}:** \n{element.text}\n')
        return '\n'.join(content_list)

    pattern = rf"<{tag_name}>(.*?)</{tag_name}>"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        match_content = match.group(0)
        return extract_content_from_xml(match_content)
    else:
        return None




def _write_to_st(session_messages,role,text,avatar=None):
    with st.chat_message(name=role,avatar=avatar):
        st.write(text)
        session_messages.append(
                    {
                        "role": role,
                        "content":  text
                    }
                )

def print_messages(recipient, messages, sender, config):
    session_messages = config['session_messages']
    avatar = config['avatar']
    log = f"{sender.name} ==> {recipient.name}"
    print(log)
    _write_to_st(session_messages,sender.name,log+"\n\n"+messages[-1]['content'],avatar)
    return False, None 

def print_formatted_messages(recipient, messages, sender, config):
    session_messages = config['session_messages']
    avatar = config['avatar']
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]['content']}")
    flow = f"Messages from: {sender.name} sent to: {recipient.name}"
    scores = extract_xml_tags(messages[-1]['content'],tag_name='scores')
    average_scores = extract_xml_tags(messages[-1]['content'],tag_name='average_score')
    suggestions = extract_xml_tags(messages[-1]['content'],tag_name='suggestions')
    formated_msg = f"*flow* {flow} \n\n### 得分\n{scores} ### 平均分\n{average_scores} ### 建议\n{suggestions}\n"
    if suggestions: 
        _write_to_st(session_messages,sender.name,formated_msg,avatar)
    else:
        _write_to_st(session_messages,sender.name,messages[-1]['content'],avatar)
    return False, None 
