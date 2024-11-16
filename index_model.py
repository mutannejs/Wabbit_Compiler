from Model.Structs import *
from Model.ToSource import *


def printEx(count: int, expr_source: str, expr_model: Node):
    print(f'===Teste número {count} =================================')
    print(f'expr_source: {expr_source}')
    print(f'expr_model : {expr_model}')
    print(f'to_source  : {to_source(expr_model)}')
    print()


# Exemplo 1
expr_source1 = "2"
expr_model1 = Integer(2)
printEx(1, expr_source1, expr_model1)

# Exemplo 2
s2 = "print 3 + 4 * -5;"
m2 = Print(
        BinOp('*',
            BinOp('+',
                Integer(3),
                Integer(4)
            ),
            UnOp('-',
                Integer(5)
            )
        )
    )
printEx(2, s2, m2)

# Exemplo 3
s3 = "print 3.4 - 5.6 / -7.8;"
m3 = Print(
    BinOp(
        '-',
        Float(3.4),
        BinOp(
            '/',
            Float(5.6),
            UnOp(
                '-',
                Float(7.8)
            )
        )
    )
)
printEx(3, s3, m3)

# Exemplo 4 e 5
s4 = "print 'x';"
m4 = Print( Char('x') )
printEx(4, s4, m4)
s5 = "print '\n';"
m5 = Print( Char('\n') )
printEx(5, s5, m5)

# Exemplo 6 e 7
s6 = "const pi = 3.14159;"
m6 = Declaration(
    'const',
    Location('pi'),
    value= Float(3.14159)
)
printEx(6, s6, m6)
s7 = "const tau = 2.0 * pi;"
m7 = Declaration(
    'const',
    Location('tau'),
    value= BinOp(
        '*',
        Float(2.0),
        Location('pi')
    )
)
printEx(7, s7, m7)

# Exemplo 8
s8 = "var r float;"
m8 = Declaration(
    'var',
    Location('r'),
    'float'
)
printEx(8, s8, m8)

# Exemplo 9
s9 = "r = 2.0;\na = pi*r*r;"
m9 = BlockStatement([
    Assignment(
        Location('r'),
        Float(2.0)
    ),
    Assignment(
        Location('a'),
        BinOp(
            '*',
            BinOp(
                '*',
                Location('pi'),
                Location('r')
            ),
            Location('r')
        )
    )
])
printEx(9, s9, m9)

# Exemplo 10
s10 = 'var c bool = true;\nc = a < 100.0;\nvar d = (a > 0.0) && (a < 10.0);\nprint d;'
m10 = BlockStatement([
    Declaration(
        'var',
        Location('c'),
        'bool',
        Bool('true')
    ),
    Assignment(
        Location('c'),
        BinOp(
            '<',
            Location('a'),
            Float(100.0)
        )
    ),
    Declaration(
        'var',
        Location('d'),
        value= BinOp(
            '&&',
            BinOp(
                '>',
                Location('a'),
                Float(0.0)
            ),
            BinOp(
                '<',
                Location('a'),
                Float(10.0)
            )
        )
    ),
    Print( Location('d') )
])
printEx(10, s10, m10)

# Exemplo 11
s11 = 'if a > 0.0 {\n\tprint a;\n} else {\n\tprint -a;\n}'
m11 = IfStatement(
    BinOp('>', Location('a'), Float(0.0)),
    BlockStatement([
        Print(Location('a'))
    ], 1),
    BlockStatement([
        Print(UnOp('-', Location('a')))
    ], 1)
)
printEx(11, s11, m11)

# Exemplo 12
s12 = 'const n = 10;\nvar x int = 1;\nvar fact int = 1;\n\nwhile x < n {\n\tfact = fact * x;\n\tprint fact;\n\tx = x + 1;\n}'
m12 = BlockStatement([
    Declaration('const', Location('n'), value=Integer(10)),
    Declaration('var', Location('x'), 'int', Integer(1)),
    Declaration('var', Location('fact'), 'int', Integer(1)),
    WhileStatement(
        BinOp('<', Location('x'), Location('n')),
        BlockStatement([
            Assignment(
                Location('fact'),
                BinOp('*', Location('fact'), Location('x'))
            ),
            Print(Location('fact')),
            Assignment(
                Location('x'),
                BinOp('+', Location('x'), Integer(1))
            )
        ], 1)
    )
])
printEx(12, s12, m12)

# Exemplo 13
s13 = 'var x = 37;\nvar y = 42;\nx = { var t = y; y = x; t; };\nprint x;\nprint y;'
m13 = BlockStatement([
    Declaration('var', Location('x'), value=Integer(37)),
    Declaration('var', Location('y'), value=Integer(42)),
    Assignment(
        Location('x'),
        CompoundExpression([
            Declaration('var', Location('t'), value=Location('y')),
            Assignment(Location('y'), value=Location('x')),
            Location('t')
        ])
    ),
    Print(Location('x')),
    Print(Location('y'))
])
printEx(13, s13, m13)

# Exemplo 14
s14 = "print '\n'"
m14 = Print( Char('\n') )
printEx(14, s14, m14)