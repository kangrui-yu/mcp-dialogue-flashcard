from __future__ import annotations
import json
from typing import List, Dict, Callable, Optional

from .schemas import GeneratorOutput, CriticOutput, AgentContext
from .agents import Generator, Critic, Refiner
from .utils import LoggerMixin, create_openai_client


class MultiAgentLatentExtractor(LoggerMixin):

    BEAM_WIDTH = 1
    ACCEPT_SCORE = 4

    def __init__(self, model: str = "gpt-4o-mini", max_refiner_loops: int = 3):
        """
        Initialize the multi-agent extractor.

        Args:
            model: OpenAI model to use for all agents
            max_refiner_loops: Maximum number of refinement iterations
        """
        super().__init__()

        self.max_refiner_loops = max_refiner_loops
        self.model = model
        self.critic_model = model

        # Initialize OpenAI client
        self.client = create_openai_client()

        # Initialize agents
        self.generator = Generator(self.client, self.model, self.BEAM_WIDTH)
        self.critic = Critic(self.client, self.critic_model)
        self.refiner = Refiner(self.client, self.model)

    def _search_latent(self, dialogue: List[Dict]) -> str:
        self._log_problem_start(dialogue)

        # Initialize context for tracking agent interactions
        context = AgentContext(dialogue)

        # 1) Generate candidates using beam search
        candidates = self.generator.generate_candidates(dialogue)

        # 2) Score candidates with critic and pick the best
        best_candidate, best_critic = None, None
        for candidate in candidates:
            critic_output = self.critic.evaluate_candidate(
                dialogue, candidate, context)
            context.add_generator_output(candidate)
            context.add_critic_output(critic_output)

            if best_critic is None or critic_output.score > best_critic.score:
                best_candidate, best_critic = candidate, critic_output

        # Log initial generation result
        self._log_initial_generation(best_candidate, best_critic)

        # 3) Refine until accepted or retries exhausted
        loops = 0
        while best_critic.score < self.ACCEPT_SCORE and loops < self.max_refiner_loops:
            loops += 1

            # Log refinement loop start
            self._log_refinement_loop_start(
                loops, best_candidate.latent, best_critic)

            # Refine the concept
            new_latent = self.refiner.refine_concept(
                best_candidate, best_critic, context)
            context.add_refiner_output(new_latent)

            # Update candidate and re-evaluate
            best_candidate = GeneratorOutput(
                latent=new_latent,
                argument=best_candidate.argument
            )
            best_critic = self.critic.evaluate_candidate(
                dialogue, best_candidate, context)
            context.add_critic_output(best_critic)

            # Log refinement loop result
            self._log_refinement_loop_result(loops, new_latent, best_critic)

        # Log final result
        self._log_problem_end(best_candidate.latent, best_critic, loops)
        return best_candidate.latent

    def _search_latent_with_progress(self, dialogue: List[Dict], progress_callback: Optional[Callable] = None) -> str:
        # Import TaskStage here to avoid circular imports
        try:
            from ..task_manager import TaskStage
        except ImportError:
            # Fallback if TaskStage is not available
            TaskStage = None

        def report_progress(stage, message=""):
            if progress_callback and TaskStage:
                progress_callback(stage, message)

        # Start problem logging
        self._log_problem_start(dialogue)

        # Initialize context for tracking agent interactions
        context = AgentContext(dialogue)

        report_progress(TaskStage.GENERATION if TaskStage else None,
                        "Generating concept candidates")

        # 1) Generate candidates using beam search
        candidates = self.generator.generate_candidates(dialogue)

        report_progress(TaskStage.CRITICISM if TaskStage else None,
                        "Evaluating candidates")

        # 2) Score candidates with critic and pick the best
        best_candidate, best_critic = None, None
        for candidate in candidates:
            critic_output = self.critic.evaluate_candidate(
                dialogue, candidate, context)
            context.add_generator_output(candidate)
            context.add_critic_output(critic_output)

            if best_critic is None or critic_output.score > best_critic.score:
                best_candidate, best_critic = candidate, critic_output

        # Log initial generation result
        self._log_initial_generation(best_candidate, best_critic)

        # 3) Refine until accepted or retries exhausted
        loops = 0
        while best_critic.score < self.ACCEPT_SCORE and loops < self.max_refiner_loops:
            loops += 1

            # Report refinement progress
            if TaskStage:
                if loops == 1:
                    stage = TaskStage.REFINEMENT_LOOP_1
                elif loops == 2:
                    stage = TaskStage.REFINEMENT_LOOP_2
                elif loops == 3:
                    stage = TaskStage.REFINEMENT_LOOP_3
                else:
                    stage = TaskStage.REFINEMENT_LOOP_3  # Fallback for additional loops

                report_progress(
                    stage, f"Refinement iteration {loops} (score: {best_critic.score})")

            # Log refinement loop start
            self._log_refinement_loop_start(
                loops, best_candidate.latent, best_critic)

            # Refine the concept
            new_latent = self.refiner.refine_concept(
                best_candidate, best_critic, context)
            context.add_refiner_output(new_latent)

            # Update candidate and re-evaluate
            best_candidate = GeneratorOutput(
                latent=new_latent,
                argument=best_candidate.argument
            )
            best_critic = self.critic.evaluate_candidate(
                dialogue, best_candidate, context)
            context.add_critic_output(best_critic)

            # Log refinement loop result
            self._log_refinement_loop_result(loops, new_latent, best_critic)

        # Log final result
        self._log_problem_end(best_candidate.latent, best_critic, loops)
        return best_candidate.latent

    def predict(self, dialogue: List[Dict]) -> str:
        return self._search_latent(dialogue)

    def predict_with_progress(
        self,
        dialogue: List[Dict],
        progress_callback: Optional[Callable] = None
    ) -> str:
        return self._search_latent_with_progress(dialogue, progress_callback)
