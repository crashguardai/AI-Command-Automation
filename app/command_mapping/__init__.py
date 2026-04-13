"""Map NLU intents + entities to concrete shell commands."""

from app.command_mapping.mapper import CommandMappingResult, map_command

__all__ = ["map_command", "CommandMappingResult"]
