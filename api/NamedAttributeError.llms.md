# NamedAttributeError

``` python
NamedAttributeError(message)
```

Base exception for all attribute-related errors in databpy.

Raised when an operation on a named attribute fails, such as data that doesn’t match the size of the domain, a conflict with the type or domain of an existing attribute, or an attribute that can’t be created. Subclasses cover a missing attribute (`AttributeNotFoundError`) and values that don’t fit the attribute (`AttributeMismatchError`).

## Notes

This currently also subclasses `AttributeError`, which will be removed in databpy 0.14.0 as `hasattr()` and `getattr()` silently swallow `AttributeError`. Catch `NamedAttributeError` or `DatabpyError` instead.
