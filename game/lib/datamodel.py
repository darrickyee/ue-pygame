# %%
import json
from functools import singledispatch
from typing import Any, Union

TYPES_SIMPLE = (bool, float, int, str)
TYPES_COMPLEX = (list, dict)
# %%


class ListModel(list):

    _types = (int, bool)

    def __add__(self, value):
        if all(isinstance(x, self._types) for x in value):
            return super().__add__(value)

        raise TypeError('Wrong type')


class MapModel(dict):

    _types = (str, float)

    def __init__(self, *args, **kwargs) -> None:
        d = dict(*args, **kwargs)
        if all(isinstance(k, str) for k in d) and all(isinstance(v, self._types) for v in d.values()):
            super().__init__(*args, **kwargs)
        else:
            raise TypeError(
                f"{self.__class__.__name__} type must take values of type {self._types}.")

    def __setitem__(self, key: str, value: Any) -> None:
        if isinstance(key, str) and isinstance(value, self._types):
            return super().__setitem__(key, value)

        raise TypeError(f'Cannot assign')
# %%


@singledispatch
def _validate(typespec, obj):
    raise NotImplementedError(f"Invalid typespec: {typespec}")


@_validate.register
def _validate_type(typespec: type, obj: Any):
    if isinstance(obj, typespec):
        return obj


def _is_typeobj(obj):

    if isinstance(obj, tuple):
        return all(_is_typeobj(el) for el in obj)

    if isinstance(obj, type):
        return issubclass(obj, TYPES_SIMPLE + TYPES_COMPLEX)

    return False


def _is_validtype(obj):
    return _is_typeobj(type(obj))


# %%


def _get_default(obj):
    if isinstance(obj, TYPES_SIMPLE):
        return obj

    if isinstance(obj, TYPES_COMPLEX):
        return json.loads(json.dumps(obj))

    if obj in TYPES_SIMPLE + TYPES_COMPLEX:
        return obj()

# %%


def _get_typeobj(obj):
    if _is_typeobj(obj):
        return obj

    if _is_typeobj(t := type(obj)):
        return t

    raise TypeError(f"Object '{obj}' has an invalid type")


class Model(dict):

    def __init__(self, properties) -> None:
        self._props = properties


class MyDict(dict):

    def __init__(self, **kwargs) -> None:
        self._types = {k: _get_typeobj(v) for k, v in kwargs.items()}

        members = {}
        for k, v in kwargs.items():
            members.update({k: v if not _is_typeobj(v) else None})
        super().__init__(**members)

    def __setitem__(self, k, v) -> None:
        if not isinstance(v, tp := self._types[k]):
            typestr = f"({', '.join(t.__name__ for t in tp)})" if isinstance(
                tp, tuple) else tp.__name__
            raise TypeError(
                f"Cannot set value for '{k}': Object of type '{type(v).__name__}' cannot be assigned to value of type '{typestr}'")

        super().__setitem__(k, v)


def get_typestr(typespec: Union[type, tuple[type]]) -> str:
    return f"({', '.join(t.__name__ for t in typespec)})" if isinstance(typespec, tuple) else typespec.__name__


def _check_type(value: Any, typespec: Union[type, tuple[type]]) -> None:
    if not isinstance(value, typespec):
        raise TypeError(
            f"Object of type '{type(value).__name__}' cannot be assigned to value of type '{get_typestr(typespec)}'")


class ModelType(dict):

    def __setitem__(self, k, v) -> None:
        if k in self.__annotations__:

            # %%
