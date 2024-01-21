"""
A DSL for filtering trace logs.

Tokens:
- Ident: Identifer, i.e. some property of the trace message, e.g timestamp, module etc.
- keywords: in, eq, and, or, not
- parens: ( and )
- Literals: Numbers, string and lists
"""

from lark import Lark, Transformer
from lark.exceptions import VisitError
from lark.tree import Tree


class UnknownIdent(Exception):
    def __init__(self, ident) -> None:
        # Call the base class constructor with the parameters it needs
        super().__init__(f"Unknown ident {ident}")
        self.ident = ident

class FilterDSLEvaluator(Transformer):
    def __init__(self, data: dict):
        self.data = data

    def start(self, exprs: list[Tree]) -> bool:
        return bool(exprs[0])

    def name(self, exprs: list[Tree]) -> str | int:
        if exprs[0] not in self.data:
            raise UnknownIdent(str(exprs[0]))
        return self.data[exprs[0]]

    def eq(self, exprs: list[Tree]) -> bool:
        (a,b) = exprs
        return a == b

    def contains(self, exprs: list[Tree]) -> bool:
        (a,b) = exprs
        return b in a

    def is_in(self, exprs: list[Tree]) -> bool:
        (a,b) = exprs
        return a in b

    def contains(self, exprs: list[Tree]) -> bool:
        (a,b) = exprs
        return b in a

    def invert(self, exprs: list[Tree]) -> bool:
        return not exprs[0]

    def combine_and(self, exprs: list[Tree]) -> bool:
        return exprs[0] and exprs[1]

    def combine_or(self, exprs: list[Tree]) -> bool:
        return exprs[0] or exprs[1]

    def STRING(self, s):
        return s[1:-1]

    SIGNED_NUMBER = int
    list = list

grammar = """
start: combine+

?combine: expr
    | combine "and" expr -> combine_and
    | combine  "or" expr -> combine_or


?expr: comparison
    | invert
    | "(" combine ")"

invert: "not" expr

comparison: name "eq" literal -> eq
    | name "contains" STRING -> contains
    | name "in" list -> is_in


?literal: STRING
       | SIGNED_NUMBER

list : "[" [STRING ("," STRING)*] "]"
     | "[" [SIGNED_NUMBER ("," SIGNED_NUMBER)*] "]"

STRING:  ESCAPED_STRING
name: CNAME

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.CNAME
%import common.WS
%ignore WS
"""
parser = Lark(grammar, parser='lalr')

class FilterDSL:
    def __init__(self, expr: str) -> None:
        self.tree = parser.parse(expr)

    def eval(self, data) -> bool:
        try:
            return FilterDSLEvaluator(data).transform(self.tree)
        except VisitError as e:
            raise e.orig_exc from e

if __name__ == "__main__":
    test = FilterDSL("module eq 1")
    print(test.tree)
