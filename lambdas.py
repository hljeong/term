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
            # todo: this doesnt work. also need to consider currying a Lambda
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

    def _unop(self, unop):
        return Lambda(lambda **kwargs: unop(self(**kwargs)), self.vars, self.defaults)

    def _binop(self, other, binop):
        if callable(other):
            vars, defaults = self._merge_vars_defaults(other)
            return Lambda(
                lambda **kwargs: binop(self(**kwargs), other(**kwargs)), vars, defaults
            )

        else:
            return Lambda(
                lambda **kwargs: binop(self(**kwargs), other), self.vars, self.defaults
            )

    def __pos__(self):
        return self._unop(lambda x: +x)

    def __neg__(self):
        return self._unop(lambda x: -x)

    def __invert__(self):
        return self._unop(lambda x: ~x)

    def __abs__(self):
        return self._unop(abs)

    def __add__(self, other):
        return self._binop(other, lambda x, y: x + y)

    def __sub__(self, other):
        return self._binop(other, lambda x, y: x - y)

    def __mul__(self, other):
        return self._binop(other, lambda x, y: x * y)

    def __truediv__(self, other):
        return self._binop(other, lambda x, y: x / y)

    def __floordiv__(self, other):
        return self._binop(other, lambda x, y: x // y)

    def __mod__(self, other):
        return self._binop(other, lambda x, y: x % y)

    def __pow__(self, other):
        return self._binop(other, lambda x, y: x**y)

    def __matmul__(self, other):
        return self._binop(other, lambda x, y: x @ y)

    def __and__(self, other):
        return self._binop(other, lambda x, y: x & y)

    def __or__(self, other):
        return self._binop(other, lambda x, y: x | y)

    def __xor__(self, other):
        return self._binop(other, lambda x, y: x ^ y)

    def __lshift__(self, other):
        return self._binop(other, lambda x, y: x << y)

    def __rshift__(self, other):
        return self._binop(other, lambda x, y: x >> y)

    def __eq__(self, other):
        return self._binop(other, lambda x, y: x == y)

    def __ne__(self, other):
        return self._binop(other, lambda x, y: x != y)

    def __lt__(self, other):
        return self._binop(other, lambda x, y: x < y)

    def __le__(self, other):
        return self._binop(other, lambda x, y: x <= y)

    def __gt__(self, other):
        return self._binop(other, lambda x, y: x > y)

    def __ge__(self, other):
        return self._binop(other, lambda x, y: x >= y)


L = Lambda
Lx = L(lambda x: x)
Ly = L(lambda y: y)
Lz = L(lambda z: z)
