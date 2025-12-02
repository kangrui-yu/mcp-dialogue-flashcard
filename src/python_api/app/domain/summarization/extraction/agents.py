from __future__ import annotations
import json
from typing import List, Dict
from openai import OpenAI

from .schemas import GeneratorOutput, CriticOutput, RefinerOutput, AgentContext
from .prompts import (
    get_generator_prompt,
    get_critic_prompt,
    get_refiner_prompt_approved,
    get_refiner_prompt_rejected
)


class Generator:

    def __init__(self, client: OpenAI, model: str, beam_width: int = 1):
        self.client = client
        self.model = model
        self.beam_width = beam_width

    def generate_candidates(self, dialogue: List[Dict]) -> List[GeneratorOutput]:
        """Generate latent concept candidates from the dialogue."""
        sys_prompt = get_generator_prompt()

        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=0.5,
            n=self.beam_width,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": json.dumps(
                    dialogue, ensure_ascii=False, indent=2)},
            ],
        )

        candidates: List[GeneratorOutput] = []
        for choice in resp.choices:
            try:
                candidates.append(
                    GeneratorOutput.model_validate_json(choice.message.content))
            except Exception:
                pass

        return candidates


class Critic:

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def evaluate_candidate(self, dialogue: List[Dict], candidate: GeneratorOutput, context: AgentContext) -> CriticOutput:
        """Evaluate a candidate latent concept."""
        sys_prompt = get_critic_prompt()

        # Build context summary for critic
        context_summary = context.get_context_summary()

        # Build user input with context
        user_content = {
            "candidate": candidate.model_dump(),
            "dialogue": dialogue,
            "interaction_history": context_summary if context_summary["total_loops"] > 0 else None
        }

        resp = self.client.responses.parse(
            model=self.model,
            temperature=0.5,
            input=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": json.dumps(
                    user_content, ensure_ascii=False, indent=2)},
            ],
            text_format=CriticOutput,
        )

        return resp.output_parsed


class Refiner:

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def refine_concept(self, candidate: GeneratorOutput, critic: CriticOutput, context: AgentContext) -> str:
        """Refine a latent concept based on critic feedback."""
        # Choose prompt based on critic verdict
        if critic.verdict == "approve":
            sys_prompt = get_refiner_prompt_approved()
        else:
            sys_prompt = get_refiner_prompt_rejected()

        # Build context summary for refiner
        context_summary = context.get_context_summary()

        # Build user input with context
        user_content = {
            "current_latent": candidate.latent,
            "current_critique": critic.critique,
            "interaction_history": context_summary if context_summary["total_loops"] > 0 else None
        }

        resp = self.client.responses.parse(
            model=self.model,
            temperature=0.5,
            input=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": json.dumps(
                    user_content, ensure_ascii=False, indent=2)},
            ],
            text_format=RefinerOutput,
        )

        return resp.output_parsed.latent
