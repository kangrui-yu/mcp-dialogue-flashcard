import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStage(Enum):
    """Stages of dialogue summarization process."""
    INITIALIZING = "initializing"
    GENERATION = "generation"
    CRITICISM = "criticism"
    REFINEMENT_LOOP_1 = "refinement_loop_1"
    REFINEMENT_LOOP_2 = "refinement_loop_2"
    REFINEMENT_LOOP_3 = "refinement_loop_3"
    FLASHCARD_GENERATION = "flashcard_generation"
    SAVING_RESULTS = "saving_results"
    COMPLETED = "completed"


@dataclass
class TaskProgress:
    """Progress information for a summarization task."""
    stage: TaskStage = TaskStage.INITIALIZING
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class SummarizationTask:
    """Represents a dialogue summarization task."""
    task_id: str
    dialogue: List[Dict]
    user_id: int = 0
    dialogue_csv_path: str = "../../data/dialogues.csv"
    flashcards_csv_path: str = "../../data/flashcards.csv"
    status: TaskStatus = TaskStatus.PENDING
    progress: List[TaskProgress] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def add_progress(self, stage: TaskStage, message: str = ""):
        """Add a progress update to the task."""
        progress = TaskProgress(stage=stage, message=message)
        self.progress.append(progress)

    def get_current_stage(self) -> TaskStage:
        """Get the current stage of the task."""
        if not self.progress:
            return TaskStage.INITIALIZING
        return self.progress[-1].stage

    def get_stage_progress_count(self) -> int:
        """Get the number of completed stages."""
        return len(self.progress)


class TaskManager:
    """
    Manages asynchronous dialogue summarization tasks.

    Provides task creation, progress tracking, and background execution
    using ThreadPoolExecutor for concurrent processing.
    """

    def __init__(self, max_workers: int = 2, task_retention_seconds: int = 3600):
        """
        Initialize the task manager.

        Args:
            max_workers: Maximum number of concurrent summarization tasks
            task_retention_seconds: How long to keep completed tasks in memory
        """
        self._tasks: Dict[str, SummarizationTask] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_retention_seconds = task_retention_seconds

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_old_tasks, daemon=True)
        self._cleanup_thread.start()

    def create_task(
        self,
        dialogue: List[Dict],
        user_id: int = 0,
        dialogue_csv_path: str = "../../data/dialogues.csv",
        flashcards_csv_path: str = "../../data/flashcards.csv"
    ) -> str:
        """
        Create a new summarization task and start execution.

        Args:
            dialogue: List of dialogue turns with role and message
            user_id: User identifier
            dialogue_csv_path: Path to dialogue CSV file
            flashcards_csv_path: Path to flashcards CSV file

        Returns:
            task_id: Unique identifier for the created task
        """
        task_id = str(uuid.uuid4())

        task = SummarizationTask(
            task_id=task_id,
            dialogue=dialogue,
            user_id=user_id,
            dialogue_csv_path=dialogue_csv_path,
            flashcards_csv_path=flashcards_csv_path
        )

        with self._lock:
            self._tasks[task_id] = task

        # Submit task for background execution
        self._executor.submit(self._execute_task, task_id)

        return task_id

    def get_task(self, task_id: str) -> Optional[SummarizationTask]:
        """Get a task by ID."""
        with self._lock:
            return self._tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get the current status and progress of a task.

        Returns:
            Dictionary with task status, progress, and results
        """
        task = self.get_task(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "current_stage": task.get_current_stage().value,
            "progress_count": task.get_stage_progress_count(),
            "total_stages": len(TaskStage),
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "progress": [
                {
                    "stage": p.stage.value,
                    "message": p.message,
                    "timestamp": p.timestamp
                }
                for p in task.progress
            ]
        }

    def wait_for_completion(self, task_id: str, timeout: float = 300) -> Optional[Dict]:
        """
        Wait for a task to complete or timeout.

        Args:
            task_id: Task identifier
            timeout: Maximum wait time in seconds

        Returns:
            Final task status or None if task not found
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            task = self.get_task(task_id)
            if not task:
                return None

            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return self.get_task_status(task_id)

            time.sleep(0.5)  # Poll every 500ms

        # Timeout reached
        return self.get_task_status(task_id)

    def _execute_task(self, task_id: str):
        """Execute a summarization task in the background."""
        task = self.get_task(task_id)
        if not task:
            return

        try:
            with self._lock:
                task.status = TaskStatus.RUNNING
                task.started_at = time.time()
                task.add_progress(TaskStage.INITIALIZING,
                                  "Starting summarization process")

            # Import the summarization function here to avoid circular imports
            from .cli import summarize_dialogue_async

            # Create progress callback
            def progress_callback(stage: TaskStage, message: str = ""):
                with self._lock:
                    task.add_progress(stage, message)

            # Execute the actual summarization
            result = summarize_dialogue_async(
                task.dialogue,
                task.user_id,
                task.dialogue_csv_path,
                task.flashcards_csv_path,
                progress_callback
            )

            with self._lock:
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.time()
                task.add_progress(TaskStage.COMPLETED,
                                  f"Summary completed: {result}")

        except Exception as e:
            with self._lock:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = time.time()

    def _cleanup_old_tasks(self):
        """Background thread to clean up old completed tasks."""
        while True:
            try:
                current_time = time.time()
                cutoff_time = current_time - self.task_retention_seconds

                with self._lock:
                    task_ids_to_remove = [
                        task_id for task_id, task in self._tasks.items()
                        if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                            and task.completed_at is not None
                            and task.completed_at < cutoff_time)
                    ]

                    for task_id in task_ids_to_remove:
                        del self._tasks[task_id]

                time.sleep(300)  # Clean up every 5 minutes

            except Exception:
                # Ignore cleanup errors and continue
                time.sleep(300)

    def shutdown(self):
        """Shutdown the task manager and cleanup resources."""
        self._executor.shutdown(wait=True)


# Global task manager instance
task_manager = TaskManager()
