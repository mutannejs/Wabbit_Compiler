from src.tokenize import tokenize

# Primeiro exemplo
data = r'''
    print 5 'a' '\n' '\x45'
    a + b - c * e / !j
    a < b <= c > d >= f
    a && y || ç == c != 5
    a = b; ( { () } )
'''
for tok in tokenize(data):
    print(tok)
print('\n')

# Segundo exemplo
data = r'''/*
    Test of break/continue 


var n int = 0;
while true {
      n = n + 1;
      if n == 5 {
         continue;
      }
      print n;
      if n > 10 {
          break;
      }
}
print -1;'''
for tok in tokenize(data):
    print(tok)
print('\n')

# Terceiro exemplo
data = r'''/* chartest.wb */

const newline = '\n';
print 'h';
print 'e';
print 'l';
print 'l';
print 'o';
print newline;
print 'w';
print 'o';
print 'r';
print 'l';
print 'd';
print newline;'''
for tok in tokenize(data):
    print(tok)
print('\n')

# Quarto exemplo
data = r'''
float a = 2.0;
int b = 2 . 3;
print '.' ();
'''
for tok in tokenize(data):
    print(tok)