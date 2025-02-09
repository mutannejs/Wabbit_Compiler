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

    @_('{ global_statement }')
    def global_scope(self, p):
        return p.global_statement

    @_('variable_definition',
       'const_definition',
       'function_definition',
       )
    def global_statement(self, p):
        return p[0]

    @_('FUNC NAME LPAREN function_param RPAREN dtype LBRACE statements RBRACE',
       'FUNC NAME LPAREN function_param RPAREN LBRACE statements RBRACE',
       'FUNC NAME LPAREN RPAREN dtype LBRACE statements RBRACE',
       'FUNC NAME LPAREN RPAREN LBRACE statements RBRACE',
       )
    def function_definition(self, p):
        return FunctionDefinition(
            p.lineno,
            p.NAME,
            p.function_param if hasattr(p, 'function_param') else [],
            p.dtype if hasattr(p, 'dtype') else 'unit',
            p.statements
        )

    @_('NAME dtype SEMI function_param',
       'NAME dtype',
       )
    def function_param(self, p):
        params = [ FunctionParam(
            p.lineno,
            p.dtype,
            p.NAME
        )]
        if hasattr(p, 'function_param'):
            params.extend(p.function_param)
        return params

    @_('{ statement }')
    def statements(self, p):
        return BlockStatement(0, p.statement)

    @_('{ statement }')
    def compound_expression(self, p):
        return CompoundExpression(p.lineno, p.statement)

    @_('print_statement',
       'assignment_statement',
       'variable_definition',
       'const_definition',
       'if_statement',
       'while_statement',
       'function_call',
       'break_statement',
       'continue_statement',
       'return_statement',
       'expr SEMICOLUMN',
       )
    def statement(self, p):
        return p[0]

    @_('PRINT expr SEMICOLUMN')
    def print_statement(self, p):
        return PrintStatement(p.lineno, p.expr)

    @_('location ASSIGN expr SEMICOLUMN')
    def assignment_statement(self, p):
        return AssignmentStatement(p.lineno, p.location, p.expr)

    @_('CONST location dtype ASSIGN expr SEMICOLUMN',
       'CONST location ASSIGN expr SEMICOLUMN',
       )
    def const_definition(self, p):
        dtype = p.dtype if hasattr(p, 'dtype') else None
        return ConstDefinition(p.lineno, p.location, p.expr, dtype)

    @_('VAR location dtype ASSIGN expr SEMICOLUMN',
       'VAR location ASSIGN expr SEMICOLUMN',
       'VAR location dtype SEMICOLUMN',
       )
    def variable_definition(self, p):
        dtype = p.dtype if hasattr(p, 'dtype') else None
        expr = p.expr if hasattr(p, 'expr') else None
        return VarDefinition(p.lineno, p.location, expr, dtype)

    @_('IF expr LBRACE statements RBRACE ',
       'IF expr LBRACE statements RBRACE ELSE LBRACE statements RBRACE',
       )
    def if_statement(self, p):
        b_if = p[3]
        b_else = p.statements1 if hasattr(p, 'ELSE') else None
        return IfStatement(p.lineno, p.expr, b_if, b_else)

    @_('WHILE expr LBRACE statements RBRACE',)
    def while_statement(self, p):
        return WhileStatement(p.lineno, p.expr, p.statements)

    @_('BREAK SEMICOLUMN')
    def break_statement(self, p):
        return Break(p.lineno)

    @_('CONTINUE SEMICOLUMN')
    def continue_statement(self, p):
        return Continue(p.lineno)

    @_('NAME LPAREN functioncall_argument RPAREN')
    def function_call(self, p):
        return FunctionCall(
            p.lineno,
            p.NAME,
            p.functioncall_argument
        )

    @_('expr SEMI functioncall_argument',
       'expr',
       )
    def functioncall_argument(self, p):
        if hasattr(p, 'functioncall_argument'):
            args = [p.expr]
            args.extend(p.functioncall_argument)
            return args
        return [p.expr]

    @_('RETURN expr SEMICOLUMN',
       'RETURN SEMICOLUMN')
    def return_statement(self, p):
        return ReturnStatement(
            p.lineno,
            p.expr if hasattr(p, 'expr') else None
        )

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
       'function_call',
       'location',
       )
    def expr(self, p):
        if hasattr(p, 'literal') or hasattr(p, 'location'):
            return p[0]
        elif hasattr(p, 'LPAREN') or hasattr(p, 'LBRACE'):
            return p[1]
        elif len(p) == 3:
            return BinOp(p.lineno, p[1], p.expr0, p.expr1)
        else:
            if hasattr(p, 'function_call'):
                return p.function_call
            return UnOp(p.lineno, p[0], p.expr)

    @_('INTEGER',
       'FLOAT',
       'CHAR',
       'TRUE',
       'FALSE',
       'LPAREN RPAREN',
       )
    def literal(self, p):
        if hasattr(p, 'INTEGER'): return Integer( p.lineno, int(p[0]) )
        if hasattr(p, 'FLOAT'): return Float( p.lineno, float(p[0]) )
        if hasattr(p, 'CHAR'):
            char = p[0][1:-1]
            if len(char) == 4:
                char = chr( int( char.replace('\\x', '0x'), 16 ) )
            return Char( p.lineno, char )
        if hasattr(p, 'TRUE'): return Bool( p.lineno, True )
        if hasattr(p, 'FALSE'): return Bool( p.lineno, False )
        return Unit( p.lineno )

    @_('NAME')
    def location(self, p):
        return Location(p.lineno, p[0])

    @_('NAME')
    def dtype(self, p):
        return p[0]