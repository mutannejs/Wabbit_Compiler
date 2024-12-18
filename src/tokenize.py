import sys
sys.path.insert(0, 'sly.zip')
from sly import Lexer

class WabbitLexer(Lexer):
    tokens = {
        # bloco de comentário
        # COMMENTBLOCK,
        # UNCOMMENTBLOCK, # Unterminated comment block

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
        FLOAT,
        INTEGER,
        CHAR,
        # UNCHAR, # unterminated character const

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
        ASSIGN,
        SEMI,
        LPAREN,
        RPAREN,
        LBRACE,
        RBRACE
    }

    ignore = ' \t'
    ignore_comment = r'\//.*'

    COMMENTBLOCK = r'/\*(.|\n)*?\*/'
    UNCOMMENTBLOCK = COMMENTBLOCK[:-4]

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

    FLOAT = r'[0-9]+\.[0-9]+'
    INTEGER = r'[0-9]+'
    CHAR = r"'((\S)|(\\x[0-9a-fA-F]{2})|(\\[n']))'"
    UNCHAR = CHAR[-1]

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

    ASSIGN = r'='
    SEMI = r';'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def COMMENTBLOCK(self, t):
        self.lineno += t.value.count('\n')
        pass

    def UNCOMMENTBLOCK(self, t):
        print(self.lineno,': Unterminated comment')

    def UNCHAR(self, t):
        print(self.lineno,': Unterminated character constant')


def tokenize(text: str):
    return WabbitLexer().tokenize(text);