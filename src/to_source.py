from .model import *

class _NodeVisitor:
    def __init__(self):
        pass

    def visit(self, node: Node):
        methname = node.__class__.__name__
        return getattr(self, f'visit_{methname}')(node)

    def visit_BlockStatement(self, node: BlockStatement):
        tabs = ''.rjust(node.tabs * 4, ' ')

        sttmts = ''
        for st in node.statements:
            sttmts += tabs + self.visit(st) + '\n'
        return sttmts

    def visit_Integer(self, node: Integer):
        return node.value

    def visit_Float(self, node: Float):
        return node.value

    def visit_Char(self, node: Char):
        return repr(node.value)

    def visit_Bool(self, node: Bool):
        return 'true' if node.value else 'false'

    def visit_Unit(self, node: Unit):
        return f'()'

    def visit_Print(self, node: Print):
        return f'print {self.visit(node.expr)};'

    def visit_UnOp(self, node: UnOp):
        return f'{node.op}{self.visit(node.expr)}'

    def visit_BinOp(self, node: BinOp):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_Location(self, node: Location):
        return f'{node.name}'

    def visit_DeclarationVar(self, node: DeclarationVar):
        base = f'var {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_DeclarationConst(self, node: DeclarationConst):
        base = f'const {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_Assignment(self, node: Assignment):
        return f'{self.visit(node.location)} = {self.visit(node.value)};'

    def visit_IfStatement(self, node: IfStatement):
        tabs = ''.rjust(node.tabs * 4, ' ')
        block_if = f'if {self.visit(node.cmp)} {{\n{self.visit(node.block_if)}{tabs}}}'
        block_else = f' else {{\n{self.visit(node.block_else)}{tabs}}}' if node.block_else else ''
        return block_if + block_else

    def visit_WhileStatement(self, node: WhileStatement):
        tabs = ''.rjust(node.tabs * 4, ' ')
        return f'while {self.visit(node.cmp)} {{\n{self.visit(node.body)}{tabs}}}'

    def visit_CompoundExpression(self, node: CompoundExpression):
        insts = ''
        for inst in node.instructions:
            insts += ' ' + self.visit(inst)
        if isinstance(node.instructions[-1], Expression):
            insts += ';'
        return f'{{{insts} }}'

    def visit_Argument(self, node: Argument):
        return f'{node.name} {node.dtype}'

    def visit_ReturnStatement(self, node: ReturnStatement):
        return f'return {self.visit(node.value)};'

    def visit_FunctionDefinition(self, node: FunctionDefinition):
        params = ''
        if node.params:
            for a in node.params[:-1]:
                params += f'{self.visit(a)}, '
            params += f'{self.visit(node.params[-1])}'
        interface = f'func {node.name}({params}) {node.typeReturn+" " if node.typeReturn != "unit" else ""}{{'
        blockSt = f'{self.visit(node.statements)}'
        return f'{interface}\n{blockSt}}}'

    def visit_FunctionApplication(self, node: FunctionApplication):
        args = ''
        for a in node.args[:-1]:
            args += f'{self.visit(a)}, '
        args += f'{self.visit(node.args[-1])}'
        return f'{node.name}({args})'

    def visit_Program(self, node: Program):
        strCode = ''
        for d in node.declarations[:-1]:
            strCode += f'{self.visit(d)}\n\n'
        strCode += f'{self.visit(node.declarations[-1])}'
        return strCode


def to_source(node):
    return _NodeVisitor().visit(node)