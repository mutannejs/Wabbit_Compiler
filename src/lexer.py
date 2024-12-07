from sly import Lexer

class WabbitLexer(Lexer):
    tokens = {
        # keywords
        CONST,
        VAR,
        PRINT,
        BREAK,
        CONTINUE,
        IF,
        ELSE,
        WHILE,
        TRUE,
        FALSE,

        # identificadores / nomes
        NAME,

        # literais
        INTEGER,
        FLOAT,
        CHAR,

        # operadores
        PLUS,
        MINUS,
        TIMES,
        DIVIDE,
        LE,
        LT,
        GE,
        GT,
        EQ,
        NE,
        LAND,
        LOR,
        LNOT,

        # diversos
        ASSGIN,
        SEMI,
        LPAREN,
        RPAREN,
        LBRACE,
        RBRACE
    }

    ignore = ' \t'

    # tokens
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NAME['const'] = CONST
    NAME['var'] = VAR
    NAME['print'] = PRINT
    NAME['break'] = BREAK
    NAME['continue'] = CONTINUE
    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['true'] = TRUE
    NAME['false'] = FALSE

    INTEGER = r'[0-9]+'
    FLOAT = r'[0-9]+.[0-9]+'
    CHAR = r"('[a-zA-Z]')|('\\x[0-9a-fA-F]{2}')|('\\[n']')"

    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    LAND = r'&&'
    LOR = r'\|\|'
    LNOT = r'!'

    ASSGIN = r'='
    SEMI = r';'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'

    def __init__(self):
        self.lineno = 0
        self.index = 0

    # Error handling rule
    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)
        self.index += len(t.value)

    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    def CHAR(self, t):
        t.value = t.value[1:-1]
        return t