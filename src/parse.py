from sly import Parser
from .lexer import WabbitLexer
from .model import *

class WabbitParser(Parser):
    tokens = WabbitLexer.tokens

    @_('INTEGER')
    @_('FLOAT')
    @_('CHAR')
    @_('TRUE')
    @_('FALSE')
    @_('LPAREN RPAREN')
    def literal(self, p):
        if hasattr(p, 'INTEGER'): return Integer( int(p[0]) )
        if hasattr(p, 'FLOAT'): return Float( float(p[0]) )
        if hasattr(p, 'CHAR'): return Char(p[0])
        if hasattr(p, 'TRUE'): return Bool( True )
        if hasattr(p, 'FALSE'): return Bool( False )
        return Unit()

    @_('NAME')
    def location(self, p):
        if hasattr(p, 'int') or hasattr(p, 'float') or hasattr(p, 'bool') or hasattr(p, 'int') or hasattr(p, 'unit'): return p[0]
        return Location(p[0])

    # @_('NAME')
    # def type(self, p):
    #     return p[0] # DType