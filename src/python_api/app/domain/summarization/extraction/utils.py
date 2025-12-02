import os
import json
import datetime
from typing import Dict, Any
from openai import OpenAI


class LoggerMixin:
    """Mixin class providing structured logging functionality."""

    def __init__(self):
        """Initialize logger with timestamped log file."""
        self._ensure_logdir()
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_path = f"logs/{ts}.log"

    def _ensure_logdir(self, path: str = "logs") -> None:
        """Ensure log directory exists."""
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

    def _log(self, stage: str, kind: str, data: Any) -> None:
        """Log structured data to file."""
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(f"\n>>> [{stage}] {kind.upper()} >>>\n" +
                     json.dumps(data, ensure_ascii=False, indent=2) + "\n<<< END >>>\n")

    def _log_problem_start(self, dialogue: list) -> None:
        """Log the start of a new problem with clear separation."""
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write("\n" + "="*50 + " PROBLEM START " + "="*50 + "\n")
            fh.write("ORIGINAL_DIALOGUE:\n")
            fh.write(json.dumps(dialogue, ensure_ascii=False, indent=2) + "\n")

    def _log_initial_generation(self, best_candidate, best_critic) -> None:
        """Log the initial generator output and critic score."""
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write("\nINITIAL_GENERATOR_OUTPUT:\n")
            fh.write(f"LATENT: {best_candidate.latent}\n")
            fh.write(f"ARGUMENT: {best_candidate.argument}\n")
            fh.write(f"INITIAL_CRITIC_SCORE: {best_critic.score}/4\n")
            fh.write(f"INITIAL_VERDICT: {best_critic.verdict}\n")
            fh.write(f"INITIAL_CRITIQUE: {best_critic.critique}\n")

    def _log_refinement_loop_start(self, loop_num: int, current_latent: str, current_critic) -> None:
        """Log the start of a refinement loop."""
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(f"\n{'-'*20} REFINEMENT LOOP {loop_num} {'-'*20}\n")
            fh.write(f"INPUT_LATENT: {current_latent}\n")
            fh.write(f"CRITIC_OUTPUT:\n")
            fh.write(f"  Score: {current_critic.score}/4\n")
            fh.write(f"  Verdict: {current_critic.verdict}\n")
            fh.write(f"  Critique: {current_critic.critique}\n")

    def _log_refinement_loop_result(self, loop_num: int, refined_latent: str, new_critic) -> None:
        """Log the result of a refinement loop."""
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(f"REFINER_OUTPUT: {refined_latent}\n")
            fh.write(f"NEW_CRITIC_EVALUATION:\n")
            fh.write(f"  Score: {new_critic.score}/4\n")
            fh.write(f"  Verdict: {new_critic.verdict}\n")
            fh.write(f"  Critique: {new_critic.critique}\n")

    def _log_problem_end(self, final_latent: str, final_critic, total_loops: int) -> None:
        """Log the final result of the problem."""
        with open(self.log_path, "a", encoding="utf-8") as fh:
            fh.write(f"\nFINAL_RESULT: {final_latent}\n")
            fh.write(f"FINAL_SCORE: {final_critic.score}/4\n")
            fh.write(f"TOTAL_REFINEMENT_LOOPS: {total_loops}\n")
            fh.write("="*50 + " PROBLEM END " + "="*52 + "\n\n")


def create_openai_client(api_key: str = None) -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)
