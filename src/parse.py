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

    @_('PRINT expr SEMI')
    def print_statement(self, p):
        return Print(p.expr)

    @_('CONST NAME dtype ASSIGN expr SEMI')
    def const_definition(self, p):
        return DeclarationConst(p.NAME, p.expr, p.dtype)

    # @_('IF expr LBRACE statements RBRACE ')
    #    'WHILE expr LBRACE statements RBRACE ELSE LBRACE statements RBRACE')

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
        return Location(p[0])

    @_('NAME',
       'empty')
    def dtype(self, p):
        return p[0] if len(p) == 1 else None

    @_('')
    def empty(self, p):
        pass