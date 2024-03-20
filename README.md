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



