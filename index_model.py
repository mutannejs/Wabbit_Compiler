from src.model import *
from src.to_source import to_source


def printEx(count: int, expr_source: str, expr_model: Node):
    print(f'===Teste número {count} =================================')
    print(f'*expr_source:{expr_source}')
    print(f'*expr_model:\n{expr_model}\n')
    print(f'*to_source:\n{to_source(expr_model)}')
    print()


# Exemplos 0
s0 = '''
if a != 5 && b >= c {
    var u unit = ();
    var v = { print u; };
}
'''
m0 = IfStatement(
    BinOp(
        '&&',
        BinOp('!=', Location('a'), Integer(5)),
        BinOp('>=', Location('b'), Location('c'))
    ),
    BlockStatement([
        DeclarationVar(Location('u'), Unit(), 'unit'),
        DeclarationVar(
            Location('v'),
            CompoundExpression([ Print(Location('u')) ])
        )
    ], 1)
)
printEx(0, s0, m0)

# Exemplo 1
expr_source1 = '''
2
'''
expr_model1 = Integer(2)
printEx(1, expr_source1, expr_model1)

# Exemplo 2
s2 = '''
print 3 + 4 * -5;
'''
m2 = Print(
        BinOp('*',
            BinOp('+', Integer(3), Integer(4)),
            UnOp('-', Integer(5))
        )
    )
printEx(2, s2, m2)

# Exemplo 3
s3 = '''
print 3.4 - 5.6 / -7.8;
'''
m3 = Print(
    BinOp(
        '-',
        Float(3.4),
        BinOp(
            '/',
            Float(5.6),
            UnOp('-', Float(7.8))
        )
    )
)
printEx(3, s3, m3)

# Exemplo 4 e 5
s4 = '''
print 'x';
print '\n';
'''
m4 = BlockStatement([
    Print( Char('x') ),
    Print( Char('\n') )]
)
printEx(4, s4, m4)

# Exemplo 5
s5 = '''
const pi = 3.14159;
const tau = 2.0 * pi;
'''
m5 = BlockStatement([
    DeclarationConst(Location('pi'), Float(3.14159)),
    DeclarationConst(
        Location('tau'),
        BinOp('*', Float(2.0), Location('pi'))
    )
])
printEx(5, s5, m5)

# Exemplo 6
s6 = '''
var r float;
'''
m6 = DeclarationVar(
    Location('r'),
    dtype='float'
)
printEx(6, s6, m6)

# Exemplo 7
s7 = '''
r = 2.0;
a = pi*r*r;
'''
m7 = BlockStatement([
    Assignment(Location('r'), Float(2.0)),
    Assignment(
        Location('a'),
        BinOp(
            '*',
            BinOp('*', Location('pi'), Location('r')),
            Location('r')
        )
    )
])
printEx(7, s7, m7)

# Exemplo 8
s8 = '''
var c bool = true;
c = a < 100.0;
var d = (a > 0.0) && (a < 10.0);
print d;
'''
m8 = BlockStatement([
    DeclarationVar(Location('c'), Bool(True), 'bool'),
    Assignment(
        Location('c'),
        BinOp('<', Location('a'), Float(100.0))
    ),
    DeclarationVar(
        Location('d'),
        BinOp(
            '&&',
            BinOp('>', Location('a'), Float(0.0)),
            BinOp('<', Location('a'), Float(10.0))
        )
    ),
    Print( Location('d') )
])
printEx(8, s8, m8)

# Exemplo 9
s9 = '''
if a > 0.0 {
    print a;
} else {
    print -a;
}
'''
m9 = IfStatement(
    BinOp('>', Location('a'), Float(0.0)),
    BlockStatement([
        Print(Location('a'))
    ], 1),
    BlockStatement([
        Print(UnOp('-', Location('a')))
    ], 1)
)
printEx(9, s9, m9)

# Exemplo 10
s10 = '''
const n = 10;
var x int = 1;
var fact int = 1;
while x < n {
    fact = fact * x;
    print fact;
    x = x + 1;
}
'''
m10 = BlockStatement([
    DeclarationConst(Location('n'), Integer(10)),
    DeclarationVar(Location('x'), Integer(1), 'int'),
    DeclarationVar(Location('fact'), Integer(1), 'int'),
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
printEx(10, s10, m10)

# Exemplo 11
s11 = '''
var x = 37;
var y = 42;
x = { var t = y; y = x; t; };
print x;
print y;
'''
m11 = BlockStatement([
    DeclarationVar(Location('x'), Integer(37)),
    DeclarationVar(Location('y'), Integer(42)),
    Assignment(
        Location('x'),
        CompoundExpression([
            DeclarationVar( Location('t'), Location('y')),
            Assignment(Location('y'), Location('x')),
            Location('t')
        ])
    ),
    Print(Location('x')),
    Print(Location('y'))
])
printEx(11, s11, m11)

# Exemplo 12
s12 ='''
func add(x int, y int) int {
    return x + y;
}

func mul(x int, y int) int {
    return x * y;
}

func factorial(n int) int {
    if n == 0 {
        return 1;
    } else {
        return mul(n, factorial(add(n, -1)));
    }
}

func print_factorials(last int) {
    var x = 0;
    while x < last {
        print factorial(x);
        x = add(x, 1);
    }
}

func main() int {
    var result = print_factorials(10);
    return 0;
}
'''
m12 = Program([
    FunctionDefinition(
        'add',
        BlockStatement([
            ReturnStatement(
                BinOp('+', Location('x'), Location('y'))
            )
        ], 1),
        [ Argument('int', 'x'), Argument('int', 'y') ],
        'int'
    ),
    FunctionDefinition(
        'mul',
        BlockStatement([
            ReturnStatement(
                BinOp('*', Location('x'), Location('y'))
            )
        ], 1),
        [ Argument('int', 'x'), Argument('int', 'y') ],
        'int'
    ),
    FunctionDefinition(
        'factorial',
        BlockStatement([
            IfStatement(
                BinOp('==', Location('n'), Integer(0)),
                BlockStatement([
                    ReturnStatement(Integer(1))
                ], 2),
                BlockStatement([
                    ReturnStatement(
                        FunctionApplication(
                            'mul', [
                                Location('n'),
                                FunctionApplication(
                                    'factorial', [
                                        FunctionApplication(
                                            'add', [
                                                Location('n'),
                                                UnOp('-', Integer(1))
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ], 2),
                1
            )
        ], 1),
        [ Argument('int', 'n') ],
        'int'
    ),
    FunctionDefinition(
        'print_factorials',
        BlockStatement([
            DeclarationVar(Location('x'), Integer(0)),
            WhileStatement(
                BinOp('<', Location('x'), Location('last')),
                BlockStatement([
                    Print(
                        FunctionApplication(
                            'factorial', [
                                Location('x')
                            ]
                        )
                    ),
                    Assignment(
                        Location('x'),
                        FunctionApplication(
                            'add', [
                                Location('x'),
                                Integer(1)
                            ]
                        )
                    )
                ], 2),
                1
            )
        ], 1),
        [ Argument('int', 'last') ]
    ),
    FunctionDefinition(
        'main',
        BlockStatement([
            DeclarationVar(
                Location('result'),
                FunctionApplication(
                    'print_factorials', [
                        Integer(10)
                    ]
                ),
            ),
            ReturnStatement(Integer(0))
        ], 1),
        typeReturn = 'int'
    )
])
printEx(12, s12, m12)

# Exemplo 13
s13 = '''
const n = 10;
var x int = 0;

while x < n {
    print x;
    if x == 1 {
        x = x + 2;
        continue;
    }
    if x == 7 {
        break;
    }
    x = x + 1;
}
'''
m13 = BlockStatement([
    DeclarationConst(Location('n'), Integer(10)),
    DeclarationVar(Location('x'), Integer(0), 'int'),
    WhileStatement(
        BinOp('<', Location('x'), Location('n')),
        BlockStatement([
            Print(Location('x')),
            IfStatement(
                BinOp('==', Location('x'), Integer(1)),
                BlockStatement([
                    Assignment(
                        Location('x'),
                        BinOp('+', Location('x'), Integer(2))
                    ),
                    Continue()
                ], 2),
                tabs = 1
            ),
            IfStatement(
                BinOp('==', Location('x'), Integer(7)),
                BlockStatement([ Break() ], 2),
                tabs = 1
            ),
            Assignment(
                Location('x'),
                BinOp('+', Location('x'), Integer(1))
            )
        ], 1)
    )
])
printEx(13, s13, m13)