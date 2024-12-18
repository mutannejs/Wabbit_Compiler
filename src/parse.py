from sly import Parser
from .lexer import WabbitLexer
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
        return p.statement

    @_('print_statement',
    #    'assignment_statement',
    #    'variable_definition',
       'const_definition',
    #    'if_statement',
    #    'while_statement',
       'break_statement',
       'continue_statement',
       'expr SEMI')
    def statement(self, p):
        if len(p) == 2:
            return ('expr', p[0])
        else:
            return p[0]

    @_('PRINT expr SEMI')
    def print_statement(self, p):
        return Print(p.expr)

    @_('CONST location NAME ASSIGN expr SEMI',
       'CONST location ASSIGN expr SEMI')
    def const_definition(self, p):
        if hasattr(p, 'NAME'):
            return DeclarationConst(p.location, p.expr, p.NAME)
        else:
            return DeclarationConst(p.location, p.expr, None)

    # @_('IF expr LBRACE statements RBRACE ')
    #    'IF expr LBRACE statements RBRACE ELSE LBRACE statements RBRACE')

    # @_('WHILE expr LBRACE statements RBRACE',)
    # def while_statement(self, p):
    #     return WhileStatement(self.expr, p.statements)

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
       'literal',
       'location')
    def expr(self, p):
        if len(p) == 1:
            return p[0]
        elif hasattr(p, 'LPAREN'):
            return p.expr
        elif len(p) == 3:
            return BinOp(p[1], p.expr0, p.expr1)
        else:
            return UnOp(p[0], p.expr)

    @_('INTEGER',
       'FLOAT',
       'CHAR',
       'TRUE',
       'FALSE',
       'LPAREN RPAREN')
    def literal(self, p):
        if hasattr(p, 'INTEGER'): return Integer( int(p[0]) )
        if hasattr(p, 'FLOAT'): return Float( float(p[0]) )
        if hasattr(p, 'CHAR'): return Char(p[0])
        if hasattr(p, 'TRUE'): return Bool( True )
        if hasattr(p, 'FALSE'): return Bool( False )
        return Unit()

    @_('NAME')
    def location(self, p):
        if p.NAME in DataTypes:
            return p[0]
        else:
            return Location(p[0])

    @_('')
    def empty(self, p):
        pass