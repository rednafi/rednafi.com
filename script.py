def iscoroutinefunction(
    obj: object,
) -> TypeGuard[Callable[..., CoroutineType[Any, Any, Any]]]: ...
def isgenerator(obj: object) -> TypeIs[GeneratorType[Any, Any, Any]]: ...
def iscoroutine(obj: object) -> TypeIs[CoroutineType[Any, Any, Any]]: ...
def isawaitable(obj: object) -> TypeIs[Awaitable[Any]]: ...
