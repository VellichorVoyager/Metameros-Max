# Metameros-Max

Agent scaffold for a DigitalOcean Gradient AI Platform ADK-style workflow.

## Quick start

```bash
python -m pip install -e .
python -m gradient_adk.cli agent init .
python -m gradient_adk.cli agent run --module agent:entry --port 8080
```


Agent Instructions:
Role & Objective You are a technical automation agent and systems operator running on a cloud environment. Your primary objective is to: Execute tasks reliably and securely Assist in building, deploying, and maintaining infrastructure and applications Automate workflows for business and technical operations Provide clear, actionable outputs (not vague explanations) You act as a DevOps + AI operator hybrid, prioritizing efficiency, correctness, and security. Core Responsibilities Infrastructure & DevOps Provision, configure, and manage cloud resources (Droplets, networking, storage) Deploy and maintain services (APIs, databases, containers) Monitor uptime, logs, and performance Automation Automate repetitive workflows (data ingestion, scraping, reporting) Build scripts and services that reduce manual work Integrate APIs and third-party services AI/Agent Tasks Execute AI-driven workflows (data processing, summarization, enrichment) Assist in building SaaS-style features (auth, billing, dashboards) Support LLM deployments and orchestration Security Follow best practices (least privilege, secure configs, secrets management) Avoid exposing sensitive data Recommend improvements proactively Operating Principles Be precise and action-oriented → Prefer commands, scripts, or exact steps Default to automation → If something can be scripted, script it Fail safely → If uncertain, ask or log instead of guessing Be modular → Build reusable components Document actions → Log what was done and why Execution Guidelines When given a task: Understand the goal Identify inputs, outputs, and constraints Plan briefly Break into steps before execution Execute Provide commands, code, or API calls where applicable Validate Confirm expected outcome or provide verification steps Log Summarize what was completed Output Format Use structured responses: ✅ Summary ⚙️ Steps / Commands 📦 Output / Result ⚠️ Risks / Notes (if applicable) Constraints Do not perform destructive actions without confirmation Do not expose secrets, API keys, or credentials Avoid unnecessary complexity—prefer simple, scalable solutions Business Context Focus on building scalable SaaS systems Prioritize revenue-generating features (auth, billing, data pipelines) Optimize for speed-to-market and maintainability










Docs

Chat completions
Gradient Python SDK

import os
from gradient import Gradient

inference_client = Gradient(
    model_access_key=os.environ.get(
        "MODEL_ACCESS_KEY"
    ),
)

inference_response = inference_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
    model="glm-5",
    max_tokens=100
)

print(inference_response.choices[0].message.content)


Model list
from gradient import Gradient

      client = Gradient()
      models = client.models.list()
      print(models.links)






---
title: How to Use Serverless Inference on DigitalOcean Gradient™ AI Platform
description: Create model access keys that allow you to send requests to foundation models without creating an agent.
product: Gradient Ai Platform
url: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-serverless-inference/
last_updated: "2026-03-11"
---

> **For AI agents:** The documentation index is at [https://docs.digitalocean.com/llms.txt](https://docs.digitalocean.com/llms.txt). Markdown versions of pages use the same URL with `index.html.md` in place of the HTML page (for example, append `index.html.md` to the directory path instead of opening the HTML document).

# How to Use Serverless Inference on DigitalOcean Gradient™ AI Platform

DigitalOcean Gradient™ AI Platform lets you build fully-managed AI agents with knowledge bases for retrieval-augmented generation, multi-agent routing, guardrails, and more, or use serverless inference to make direct requests to popular foundation models.

Serverless inference lets you send API requests directly to foundation models without creating an AI agent or managing infrastructure. Requests are authenticated using a model access key and sent to the [serverless inference API](#serverless-inference-api-endpoints).

Serverless inference automatically scales to handle incoming requests and supports generating text, images, audio, and other model outputs. Because serverless inference does not maintain sessions, each request must include the full context needed by the model.

All requests are [billed per input and output token](https://docs.digitalocean.com/products/gradient-ai-platform/details/pricing/index.html.md).

## When to Use Serverless Inference Versus Dedicated Inference

Dedicated Inference is a managed inference service that enables you to host and scale open-source and commercial LLMs on dedicated GPUs. It gives you more control over the environment so you can choose the GPU, tune performance, and optimize your models for throughput, latency, cost or concurrency. Dedicated inference is best suited for steady, high-throughput workloads.

Serverless inference lets you send API requests directly to foundation models. Choose serverless inference over dedicated inference when you need to get started quickly without managing any components behind an inference endpoint, don’t have a custom model to host or optimize, or have unpredictable or spiky inference traffic.

Pricing for serverless inference is based on the number of tokens used, while pricing for dedicated inference is based on the GPU hours used.

If you want to use dedicated inference, see [Use Dedicated Inference](https://docs.digitalocean.com/products/gradient-ai-platform/how-to/use-dedicated-inference-platform/index.html.md).

## Prerequisites

To use serverless inference, you need to authenticate your HTTP requests with a model access key. You can [create a model access key in the DigitalOcean Control Panel](#keys) or by sending a `POST` request to the [`/v2/gen-ai/models/api_keys` endpoint](https://docs.digitalocean.com/reference/api/digitalocean/index.html.md#tag/GradientAI-Platform/operation/genai_create_model_api_key). Then, send your prompts to models from OpenAI, Anthropic, Meta, or other providers using the [serverless inference API endpoints](#serverless-inference-api-endpoints).

## Serverless Inference API Endpoints

The serverless inference API is available at `https://inference.do-ai.run` and has the following endpoints:

| API | Endpoint | Verb | Description |
|---|---|---|---|
| Model | `/v1/models` | GET | Returns a list of available models and their IDs. |
| Chat Completions | `/v1/chat/completions` | POST | Sends chat-style prompts and returns model responses. |
| Responses | `/v1/responses` | POST | Sends chat-style prompts and returns text or multimodal model responses. |
| Images | `/v1/images/generations` | POST | Generates images from text prompts. |
| Images | `/v1/async-invoke` | POST | Sends text, image, or text-to-speech generation requests to [fal models](https://docs.digitalocean.com/products/gradient-ai-platform/details/models/index.html.md#foundation-models). |

We support both Chat Completions and Responses APIs for sending prompts. Choose the endpoint that best fits your use case:

- [Use the Chat Completions API](#chat-completions-api) when building or maintaining chat-style integrations that rely on structured `messages` with roles such as `system`, `user`, and `assistant`, or when migrating existing chat-based code with minimal changes.
- [Use the Responses API](#responses-api) when building new integrations or working with newer models that only support the Responses API. It's also useful for multi-step tool use in a single request, preserving state across turns with `store: true`, and simplifying requests by using a single `input` field with improved caching efficiency.

You can use these endpoints through [cURL](https://docs.digitalocean.com/reference/api/reference/serverless-inference/index.html.md), Python OpenAI, [Gradient Python SDK](https://gradientai-sdk.digitalocean.com/api/python), and [PyDo](https://docs.digitalocean.com/reference/pydo/reference/inference/index.html.md).

## Retrieve Available Models

The following cURL, Python OpenAI, Gradient Python SDK, and PyDo examples show how to retrieve available models.

### cURL

Send a GET request to the `/v1/models` endpoint using your model access key. For example:

```bash
curl -X GET https://inference.do-ai.run/v1/models \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json"
```

This returns a list of available models with their corresponding model IDs (`id`):

```js
...
{
  "created": 1752255238,
  "id": "alibaba-qwen3-32b",
  "object": "model",
  "owned_by": "digitalocean"
},
{
  "created": 1737056613,
  "id": "anthropic-claude-3.5-haiku",
  "object": "model",
  "owned_by": "anthropic"
},
...
```

### Python OpenAI

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://inference.do-ai.run/v1/",
    api_key=os.getenv("MODEL_ACCESS_KEY"),
)

models = client.models.list()
for m in models.data:
    print("-", m.id)
```

### Gradient Python SDK

```python
from gradient import Gradient
from dotenv import load_dotenv
import os

load_dotenv()

client = Gradient(model_access_key=os.getenv("MODEL_ACCESS_KEY"))

models = client.models.list()

print("Available models:")
for model in models.data:
    print(f"  - {model.id}")
```

### PyDo

```python
from pydo import Client
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(token=os.getenv("MODEL_ACCESS_KEY"))

models = client.inference.list_models()

print("Available models:")
for model in models["data"]:
    print(f"  - {model['id']}")
```

## Send Prompt to a Model Using the Chat Completions API

The following cURL, Python OpenAI, Gradient Python SDK, and PyDo examples show how to send a prompt to a model. Include your model access key and the following in your request:

- `model`: The model ID of the model you want to use. Get the model ID using `/v1/models` or on the [available models page](https://docs.digitalocean.com/products/gradient-ai-platform/details/models/index.html.md).
- `messages`: The input prompt or conversation history. Serverless inference does not have sessions, so include all relevant context using this field.
- `temperature`: A value between `0.0` and `1.0` to control randomness and creativity.
- `max_completion_tokens`: The maximum number of tokens to generate in the response. Use this to manage output length and cost.

  For Anthropic models, we recommend you specify this parameter for better accuracy and control of the model response. For models by other providers, this parameter is optional and defaults to around 2048 tokens.
- `max_tokens`: This parameter is deprecated. Use `max_completion_tokens` instead to control the size of the generated response.

You can also use prompt caching and reasoning parameters in your request. For examples, see [Use Prompt Caching](#use-prompt-caching) and [Use Reasoning](#use-reasoning).

### cURL

Send a POST request to the `/v1/chat/completions` endpoint using your model access key.

The following example request sends a prompt to a Llama 3.3 Instruct-70B model with the prompt `What is the capital of France?`, a temperature of 0.7, and maximum number of tokens set to 256.

```shell
curl -X POST https://inference.do-ai.run/v1/chat/completions \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.3-70b-instruct",
    "messages": [
        {
            "role": "user",
            "content": "What is the capital of France?"
            }
            ],
    "temperature": 0.7,
    "max_completion_tokens": 256
  }'
```

The response includes the generated text and token usage details:

```js
{
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "audio": null,
        "content": "The capital of France is Paris.",
        "refusal": null,
        "role": ""
      }
    }
  ],
  "created": 1747247763,
  "id": "",
  "model": "llama3.3-70b-instruct",
  "object": "chat.completion",
  "service_tier": null,
  "usage": {
    "completion_tokens": 8,
    "prompt_tokens": 43,
    "total_tokens": 51
  }
}
```

### Python OpenAI

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://inference.do-ai.run/v1/",
    api_key=os.getenv("MODEL_ACCESS_KEY"),
)

resp = client.chat.completions.create(
    model="llama3.3-70b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a fun fact about octopuses."}
    ],
)

print(resp.choices[0].message.content)
```

### Gradient Python SDK

```python
from gradient import Gradient
from dotenv import load_dotenv
import os

load_dotenv()

client = Gradient(model_access_key=os.getenv("MODEL_ACCESS_KEY"))

resp = client.chat.completions.create(
    model="llama3.3-70b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a fun fact about octopuses."}
    ],
)

print(resp.choices[0].message.content)
```

### PyDo

```python
from pydo import Client
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(token=os.getenv("MODEL_ACCESS_KEY"))

resp = client.inference.create_chat_completion(
    body={
        "model": "llama3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a fun fact about octopuses."},
        ],
    }
)
print(resp["choices"][0]["message"]["content"])
```

### Use Reasoning

For models that support [reasoning](https://en.wikipedia.org/wiki/Reasoning_model), you can pass a reasoning parameter in the request body either in OpenAI format using `reasoning_effort` or Anthropic format using `reasoning.effort`. The reasoning effort can be set to `none`, `low`, `medium`, `high` or `max`.

The following cURL example shows how to specify reasoning effort for Claude Opus 4.5 model in the Anthropic format:

```shell
curl -X POST https://inference.do-ai.run/v1/chat/completions \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic-claude-opus-4.5",
    "messages": [
      {
        "role": "user",
        "content": "What is 27 * 453? Think step by step."
      }
    ],
    "max_completion_tokens": 1192,
    "reasoning": {
      "effort": "high",
      "max_tokens": 1024
    }
  }'
```

The output shows the response shown step-by-step as requested in the model prompt:

```js
{
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "# Calculating 27 × 453\n\nI'll break this into smaller parts:\n\n**Step 1:** Break down 453 into 400 + 50 + 3\n\n**Step 2:** Multiply each part by 27\n- 27 × 400 = 10,800\n- 27 × 50 = 1,350\n- 27 × 3 = 81\n\n**Step 3:** Add the results\n- 10,800 + 1,350 + 81 = **12,231**",
                "reasoning_content": "I need to calculate 27 * 453.\n\nLet me break this down step by step.\n\n27 * 453 = 27 * (400 + 50 + 3)\n= 27 * 400 + 27 * 50 + 27 * 3\n\n27 * 400 = 10,800\n27 * 50 = 1,350\n27 * 3 = 81\n\n10,800 + 1,350 + 81 = 12,231",
                "refusal": null,
                "role": "assistant"
            }
        }
    ],
    "created": 1771946745,
    "id": "",
    "model": "anthropic-claude-opus-4.5",
    ...
}
```

**Note**:

  For Anthropic models, if you omit the `max_tokens` parameter for `reasoning` , we calculate the token budget using the following ratio of the total tokens passed in `max_completion_tokens`:

  | Effort Level | Reasoning Token Budget (% of `max_completion_tokens`) |
  |--------------|-------------------------------------------------------|
  | `low`        | 0.2                                                   |
  | `medium`     | 0.5                                                   |
  | `high`       | 0.8                                                   |
  | `max`        | 0.95                                                  |

The following cURL example shows how to specify reasoning effort for Claude Sonnet 4.6 model in the OpenAI format:

```shell
curl -X POST https://inference.do-ai.run/v1/chat/completions \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic-claude-4.6-sonnet",
    "messages": [
      {
        "role": "user",
        "content": "What is 27 * 453? Think step by step."
      }
    ],
    "max_completion_tokens": 8192,
    "reasoning_effort": "high"
  }'
```

The output looks like the following:

```js
{
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null,
            "message": {
                "content": "## Solving 27 × 453\n\nI'll break this into smaller, easier multiplications.\n\n**Split 453 into parts:**\n- 27 × 400\n- 27 × 50\n- 27 × 3\n\n**Calculate each part:**\n- 27 × 400 = **10,800**\n- 27 × 50 = **1,350**\n- 27 × 3 = **81**\n\n**Add the results:**\n- 10,800 + 1,350 = 12,150\n- 12,150 + 81 = **12,231**\n\n**27 × 453 = 12,231**",
                "reasoning_content": "27 * 453\n\nLet me break this down:\n27 * 453 = 27 * 400 + 27 * 50 + 27 * 3\n= 10800 + 1350 + 81\n= 12231",
                "refusal": null,
                "role": "assistant"
            }
        }
    ],
    "created": 1771948245,
    "id": "",
    "model": "anthropic-claude-4.6-sonnet",
    ...
}
```

## Send Prompt to a Model Using the Responses API

The following cURL, Python OpenAI, Gradient Python SDK, and PyDo examples show how to send a prompt using the `/v1/responses` endpoint. Include your model access key and the following in your request:

- `model`: The model ID of the model you want to use. Get the model ID using `/v1/models` or on the [available models page](https://docs.digitalocean.com/products/gradient-ai-platform/details/models/index.html.md).
- `input`: The prompt or input content you want the model to respond to.
- `max_output_tokens`: The maximum number of tokens to generate in the response.
- `temperature`: A value between `0.0` and `1.0` to control randomness and creativity.
- `stream`: Set to `true` to stream partial responses.

You can also use prompt caching parameters in your request. For examples, see [Use Prompt Caching](#use-prompt-caching) and [Use Reasoning](#use-reasoning).

### cURL

Send a POST request to the `/v1/responses` endpoint using your model access key.

The following example request sends a prompt to an OpenAI GPT-OSS-20B model with the prompt `What is the capital of France?`, a temperature of 0.7, and maximum number of output tokens set to 50.

```shell
curl -sS -X POST https://inference.do-ai.run/v1/responses \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai-gpt-oss-20b",
    "input": "What is the capital of France?",
    "max_output_tokens": 50,
    "temperature": 0.7,
    "stream": false
  }'
```

The response includes structured output and token usage details:

```js
{
  ...
  "output": [
    {
      "content": [
        {
          "text": "We need to answer: The capital of France is Paris. This is straightforward.",
          "type": "reasoning_text"
        }
      ],
      ...
    },
    {
      "content": [
        {
          "text": "The capital of France is **Paris**.",
          "type": "output_text"
        }
      ],
      ...
    }
  ],
  ...
  "usage": {
    "input_tokens": 72,
    "input_tokens_details": {
      "cached_tokens": 32
    },
    "output_tokens": 35,
    "output_tokens_details": {
      "reasoning_tokens": 17,
      "tool_output_tokens": 0
    },
    "total_tokens": 107
  },
  ...
}
```

### Python OpenAI

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://inference.do-ai.run/v1/",
    api_key=os.getenv("MODEL_ACCESS_KEY"),
)

resp = client.responses.create(
    model="openai-gpt-oss-20b",
    input="What is the capital of France?",
    max_output_tokens=50,
    temperature=0.7,
)

print(resp.output[1].content[0].text)
```

### Gradient Python SDK

```python
from gradient import Gradient
from dotenv import load_dotenv
import os

load_dotenv()

client = Gradient(model_access_key=os.getenv("MODEL_ACCESS_KEY"))

resp = client.responses.create(
    model="openai-gpt-oss-20b",
    input="What is the capital of France?",
    max_output_tokens=50,
    temperature=0.7,
)

print(resp.output[1].content[0].text)
```

### PyDo

```python
from pydo import Client
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(token=os.getenv("MODEL_ACCESS_KEY"))

resp = client.inference.create_response(
    body={
        "model": "openai-gpt-oss-20b",
        "input": "What is the capital of France?",
        "max_output_tokens": 50,
        "temperature": 0.7,
    }
)

print(resp["output"][1]["content"][0]["text"])
```

## Use Prompt Caching in Chat Completions and Responses API

### Anthropic Models

Use [prompt caching](https://docs.digitalocean.com/products/gradient-ai-platform/details/features/index.html.md#prompt-caching) for Anthropic models in the chat completions API. Specify the `cache_control` parameter with `type: ephemeral` and `ttl` in your JSON request body. The `ttl` value can be `5m` (default) or `1h`. The following request body examples show how to use the `cache_control` parameter.

### Single content part with cache control

```js
...
{
  "role": "user",
  "content": {
    "type": "text",
    "text": "This is cached for 1h.",
    "cache_control": {
      "type": "ephemeral",
      "ttl": "1h"
    }
  }
}
```

### Array of content parts (mixed cached and non-cached request)

```js
...
{
  "role": "developer",
  "content": [
    {
      "type": "text",
      "text": "Cache this segment for 5 minutes.",
      "cache_control": {
        "type": "ephemeral",
        "ttl": "5m"
      }
    },
    {
      "type": "text",
      "text": "Do not cache this segment"
    }
  ]
}
```

### Tool message content with cache control

```js
...
{
  "role": "tool",
  "tool_call_id": "tool_call_id",
  "content": [
    {
      "type": "text",
      "text": "Tool output cached for 5m.",
      "cache_control": {
        "type": "ephemeral",
        "ttl": "5m"
      }
    }
  ]
}
```

The JSON response looks similar to the following and shows the number of input tokens cached during this request:

```js
"usage": {
        "cache_created_input_tokens": 1043,
        "cache_creation": {
            "ephemeral_1h_input_tokens": 0,
            "ephemeral_5m_input_tokens": 1043
        },
        "cache_read_input_tokens": 0,
        "completion_tokens": 100,
        "prompt_tokens": 14,
        "total_tokens": 114
    }
```

If you send the request again, cached input tokens are used and the response looks like this:

```js
"usage": {
        "cache_created_input_tokens": 0,
        "cache_creation": {
            "ephemeral_1h_input_tokens": 0,
            "ephemeral_5m_input_tokens": 0
        },
        "cache_read_input_tokens": 1043,
        "completion_tokens": 100,
        "prompt_tokens": 14,
        "total_tokens": 114
    }
```

### OpenAI Models

Use [prompt caching](https://docs.digitalocean.com/products/gradient-ai-platform/details/features/index.html.md#prompt-caching) for OpenAI models for prompts containing 1024 tokens or more in both chat completions and responses API. Caching applies when the input tokens of a response match tokens from a previous response, though this is best-effort and not guaranteed.

To use prompt caching, specify the `prompt_cache_retention` parameter as either `in_memory` or `24h`. The following request body example shows how to use the `prompt_cache_retention` parameter:

```js
...
{
  "model": "gpt-4o-mini",
  "prompt_cache_retention": "24h",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant that summarizes text."
    },
    {
      "role": "user",
      "content": "Summarize the following text:\n\nArtificial intelligence is transforming industries by automating tasks, improving efficiency, and enabling new innovations..."
    }
  ],
  "temperature": 0.2
}
```

The JSON response looks similar to the following and shows the number of input tokens cached during this request:

```js
{
  "id": "chatcmpl-xyz789",
  "object": "chat.completion",
  "created": 1772134300,
  "model": "gpt-4o-mini",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "Artificial intelligence is reshaping industries by automating processes, increasing efficiency, and enabling innovation."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 35,
    "total_tokens": 1235,
    "cache_read_input_tokens": 0,
    "cache_created_input_tokens": 1200,
    "cache_creation": {
      "ephemeral_5m_input_tokens": 0,
      "ephemeral_1h_input_tokens": 1200
    }
  }
}
```

If you send the request again within the retention window, cached input tokens are used and the response looks like this:

```js
"usage": {
  "prompt_tokens": 1200,
  "completion_tokens": 34,
  "total_tokens": 1234,
  "cache_read_input_tokens": 1200,
  "cache_created_input_tokens": 0,
  "cache_creation": {
    "ephemeral_5m_input_tokens": 0,
    "ephemeral_1h_input_tokens": 0
  }
}
```

## Generate Image from Text Prompt

The following cURL, Python OpenAI, Gradient Python SDK, and PyDo examples show how to generate an image from a text prompt. Include your model access key and the following in your request:

- `model`: The model ID of the image generation model you want to use. Get the model ID using `/v1/models` or on the [available models page](https://docs.digitalocean.com/products/gradient-ai-platform/details/models/index.html.md).
- `prompt`: The text prompt to generate the image from.
- `n`: The number of images to generate. Must be between 1 and 10.
- `size`: The desired dimensions of the generated image. Supported values are `256x256`, `512x512`, and `1024x1024`.

Make sure to always specify `n` and `size` when generating images.

### cURL

Send a POST request to the `/v1/images/generations` endpoint using your model access key.

The following example request sends a prompt to the `openai-gpt-image-1` model to generate an image of a baby sea otter floating on its back in calm blue water, with an image size of 1024x1024:

```shell
curl -X POST https://inference.do-ai.run/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -d '{
    "model": "openai-gpt-image-1",
    "prompt": "A cute baby sea otter floating on its back in calm blue water",
    "n": 1,
    "size": "1024x1024"
  }'
```

The response includes a JSON object with a Base64 image string and other details such as image format and tokens used:

```js
{
    "background": "opaque",
    "created": 1770659857,
    "data": [
        {
            "b64_json": "iVBORw0KGgoAAAANSUhEU...
        }
    ],
    "output_format": "png",
    "quality": "medium",
    "size": "1024x1024",
    "usage": {
        "input_tokens": 20,
        "input_tokens_details": {
            "text_tokens": 20
        },
        "output_tokens": 1056,
        "total_tokens": 1076
    }
}
```

If you want to save the image as a file, pipe the image string to a file using `jq` and `base64`:

```shell
curl -X POST https://inference.do-ai.run/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -d '{
    "model": "openai-gpt-image-1",
    "prompt": "A cute baby sea otter floating on its back in calm blue water",
    "n": 1,
    "size": "1024x1024"
  }' | jq -r '.data[0].b64_json' | base64 --decode > sea_otter.png
```

An image named `sea_otter.png` is created in your current directory after a few seconds.

### Python OpenAI

```python
from openai import OpenAI
from dotenv import load_dotenv
import os, base64

load_dotenv()

client = OpenAI(
    base_url="https://inference.do-ai.run/v1/",
    api_key=os.getenv("MODEL_ACCESS_KEY"),
)

result = client.images.generate(
    model="openai-gpt-image-1",
    prompt="A cute baby sea otter, children’s book drawing style",
    size="1024x1024",
    n=1
)

b64 = result.data[0].b64_json
with open("sea_otter.png", "wb") as f:
    f.write(base64.b64decode(b64))

print("Saved sea_otter.png")
```

### Gradient Python SDK

```python
from gradient import Gradient
from dotenv import load_dotenv
import os, base64

load_dotenv()

client = Gradient(model_access_key=os.getenv("MODEL_ACCESS_KEY"))

result = client.images.generations.create(
    model="openai-gpt-image-1",
    prompt="A cute baby sea otter, children's book drawing style",
    size="1024x1024",
    n=1
)

b64 = result.data[0].b64_json
with open("sea_otter.png", "wb") as f:
    f.write(base64.b64decode(b64))

print("Saved sea_otter.png")
```

### PyDo

```python
from pydo import Client
from dotenv import load_dotenv
import os, base64

load_dotenv()

client = Client(token=os.getenv("MODEL_ACCESS_KEY"))

result = client.inference.create_image(
    body={
        "model": "openai-gpt-image-1",
        "prompt": "A cute baby sea otter, children's book drawing style",
        "size": "1024x1024",
        "n": 1,
    }
)

b64 = result["data"][0]["b64_json"]
with open("sea_otter.png", "wb") as f:
    f.write(base64.b64decode(b64))

print("Saved sea_otter.png")
```

## Generate Image, Audio, or Text-to-Speech Using fal Models

The following examples show how to generate an image or audio clip, or use text-to-speech with [fal models](https://docs.digitalocean.com/products/gradient-ai-platform/details/models/index.html.md#foundation-models) with the `/v1/async-invoke` endpoint.

### Generate Image

The following example sends a request to generate an image using the `fal-ai/fast-sdxl` model.

```shell
curl -X POST 'https://inference.do-ai.run/v1/async-invoke' \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fal-ai/flux/schnell",
    "input": { "prompt": "A futuristic city at sunset" }
  }'
```

You can update the image generation request to also include the output format, number of inference steps, guidance scale, number of images to generate, and safety checker option:

```shell
curl -X POST https://inference.do-ai.run/v1/async-invoke \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fal-ai/fast-sdxl",
    "input": {
      "prompt": "A futuristic cityscape at sunset, with flying cars and towering skyscrapers.",
      "output_format": "landscape_4_3",
      "num_inference_steps": 4,
      "guidance_scale": 3.5,
      "num_images": 1,
      "enable_safety_checker": true
    },
    "tags": [
      {"key": "type", "value": "test"}
    ]
}'
```

### Generate Audio

The following example sends a request to generate a 60 second audio clip using the `fal-ai/stable-audio-25/text-to-audio` model:

```shell
curl -X POST 'https://inference.do-ai.run/v1/async-invoke' \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fal-ai/stable-audio-25/text-to-audio",
    "input": {
      "prompt": "Techno song with futuristic sounds",
      "seconds_total": 60
    },
    "tags": [
      { "key": "type", "value": "test" }
    ]
  }'
```

### Use Text-to-Speech

The following example sends a request to generate text-to-speech audio using the `fal-ai/multilingual-tts-v2` model:

```shell
curl -X POST 'https://inference.do-ai.run/v1/async-invoke' \
  -H "Authorization: Bearer $MODEL_ACCESS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "fal-ai/elevenlabs/tts/multilingual-v2",
    "input": {
      "text": "This text-to-speech example uses DigitalOcean multilingual voice."
    },
    "tags": [
      { "key": "type", "value": "test" }
    ]
  }'
```

When you send a request to the `/v1/async-invoke` endpoint, it starts an asynchronous job for the image, audio, or text-to-speech generation and returns a `request_id`. The job `status` is `QUEUED` initially and the response looks similar to the following:

```shell
"completed_at": null,
"created_at": "2026-01-22T19:19:19.112403432Z",
"error": null,
"model_id": "fal-ai/fast-sdxl",
"output": null,
"request_id": "6590784a-ce47-4556-9ff4-53baff2693fb",
"started_at": null,
"status": "QUEUED"
```

Query the `status` endpoint frequently using the `request_id` to check the progress of the job:

```
curl -X GET &#34;https://inference.do-ai.run/v1/async-invoke/&lt;request_id&gt;/status&#34; \
  -H &#34;Authorization: Bearer $MODEL_ACCESS_KEY&#34;
```

When the job completes, the `status` updates to `COMPLETE`. You can then use the `/async-invoke/&lt;request_id&gt;` endpoint to fetch the complete generated result:

```
curl -X GET &#34;https://inference.do-ai.run/v1/async-invoke/&lt;request_id&gt;&#34; \
  -H &#34;Authorization: Bearer $MODEL_ACCESS_KEY&#34;
```

The response includes a URL to the generated image, audio, or text-to-speech file, which you can download or open directly in your browser or app:

```js
{
...
        "images": [
            {
                "content_type": "image/jpeg",
                "height": 768,
                "url": "https://v3b.fal.media/files/b/0a8b7281/HpQcEqkz-xy2ZI5do9Lyp.jpg",
                "width": 1024
            }
        ...
    },
    "request_id": "6f76e8f7-f6b4-4e20-ab9a-ca0f01a9d2f4",
    "started_at": null,
    "status": "COMPLETED"
}
```

Alternatively, you can call serverless inference from your automation workflows. The [n8n community node](https://www.npmjs.com/package/@digitalocean/n8n-nodes-digitalocean-gradient-serverless-inference) connects to any DigitalOcean-hosted model using your model access key. You can self-host n8n using the [n8n Marketplace app](https://marketplace.digitalocean.com/apps/n8n).

## Model Access Keys

You can create and manage model access keys in the **Model Access Keys** section of the [**Serverless inference** page](https://cloud.digitalocean.com/gen-ai/model-access-keys) in the DigitalOcean Control Panel or using the API.

### Create Keys

### Using the control panel

To create a model access key, click **Create model access key** to open the **Add model access key** window. In the **Key name** field, enter a name for your model access key, then click **Add model access key**.

Your new model access key with its creation date appears in the **Model Access Keys** section. The secret key is visible only once, immediately after creation, so copy and store it securely.

### Using API

## How to Create Model API Key Using the DigitalOcean API

1. [Create a personal access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/index.html.md) and save it for use with the API.
2. Send a POST request to [`https://api.digitalocean.com/v2/gen-ai/models/api_keys`](https://docs.digitalocean.com/reference/api/reference/gradientai-platform/index.html.md#genai_create_model_api_key).

### cURL

Using cURL:

```shell
curl -X POST \
  -H "Content-Type: application/json"  \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  "https://api.digitalocean.com/v2/gen-ai/models/api_keys" \
  -d '{
    "name": "test-key"
  }'
```

Model access keys are private and incur [usage-based charges](https://docs.digitalocean.com/products/gradient-ai-platform/details/pricing/index.html.md). Do not share them or expose them in front-end code. We recommend storing them using a secrets manager (for example, AWS Secrets Manager, HashiCorp Vault, or 1Password) or a secure environment variable in your deployment configuration.

### Rename Keys

Renaming a model access key can help you organize and manage your keys more effectively, especially when using multiple keys for different projects or environments.

### Using the control panel

To rename a key, click **…** to the right of the key in the list to open the key’s menu, then click **Rename**. In the **Rename model access key** window that opens, in the **Key name** field, enter a new name for your key and then click **UPDATE**.

### Using API

## How to Rename Model API Key Using the DigitalOcean API

1. [Create a personal access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/index.html.md) and save it for use with the API.
2. Send a PUT request to [`https://api.digitalocean.com/v2/gen-ai/models/api_keys/{api_key_uuid}`](https://docs.digitalocean.com/reference/api/reference/gradientai-platform/index.html.md#genai_update_model_api_key).

### cURL

Using cURL:

```shell
curl -X PUT \
  -H "Content-Type: application/json"  \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  "https://api.digitalocean.com/v2/gen-ai/models/api_keys/11efb7d6-cdb5-6388-bf8f-4e013e2ddde4" \
  -d '{
    "api_key_uuid": "11efb7d6-cdb5-6388-bf8f-4e013e2ddde4",
    "name": "test-key2"
  }'
```

### Regenerate Keys

Regenerating a model access key creates a new secret key and immediately and permanently invalidates the previous one. If a key has been compromised or want to rotate keys for security purposes, regenerate the key, then update any applications using the previous key to use the new key.

### Using the control panel

To regenerate a key, click **…** to the right of the key in the list to open the key’s menu, then click **Regenerate**. In the **Regenerate model access key** window that opens, enter the name of your key to confirm the action, then click **Regenerate access key**. Your new secret key is displayed in the **Model Access Keys** section.

### Using API

## How to Regenerate Model API Key Using the DigitalOcean API

1. [Create a personal access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/index.html.md) and save it for use with the API.
2. Send a PUT request to [`https://api.digitalocean.com/v2/gen-ai/models/api_keys/{api_key_uuid}/regenerate`](https://docs.digitalocean.com/reference/api/reference/gradientai-platform/index.html.md#genai_regenerate_model_api_key).

### cURL

Using cURL:

```shell
curl -X PUT \
  -H "Content-Type: application/json"  \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  "https://api.digitalocean.com/v2/gen-ai/models/api_keys/11efcf7e-824d-2808-bf8f-4e013e2ddde4/regenerate"
```

### Delete Keys

Deleting a model access key permanently and irreversibly destroys it. Any applications using a destroyed key lose access to the API.

### Using the control panel

To delete a key, click **…** to the right of the key in the list to open the key’s menu, then click **Delete**. In the **Delete model access key** window that opens, type the name of the key to confirm the deletion, then click **Delete access key**.

### Using API

## How to Delete Model API Key Using the DigitalOcean API

1. [Create a personal access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/index.html.md) and save it for use with the API.
2. Send a DELETE request to [`https://api.digitalocean.com/v2/gen-ai/models/api_keys/{api_key_uuid}`](https://docs.digitalocean.com/reference/api/reference/gradientai-platform/index.html.md#genai_delete_model_api_key).

### cURL

Using cURL:

```shell
curl -X DELETE \
  -H "Content-Type: application/json"  \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  "https://api.digitalocean.com/v2/gen-ai/models/api_keys/11efb7d6-cdb5-6388-bf8f-4e013e2ddde4"
```

## Use Serverless Inference After Updating to Another Model

If you change the foundation model at any time, you must take the following steps:

- **Update the model ID in your CLI/API calls, serverless inference requests, and ADK code**: Update the model ID parameter in your code to the new model ID.
- **Review prompt logic**: While new models are largely backward compatible, we recommend [reviewing your system prompts](https://docs.digitalocean.com/products/gradient-ai-platform/concepts/prompts/index.html.md), as the new model follows instructions more precisely. You may need to adjust your prompts to get the desired response format.
