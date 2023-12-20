import os
from llama_index.multi_modal_llms import ReplicateMultiModal
from llama_index.program import MultiModalLLMCompletionProgram
from llama_index.output_parsers import PydanticOutputParser
from llama_index.multi_modal_llms.replicate_multi_modal import (
    REPLICATE_MULTI_MODAL_LLM_MODELS,
)
from llama_index import SimpleDirectoryReader
from data_model import Receipt
from pydantic import BaseModel


PROMPT_TEMPLATE = """Extract out relevant details from a receipt image and return the answer with json format:
The business name should be on top of the receipt.
The date of the receipt should be of the following format: `DD/MM/YYYY`.
The total of the receipt should be beside the word `Total` and should have at least 2 decimal places.
The category of the expense should be in any of the following list `Food, Transport, Utility Bills, Shopping, Entertainment, Investment`.
"""

def get_multimodal_model(model_name: str = "llava-13b",
                         max_new_tokens: int = 1000) -> ReplicateMultiModal:
    """
    Get a multi-modal model
    """

    return ReplicateMultiModal(
        model=REPLICATE_MULTI_MODAL_LLM_MODELS[model_name],
        max_new_tokens=max_new_tokens,
    )

def extract(dataclass,
            img_documents,
            prompt,
            llm):
    return MultiModalLLMCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(dataclass),
        image_documents=img_documents,
        prompt_template_str=prompt,
        multi_modal_llm=llm,
        verbose=True,
    )()

def get_image_documents(image_dir: str):
    return SimpleDirectoryReader(image_dir).load_data()

