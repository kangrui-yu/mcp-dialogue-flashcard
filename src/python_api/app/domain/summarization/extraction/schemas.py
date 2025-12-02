from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel, Field


class GeneratorOutput(BaseModel):
    """Output schema for the latent concept generator agent."""
    latent: str = Field(..., max_length=60)
    argument: str = Field(..., max_length=1000)


class CriticOutput(BaseModel):
    """Output schema for the critic evaluation agent."""
    verdict: str = Field(..., pattern="^(approve|reject)$")
    score: int = Field(..., ge=0, le=4)
    critique: str = Field(..., max_length=200)


class RefinerOutput(BaseModel):
    """Output schema for the refiner improvement agent."""
    latent: str = Field(..., max_length=60)


class AgentContext:
    """
    Tracks the full history of agent interactions for context-aware decision making.

    This class maintains state across the generator-critic-refiner loops to enable
    agents to learn from previous attempts and avoid repeated failures.
    """

    def __init__(self, dialogue: List[Dict]):
        """Initialize context with the original dialogue."""
        self.dialogue = dialogue
        self.generator_history: List[GeneratorOutput] = []
        self.critic_history: List[CriticOutput] = []
        self.refiner_history: List[str] = []  # List of refined latents
        self.current_loop = 0

    def add_generator_output(self, output: GeneratorOutput) -> None:
        """Add a generator output to history."""
        self.generator_history.append(output)

    def add_critic_output(self, output: CriticOutput) -> None:
        """Add a critic evaluation to history."""
        self.critic_history.append(output)

    def add_refiner_output(self, refined_latent: str) -> None:
        """Add a refiner output to history."""
        self.refiner_history.append(refined_latent)
        self.current_loop += 1

    def get_context_summary(self) -> Dict:
        """Get a summary of all previous interactions."""
        return {
            "total_loops": self.current_loop,
            "generator_attempts": len(self.generator_history),
            "critic_evaluations": len(self.critic_history),
            "refinement_attempts": len(self.refiner_history),
            "previous_latents": [g.latent for g in self.generator_history] + self.refiner_history,
            "previous_scores": [c.score for c in self.critic_history],
            "previous_critiques": [c.critique for c in self.critic_history]
        }
