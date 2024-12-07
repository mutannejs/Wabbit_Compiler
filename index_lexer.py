from src.lexer import WabbitLexer

lexer = WabbitLexer()

# Primeiro exemplo
data = r'''
    print 5 'a' '\n' '\x45'
    a + b - c * e / !j
    a < b <= c > d >= f
    a && y || ç == c != 5
    a = b; ( { () } )
'''
for tok in lexer.tokenize(data):
    print(tok)
print('\n')

# Segundo exemplo
data = r'''/* print values of factorials */

var n int = 1;
var value int = 1;

while n < 10 {
    value = value * n;
    print value ;
    n = n + 1;
}'''
for tok in lexer.tokenize(data):
    print(tok)
print('\n')

# Terceiro exemplo
data = r'''/* hello */
print 'h';
print 'e';
print 'l';
print 'l';
print 'o;

/* world
print 'w';
print 'o';
print 'r';
print 'l';
print 'd;
print '!';
'''
for tok in lexer.tokenize(data):
    print(tok)