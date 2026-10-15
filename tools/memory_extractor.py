"""
ULTRON Memory Extractor Loop
Monitors live session chat history and persists incremental new messages to ConversationMemory in the background.
"""

import time
import asyncio
import logging
from typing import Any, List, Dict, Optional

try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:
        pass

from friday_tools.memory_store import ConversationMemory

logger = logging.getLogger(__name__)


class MemoryExtractor:
    """
    Background memory monitor that automatically detects new incoming messages
    in an active session and saves them sequentially to persistent storage.
    """
    def __init__(self, user_id: str = "Shivansh"):
        self.user_id = user_id
        self.saved_message_count = 0

    def _serialize_for_hash(self, obj: Any) -> Any:
        """
        Recursively converts Pydantic objects or nested data into serializable dicts.
        """
        if isinstance(obj, BaseModel) and hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_hash(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_hash(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            return {k: self._serialize_for_hash(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
        else:
            return obj

    async def run(self, session: Any, poll_interval: float = 1.0):
        """
        The main loop that continuously checks for and saves new conversations.
        session: Either a list of messages, or an object containing a messages/chat_history attribute.
        """
        memory = ConversationMemory(self.user_id)
        logger.info(f"MemoryExtractor loop started for user {self.user_id}.")

        while True:
            await asyncio.sleep(poll_interval)

            # Resolve current chat history list
            if isinstance(session, list):
                current_chat_history = session
            elif hasattr(session, "chat_history"):
                current_chat_history = session.chat_history
            elif hasattr(session, "messages"):
                current_chat_history = session.messages
            elif callable(session):
                try:
                    current_chat_history = session()
                except Exception:
                    current_chat_history = []
            else:
                current_chat_history = []

            # Compare current count with saved count
            if len(current_chat_history) > self.saved_message_count:
                new_count = len(current_chat_history) - self.saved_message_count
                logger.info(f"{new_count} new message(s) detected. Saving...")

                # Slice of newly detected messages
                new_messages = current_chat_history[self.saved_message_count:]

                for message in new_messages:
                    serialized_message = self._serialize_for_hash(message)
                    conversation_wrapper = {
                        "messages": [serialized_message] if not isinstance(serialized_message, list) else serialized_message,
                        "timestamp": time.time()
                    }

                    success = memory.save_conversation(conversation_wrapper)
                    msg_id = getattr(message, "id", None) or (serialized_message.get("id") if isinstance(serialized_message, dict) else "auto_id")
                    if success:
                        logger.info(f"Saved new message: {msg_id}")
                    else:
                        logger.error(f"Failed to save message: {msg_id}")

                self.saved_message_count = len(current_chat_history)


async def start_memory_extractor_task(session: Any, user_id: str = "Shivansh") -> asyncio.Task:
    """Helper to launch MemoryExtractor as a background asyncio task."""
    extractor = MemoryExtractor(user_id=user_id)
    return asyncio.create_task(extractor.run(session))
