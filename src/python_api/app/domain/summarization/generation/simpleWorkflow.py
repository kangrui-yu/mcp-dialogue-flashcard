import os
from pydantic import BaseModel
from openai import OpenAI
import os


class FlashCardSchema(BaseModel):
    question: str
    answer: str


class FlashCardGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.sys_prompt = """
        You are an expert flashcard generator. Given a concept, generate a concise question and answer pair.
        Example 1:
        Concept: Binary Search
        Question: What is the time complexity of binary search in a sorted array?
        Answer: O(log n)
        Example 2:
        Concept: Conditional Independence
        Question: What does it mean for two events A and B to be conditionally independent given event C?
        Answer: It means that the occurrence of A provides no information about B once C is known
        Example 3:
        Concept: Back Propagation
        Question: What is the purpose of back propagation in neural networks?
        Answer: To compute the gradient of the loss function with respect to each weight by the chain
"""
        self.model = "gpt-4o-mini"
        self.schema = FlashCardSchema

    def generate(self, concept: str) -> FlashCardSchema:
        usr_prompt = f"Generate a flashcard for the following concept:\nConcept: {concept}\nFlashcard:"
        response = self.client.responses.parse(
            model=self.model,
            temperature=0.5,
            input=[
                {"role": "system", "content": self.sys_prompt},
                {"role": "user", "content": usr_prompt}
            ],
            text_format=self.schema,
        )
        return response.output_parsed
