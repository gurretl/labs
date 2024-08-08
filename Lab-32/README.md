# About
Date : 08th August 2024  
Author: Lionel Gurret  
Description : My First App using OpenAI

# How to run the script

- Create an Azure OpenAI resource in your subscription

```
az cognitiveservices account create \
-n MyOpenAIResource \
-g OAIResourceGroup \
-l eastus \
--kind OpenAI \
--sku s0 \
--subscription XXXXXXXXXXXXX

az cognitiveservices account deployment create \
-g OAIResourceGroup \
-n MyOpenAIResource \
--deployment-name MyModel \
--model-name gpt-35-turbo \
--model-version "0301"  \
--model-format OpenAI \
--sku-name "Standard" \
--sku-capacity 1
```

- Configure the .env file
- Run the script with Python

# YouTube Video
[https://youtu.be/TO_COMPLETE](Link)
