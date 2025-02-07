#!/bin/bash

MODEL_PATH="/home/yhj2263/llama/models/Llama-3.1-8B-Instruct"
PORT=8001

vllm serve $MODEL_PATH \
--gpu-memory-utilization 0.9 \
--max-model-len 4096 \
--port $PORT \
--enable-auto-tool-choice \
--tool-call-parser llama3_json \
--chat-template /home/yhj2263/projects/llama-chatbot/src/api/huggingface_chat_template.jinja
