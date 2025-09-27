from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Basic setup

from langchain_community.llms import Minimax

minimax = Minimax(minimax_api_key="YOUR_API_KEY", minimax_group_id="YOUR_GROUP_ID")

template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)
llm = Minimax()

chain = LLMChain(prompt=prompt, llm=llm)

question = "What is the capital of France?"

chain.run(question)
