from google.adk.events import Event
from google.adk.memory.memory_entry import MemoryEntry

def event_to_memory_entry(event: Event) -> MemoryEntry:
    return MemoryEntry(
        author=event.author,
        content=event.content,
        created_at=event.timestamp
    )
