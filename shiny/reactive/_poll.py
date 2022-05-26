import os
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union
import shiny

from shiny.types import MISSING, MISSING_TYPE
from shiny import reactive

if TYPE_CHECKING:
    from ..session import Session

__all__ = ["poll", "file_reader"]

T = TypeVar("T")


def poll(
    poll_func: Callable[[], Any],
    interval_secs: float = 1,
    *,
    compare: Optional[Callable[[Any, Any], bool]] = None,
    session: Union[MISSING_TYPE, "Session", None] = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]:

    if compare is None:
        compare = shiny.equal

    with reactive.isolate():
        last_value: reactive.Value[Any] = reactive.Value(poll_func())

    @reactive.Effect(session=session)
    def _():
        try:
            new = poll_func()
            with reactive.isolate():
                old = last_value.get()
            if not compare(old, new):
                last_value.set(new)
        finally:
            reactive.invalidate_later(interval_secs)

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        @reactive.Calc(session=session)
        def result() -> T:
            # Take dependency on polling result
            last_value.get()

            # Note that we also depend on the main function
            return fn()

        return result

    return wrapper


def file_reader(
    filepath: Union[str, Callable[[], str]],
    interval_secs: float = 1,
    *,
    session: Union[MISSING_TYPE, "Session", None] = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    if isinstance(filepath, str):
        # Normalize filepath so it's always a function

        filepath_value = filepath

        def filepath_func() -> str:
            return filepath_value

        filepath = filepath_func

    def check_timestamp():
        return os.path.getmtime(filepath())

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        @poll(check_timestamp)
        def reader():
            return fn()

        return reader

    return wrapper
