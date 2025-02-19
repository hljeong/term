import inspect


class Lambda:
    def __init__(self, func, vars=None, defaults=None):
        assert callable(func)
        self.func = func

        if vars is None:
            signature = inspect.signature(func)
            assert not any(
                param.kind
                in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]
                for param in signature.parameters.values()
            )
            self.vars = list(signature.parameters.keys())
            self.defaults = {
                var: param.default
                for var, param in signature.parameters.items()
                if param.default is not inspect.Parameter.empty
            }

        else:
            self.vars = vars
            self.defaults = defaults

    def __call__(self, *args, **kwargs):
        assert not any(var in self.vars[: len(args)] for var in kwargs)

        vars = dict(self.defaults)
        vars.update({var: value for var, value in zip(self.vars[: len(args)], args)})
        vars.update(kwargs)
        vars = {var: value for var, value in vars.items() if var in self.vars}

        if len(vars) == len(self.vars):
            return self.func(**vars)

        else:
            raise NotImplementedError("currying not implemented")
            # return Lambda(partial(self.func, **vars))

    @staticmethod
    def regularize(func):
        assert callable(func)
        if isinstance(func, Lambda):
            return func
        else:
            return Lambda(func)

    def _merge_vars_defaults(self, other):
        other = Lambda.regularize(other)
        assert all(
            self.defaults[var] == other.defaults[var]
            for var in self.defaults
            if var in other.defaults
        )
        vars = self.vars + list(var for var in other.vars if var not in self.vars)
        defaults = dict(self.defaults, **other.defaults)
        return vars, defaults

    def __add__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) + other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) + other, self.vars, self.defaults
            )

    def __sub__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) - other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) - other, self.vars, self.defaults
            )

    def __mul__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) * other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) * other, self.vars, self.defaults
            )

    def __truediv__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) / other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) / other, self.vars, self.defaults
            )

    def __floordiv__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) // other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) // other, self.vars, self.defaults
            )

    def __mod__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) % other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) % other, self.vars, self.defaults
            )

    def __pow__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) ** other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) ** other, self.vars, self.defaults
            )

    def __matmul__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) @ other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) @ other, self.vars, self.defaults
            )

    def __and__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) & other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) & other, self.vars, self.defaults
            )

    def __or__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) | other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) | other, self.vars, self.defaults
            )

    def __xor__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) ^ other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) ^ other, self.vars, self.defaults
            )

    def __lshift__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) << other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) << other, self.vars, self.defaults
            )

    def __rshift__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) >> other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) >> other, self.vars, self.defaults
            )

    def __eq__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) == other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) == other, self.vars, self.defaults
            )

    def __ne__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) != other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) != other, self.vars, self.defaults
            )

    def __lt__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) < other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) < other, self.vars, self.defaults
            )

    def __le__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) <= other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) <= other, self.vars, self.defaults
            )

    def __gt__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) > other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) > other, self.vars, self.defaults
            )

    def __ge__(self, other):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: self(**kwargs) >= other(**kwargs), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: self(**kwargs) >= other, self.vars, self.defaults
            )

    def __pos__(self):
        return Lambda(lambda **kwargs: +self(**kwargs), self.vars, self.defaults)

    def __neg__(self):
        return Lambda(lambda **kwargs: -self(**kwargs), self.vars, self.defaults)

    def __invert__(self):
        return Lambda(lambda **kwargs: ~self(**kwargs), self.vars, self.defaults)

    def __abs__(self):
        return Lambda(lambda **kwargs: abs(self(**kwargs)), self.vars, self.defaults)


Lx = Lambda(lambda x: x)
Ly = Lambda(lambda y: y)
Lz = Lambda(lambda z: z)
