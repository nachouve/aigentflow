#!/usr/bin/env python
# coding=utf-8

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


### USAGE: 
#  python agents/smolagents_cli.py --model-type HfApiModel --model-id Qwen/Qwen2.5-Coder-32B-Instruct --tools web_search --verbosity-level 1
#  python smolagents_cli.py "your prompt here" --model-type LiteLLMModel --model-id google/gemini-1.5-pro


import argparse
import os

from dotenv import load_dotenv

from smolagents import CodeAgent, HfApiModel, LiteLLMModel, Model, OpenAIServerModel, Tool, TransformersModel
from smolagents.default_tools import TOOL_MAPPING

leopard_prompt = """Please tell me the layers available in this service endpoint: https://www.ign.es/wmts/pnoa-ma?"""

sys_prompt = """
You are a AI Agent expert in Geographic Information Systems (GIS).
WMS, WFS, WMTS, etc. has no secrets for you.

So you can help to inspect and request to that kind of services, getCapabilities, list layers, etc. and help to understand the data.
"""


def parse_arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",  # Makes it optional
        default=leopard_prompt,
        help="The prompt to run with the agent",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="HfApiModel",
        help="The model type to use (e.g., HfApiModel, OpenAIServerModel, LiteLLMModel, TransformersModel)",
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="Qwen/Qwen2.5-Coder-32B-Instruct",
        help="The model ID to use for the specified model type",
    )
    parser.add_argument(
        "--imports",
        nargs="*",  # accepts zero or more arguments
        default=[],
        help="Space-separated list of imports to authorize (e.g., 'numpy pandas')",
    )
    parser.add_argument(
        "--tools",
        nargs="*",
        default=["web_search"],
        help="Space-separated list of tools that the agent can use (e.g., 'tool1 tool2 tool3')",
    )
    parser.add_argument(
        "--verbosity-level",
        type=int,
        default=1,
        help="The verbosity level, as an int in [0, 1, 2].",
    )
    group = parser.add_argument_group("api options", "Options for API-based model types")
    group.add_argument(
        "--api-base",
        type=str,
        help="The base URL for the model",
    )
    group.add_argument(
        "--api-key",
        type=str,
        help="The API key for the model",
    )
    return parser.parse_args()


def load_model(model_type: str, model_id: str, api_base: str | None, api_key: str | None) -> Model:
    if model_type == "OpenAIServerModel":
        return OpenAIServerModel(
            api_key=api_key or os.getenv("FIREWORKS_API_KEY"),
            api_base=api_base or "https://api.fireworks.ai/inference/v1",
            model_id=model_id,
        )
    elif model_type == "LiteLLMModel":
        model_base_id = model_id.split("/")[0]
        if model_base_id == "google" or model_base_id == "gemini":
            import litellm
            litellm._turn_on_debug()
            api_key = api_key or os.getenv("GEMINI_API_KEY")
            print(model_id, api_key)
        return LiteLLMModel(
            model_id=model_id,
            api_key=api_key,
            #api_base=api_base, # Leave the LiteLLMModel to determine the api_base
        )
    elif model_type == "TransformersModel":
        return TransformersModel(model_id=model_id, device_map="auto", flatten_messages_as_text=False)
    elif model_type == "HfApiModel":
        return HfApiModel(
            token=api_key or os.getenv("HF_API_KEY"),
            model_id=model_id,
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


def main():
    load_dotenv()

    args = parse_arguments(description="Run a CodeAgent with all specified parameters")

    model = load_model(args.model_type, args.model_id, args.api_base, args.api_key)

    available_tools = []
    for tool_name in args.tools:
        if "/" in tool_name:
            available_tools.append(Tool.from_space(tool_name))
        else:
            if tool_name in TOOL_MAPPING:
                available_tools.append(TOOL_MAPPING[tool_name]())
            else:
                raise ValueError(f"Tool {tool_name} is not recognized either as a default tool or a Space.")

    print(f"Running agent with these tools: {args.tools}")
    agent = CodeAgent(tools=available_tools, model=model, additional_authorized_imports=args.imports)

    agent.run(args.prompt)


if __name__ == "__main__":
    main()
