from Model.Structs import *
from Interpret.Interpret import *


def printEx(count: int, expr_source: str, expr_model: Node):
    print(f'===Teste número {count} =================================')
    print(f'*expr_source:\n{expr_source}')
    print()
    print(f'*expr_model:')
    interpret_program(expr_model)
    print()


# Exemplo 1
expr_source1 = "2"
expr_model1 = Integer(2)
printEx(1, expr_source1, expr_model1)

# Exemplo 2
s2 = "print 3 + 4 * -5;"
m2 = Print(
        BinOp('+',
            Integer(3),
            BinOp('*',
                Integer(4),
                UnOp('-', Integer(5))
            )
        )
    )
printEx(2, s2, m2)

# Exemplo 3
s3 = "print 'x';\nprint '\\n';"
m3 = BlockStatement([
    Print( Char('x') ),
    Print( Char('\n') )
])
printEx(3, s3, m3)

# Exemplo 4
s4 = "const pi = 3.14159;\nconst tau = 2.0 * pi;"
m4 = BlockStatement([
    Declaration(
        'const',
        Location('pi'),
        value= Float(3.14159)
    ),
    Declaration(
        'const',
        Location('tau'),
        value= BinOp(
            '*',
            Float(2.0),
            Location('pi')
        )
    ),
    Print(Location('tau'))
])
printEx(4, s4, m4)

# Exemplo 5
s5 = '''
    var a int = 2;
    var b int = 3;
    if a < b {
        print a;
    } else {
        print b;
    }
'''
m5 = BlockStatement([
    Declaration('var', Location('a'), int, Integer(2)),
    Declaration('var', Location('b'), int, Integer(3)),
    IfStatement(
        BinOp('<', Location('a'), Location('b')),
        BlockStatement([
            Print(Location('a'))
        ]),
        BlockStatement([
            Print(Location('b'))
        ])
    )
])
printEx(5, s5, m5)

# Exemplo 6
s6 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''
m6 = BlockStatement([
    Declaration('const', Location('n'), value=Integer(10)),
    Declaration('var', Location('x'), int, Integer(1)),
    Declaration('var', Location('fact'), int, Integer(1)),
    WhileStatement(
        BinOp('<', Location('x'), Location('n')),
        BlockStatement([
            Assignment(
                Location('fact'),
                BinOp('*', Location('fact'), Location('x'))
            ),
            Print(Location('fact')),
            Print(Char('\n')),
            Assignment(
                Location('x'),
                BinOp('+', Location('x'), Integer(1))
            )
        ])
    )
])
printEx(6, s6, m6)

s7 = '''
    var x = 37;
    var y = 42;
    x = { var t = y; y = x; t; };     // Compound expression.
    print x;
    print y;
'''
m7 = BlockStatement([
    Declaration('var', Location('x'), value=Integer(37)),
    Declaration('var', Location('y'), value=Integer(42)),
    Assignment(
        Location('x'),
        CompoundExpression([
            Declaration('var', Location('t'), value=Location('y')),
            Assignment(Location('y'), Location('x')),
            Location('t')
        ])
    ),
    Print(Location('x')),
    Print(Location('y'))
])
printEx(7, s7, m7)