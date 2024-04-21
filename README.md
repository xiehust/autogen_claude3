# autogen_claude3
autogen running using claude3  

## Setup LiteLLM as Proxy for Bedrock Claude3

Install litellm oroxy  
```bash
pip install 'litellm[proxy]'
```

Setup env for aws bedrock  
```bash
export AWS_ACCESS_KEY_ID=
export AWS_REGION_NAME=
export AWS_SECRET_ACCESS_KEY=
```

Run LLM lite proxy  
```bash
litellm --config litellm/config.yaml 
```


如果使用group chat需要修改
https://github.com/BerriAI/litellm/blob/main/litellm/llms/prompt_templates/factory.py#L836
https://github.com/xiehust/litellm/blob/717abfef9874e3a91e1228aac5201e5af5a62b4e/litellm/llms/prompt_templates/factory.py#L733


```python
    if new_messages[-1]["role"] == "assistant":
        last_content = ''
        for content in new_messages[-1]["content"]:
            if isinstance(content, dict) and content["type"] == "text":
                last_content = content[
                    "text"
                ].rstrip()  # no trailing whitespace for final assistant message
        for content in new_messages[-2]["content"]:
            if isinstance(content, dict) and content["type"] == "text":
                content["text"] = content["text"] + "\n\n" + last_content
        new_messages = new_messages[:-1]
     return new_messages
```
修改之后执行
pip install -r litellm/requirement.txt
bash start.sh