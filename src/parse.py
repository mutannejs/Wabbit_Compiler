import sys
sys.path.insert(0, 'sly.zip')
from sly import Parser

from .tokenize import WabbitLexer
from .model import *

class WabbitParser(Parser):
    tokens = WabbitLexer.tokens

    precedence = (
        ('left', LOR),
        ('left', LAND),
        ('left', LT, LE, GT, GE, EQ, NE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('left', UOP)
    )

    @_('{ statement }')
    def statements(self, p):
        return BlockStatement(p.statement)

    @_('{ statement }')
    def compound_expression(self, p):
        return CompoundExpression(p.statement)

    @_('print_statement',
       'assignment_statement',
       'variable_definition',
       'const_definition',
       'if_statement',
       'while_statement',
       'break_statement',
       'continue_statement',
       'expr SEMI',
       )
    def statement(self, p):
        return p[0]

    @_('PRINT expr SEMI')
    def print_statement(self, p):
        return PrintStatement(p.expr)

    @_('location ASSIGN expr SEMI')
    def assignment_statement(self, p):
        return AssignmentStatement(p.location, p.expr)

    @_('CONST location dtype ASSIGN expr SEMI',
       'CONST location ASSIGN expr SEMI',
       )
    def const_definition(self, p):
        dtype = p.dtype if hasattr(p, 'dtype') else None
        return ConstDefinition(p.location, p.expr, dtype)

    @_('VAR location dtype ASSIGN expr SEMI',
       'VAR location ASSIGN expr SEMI',
       'VAR location dtype SEMI',
       )
    def variable_definition(self, p):
        dtype = p.dtype if hasattr(p, 'dtype') else None
        expr = p.expr if hasattr(p, 'expr') else None
        return VarDefinition(p.location, expr, dtype)

    @_('IF expr LBRACE statements RBRACE ',
       'IF expr LBRACE statements RBRACE ELSE LBRACE statements RBRACE',
       )
    def if_statement(self, p):
        b_if = p[3]
        b_else = p.statements1 if hasattr(p, 'ELSE') else None
        return IfStatement(p.expr, b_if, b_else)

    @_('WHILE expr LBRACE statements RBRACE',)
    def while_statement(self, p):
        return WhileStatement(p.expr, p.statements)

    @_('BREAK SEMI')
    def break_statement(self, p):
        return Break()

    @_('CONTINUE SEMI')
    def continue_statement(self, p):
        return Continue()

    @_('expr LOR expr',
       'expr LAND expr',
       'expr LT expr',
       'expr LE expr',
       'expr GT expr',
       'expr GE expr',
       'expr EQ expr',
       'expr NE expr',
       'expr PLUS expr',
       'expr MINUS expr',
       'expr TIMES expr',
       'expr DIVIDE expr',
       'PLUS expr %prec UOP',
       'MINUS expr %prec UOP',
       'LNOT expr %prec UOP',
       'LPAREN expr RPAREN',
       'LBRACE compound_expression RBRACE',
       'literal',
       'location',
       )
    def expr(self, p):
        if hasattr(p, 'literal') or hasattr(p, 'location'):
            return p[0]
        elif hasattr(p, 'LPAREN') or hasattr(p, 'LBRACE'):
            return p[1]
        elif len(p) == 3:
            return BinOp(p[1], p.expr0, p.expr1)
        else:
            return UnOp(p[0], p.expr)

    @_('INTEGER',
       'FLOAT',
       'CHAR',
       'TRUE',
       'FALSE',
       'LPAREN RPAREN',
       )
    def literal(self, p):
        if hasattr(p, 'INTEGER'): return Integer( int(p[0]) )
        if hasattr(p, 'FLOAT'): return Float( float(p[0]) )
        if hasattr(p, 'CHAR'):
            char = p[0][1:-1]
            if len(char) == 4:
                char = chr( int( char.replace('\\x', '0x'), 16 ) )
            return Char( char )
        if hasattr(p, 'TRUE'): return Bool( True )
        if hasattr(p, 'FALSE'): return Bool( False )
        return Unit()

    @_('NAME')
    def location(self, p):
        return Location(p[0])

    @_('NAME')
    def dtype(self, p):
        return p[0]