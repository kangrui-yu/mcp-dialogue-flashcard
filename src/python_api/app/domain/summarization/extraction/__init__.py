"""
Multi-Agent Latent Extraction Package

This package provides a clean, modular implementation of the multi-agent latent concept
extraction workflow with generator-critic-refiner architecture.
"""

from .workflow import MultiAgentLatentExtractor
from .schemas import GeneratorOutput, CriticOutput, RefinerOutput, AgentContext

__all__ = [
    'MultiAgentLatentExtractor',
    'GeneratorOutput',
    'CriticOutput',
    'RefinerOutput',
    'AgentContext'
]
