# AttributeMismatchError

``` python
AttributeMismatchError(message)
```

Exception raised when data doesn’t fit an attribute.

Raised when the number of values written with `Attribute.from_array` doesn’t match the attribute, or when values can’t be represented by the attribute’s type (complex numbers, or integers outside the range of the storage type).
