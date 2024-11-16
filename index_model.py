# from Model.Structs import *
# from Model.ToSource import *
from Entregar.model import *


def printEx(count: int, expr_source: str, expr_model: Node):
    print(f'===Teste número {count} =================================')
    print(f'*expr_source:{expr_source}')
    print(f'*expr_model:\n{expr_model}\n')
    print(f'*to_source:\n{to_source(expr_model)}')
    print()


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
    DeclarationConst(Location('pi'), value= Float(3.14159)),
    DeclarationConst(
        Location('tau'),
        value=BinOp('*', Float(2.0), Location('pi'))
    )
])
printEx(5, s5, m5)

# Exemplo 6
s6 = '''
var r float;
'''
m6 = DeclarationVar(
    Location('r'),
    'float'
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
    DeclarationVar(Location('c'), 'bool', Bool(True)),
    Assignment(
        Location('c'),
        BinOp('<', Location('a'), Float(100.0))
    ),
    DeclarationVar(
        Location('d'),
        value= BinOp(
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
    DeclarationConst(Location('n'), value=Integer(10)),
    DeclarationVar(Location('x'), 'int', Integer(1)),
    DeclarationVar(Location('fact'), 'int', Integer(1)),
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
    DeclarationVar(Location('x'), value=Integer(37)),
    DeclarationVar(Location('y'), value=Integer(42)),
    Assignment(
        Location('x'),
        CompoundExpression([
            DeclarationVar( Location('t'), value=Location('y')),
            Assignment(Location('y'), value=Location('x')),
            Location('t')
        ])
    ),
    Print(Location('x')),
    Print(Location('y'))
])
printEx(11, s11, m11)