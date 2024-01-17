"""Module contains typedefs that are used with runnables."""
from __future__ import annotations

from typing import List, Dict, Any

from typing_extensions import TypedDict, NotRequired


class _EventData(TypedDict):
    """Data associated with a streaming event."""

    input: NotRequired[Any]
    """The input passed to the runnable that generated the event.
    
    Inputs will sometimes be available at the *START* of the runnable, and 
    sometimes at the *END* of the runnable.
    
    If a runnable is able to stream its inputs, then its input by definition
    won't be known until the *END* of the runnable when it has finished streaming
    its inputs.
    """
    output: NotRequired[Any]
    """The output of the runnable that generated the event.
    
    Outputs will only be available at the *END* of the runnable.
    
    This field is technically not required since it can be inferred from the
    `chunk` field, but it is included for convenience.
    """
    chunk: NotRequired[Any]
    """A streaming chunk from the output that generated the event.
    
    chunks support addition in general, and adding them up should result
    in the output of the runnable that generated the event.
    """


class StreamEvent(TypedDict):
    """A streaming event.

    Schema of a streaming event which is produced from the astream_events method.

    Example:

        .. code-block:: python

            from langchain_core.runnables import RunnableLambda

            async def reverse(s: str) -> str:
                return s[::-1]

            chain = RunnableLambda(func=reverse)

            events = [event async for event in chain.astream_events("hello")]

            # will produce the following events (run_id has been omitted for brevity):
            [
                {
                    "data": {"input": "hello"},
                    "event": "on_chain_start",
                    "metadata": {},
                    "name": "reverse",
                    "tags": [],
                },
                {
                    "data": {"chunk": "olleh"},
                    "event": "on_chain_stream",
                    "metadata": {},
                    "name": "reverse",
                    "tags": [],
                },
                {
                    "data": {"output": "olleh"},
                    "event": "on_chain_end",
                    "metadata": {},
                    "name": "reverse",
                    "tags": [],
                },
            ]
    """

    event: str
    """Event names are of the format: on_[runnable_type]_(start|stream|end).
    
    Runnable types are one of: 
    * llm - both chat and non chat models
    * prompt --  e.g., ChatPromptTemplate
    * tool -- from tools defined via @tool decorator or inherting from Tool/BaseTool
    * chain - most Runnables are of this type
    
    Further, the events are categorized as one of:
    * start - when the runnable starts
    * stream - when the runnable is streaming
    * end - when the runnable ends
    
    start, stream and end are associated with slightly different `data` payload.
    
    Please see the documentation for `_EventData` for more details.
    """
    name: str
    """The name of the runnable that generated the event."""
    run_id: str
    """An randomly generated ID to keep track of the execution of the given runnable.
    
    Each child runnable that gets invoked as part of the execution of a parent runnable
    is assigned its own unique ID.
    """
    tags: NotRequired[List[str]]
    """Tags associated with the runnable that generated this event.
    
    Tags are always inherited from parent runnables.
    
    Tags can either be bound to a runnable using `.with_config({"tags":  ["hello"]})`
    or passed at run time using `.astream_events(..., {"tags": ["hello"]})`.
    """
    metadata: NotRequired[Dict[str, Any]]
    """Metadata associated with the runnable that generated this event.
    
    Metadata can either be bound to a runnable using 
    
        `.with_config({"metadata": { "foo": "bar" }})`
        
    or passed at run time using 
    
        `.astream_events(..., {"metadata": {"foo": "bar"}})`.
    """
    data: _EventData
    """Event data.

    The contents of the event data depend on the event type.
    """
