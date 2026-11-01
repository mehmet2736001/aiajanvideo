# -*- coding: utf-8 -*-
"""
Multi-Agent Video Production System - Base Agent Class
Provides the strict gatekeeper check ensuring no agent can execute
before its prerequisite agent has completed its task successfully.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Callable
import time
from .state import ProjectState, PipelinePhase, AgentStatus, AgentStepLog


class StateTransitionError(Exception):
    """Raised when an agent tries to execute without its prerequisite phase being satisfied."""
    pass


class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: int,
        name: str,
        required_phase: PipelinePhase,
        target_phase: PipelinePhase
    ):
        self.agent_id = agent_id
        self.name = name
        self.required_phase = required_phase
        self.target_phase = target_phase

    def can_execute(self, state: ProjectState) -> Tuple[bool, str]:
        """
        GATED SECURITY CHECK:
        Enforces that this agent CANNOT run unless the prior agent has completed its work
        and reached the required pipeline phase.
        """
        if state.current_phase != self.required_phase:
            return (
                False,
                f"Kural İhlali: [{self.agent_id}. {self.name}] çalıştırılamaz! "
                f"Gerekli Aşama: '{self.required_phase.value}', Mevcut Aşama: '{state.current_phase.value}'. "
                f"Önceki ajan görevini bitirmeden sonraki ajana geçilemez!"
            )
        return True, "Geçerli"

    def run(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        """
        Executes the agent lifecycle with strict input gate validation,
        execution monitoring, and atomic phase progression.
        """
        can_run, reason = self.can_execute(state)
        if not can_run:
            print(f"[Multi-Agent Gatekeeper] {reason}")
            raise StateTransitionError(reason)

        started_at = time.strftime("%Y-%m-%d %H:%M:%S")
        t0 = time.time()

        # Update log to RUNNING
        state.agent_logs[self.agent_id] = AgentStepLog(
            agent_id=self.agent_id,
            agent_name=self.name,
            status=AgentStatus.RUNNING,
            started_at=started_at
        )

        if on_progress:
            on_progress(self.agent_id, "running", {"message": f"{self.name} göreve başladı..."})

        try:
            # Subclass actual logic
            state = self._process(state, on_progress)

            # Validate that output contract was satisfied
            self._validate_contract(state)

            # Advance state machine phase
            state.current_phase = self.target_phase
            duration_sec = round(time.time() - t0, 2)
            finished_at = time.strftime("%Y-%m-%d %H:%M:%S")

            state.agent_logs[self.agent_id].status = AgentStatus.SUCCESS
            state.agent_logs[self.agent_id].finished_at = finished_at
            state.agent_logs[self.agent_id].duration_sec = duration_sec

            if on_progress:
                on_progress(self.agent_id, "success", {
                    "message": f"{self.name} görevini başarıyla tamamladı ({duration_sec}s).",
                    "next_phase": self.target_phase.value
                })

            return state

        except Exception as e:
            duration_sec = round(time.time() - t0, 2)
            finished_at = time.strftime("%Y-%m-%d %H:%M:%S")

            state.agent_logs[self.agent_id].status = AgentStatus.FAILED
            state.agent_logs[self.agent_id].finished_at = finished_at
            state.agent_logs[self.agent_id].duration_sec = duration_sec
            state.agent_logs[self.agent_id].error = str(e)
            state.errors.append(f"[{self.name}] {str(e)}")

            if on_progress:
                on_progress(self.agent_id, "failed", {
                    "message": f"{self.name} hata verdi: {str(e)}",
                    "error": str(e)
                })

            raise

    @abstractmethod
    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        """Subclass implementation of the agent's core task."""
        pass

    @abstractmethod
    def _validate_contract(self, state: ProjectState) -> None:
        """Subclass validation verifying its output is populated properly."""
        pass
