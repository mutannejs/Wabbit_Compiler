from .model import *

class _NodeVisitor:
    def __init__(self):
        self.tabs = 0

    def visit(self, node: Node):
        methname = node.__class__.__name__
        return getattr(self, f'visit_{methname}')(node)

    def visit_Integer(self, node: Integer):
        return node.value

    def visit_Float(self, node: Float):
        return node.value

    def visit_Char(self, node: Char):
        return repr(node.value) if node.value[0] != '\\' else f"'{node.value}'"

    def visit_Bool(self, node: Bool):
        return 'true' if node.value else 'false'

    def visit_Unit(self, node: Unit):
        return '()'

    def visit_Break(self, node: Break):
        return 'break;'

    def visit_Continue(self, node: Continue):
        return 'continue;'

    def visit_PrintStatement(self, node: PrintStatement):
        return f'print {self.visit(node.expr)};'

    def visit_UnOp(self, node: UnOp):
        return f'{node.op}{self.visit(node.expr)}'

    def visit_BinOp(self, node: BinOp):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_Location(self, node: Location):
        return f'{node.name}'

    def visit_VarDefinition(self, node: VarDefinition):
        base = f'var {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_ConstDefinition(self, node: ConstDefinition):
        base = f'const {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        return f'{self.visit(node.location)} = {self.visit(node.value)};'

    def visit_BlockStatement(self, node: BlockStatement):
        self.tabs += 1
        tabs = ''.rjust(self.tabs * 4, ' ')

        insts = ''
        for inst in node.instructions:
            insts += tabs + self.visit(inst) + '\n'

        self.tabs -= 1
        return insts

    def visit_IfStatement(self, node: IfStatement):
        tabs = ''.rjust(self.tabs * 4, ' ')
        block_if = f'if {self.visit(node.cmp)} {{\n{self.visit(node.block_if)}{tabs}}}'
        block_else = f' else {{\n{self.visit(node.block_else)}{tabs}}}' if node.block_else else ''
        return block_if + block_else

    def visit_WhileStatement(self, node: WhileStatement):
        tabs = ''.rjust(self.tabs * 4, ' ')
        cmp = self.visit(node.cmp)
        body = self.visit(node.body)
        return f'while {cmp} {{\n{body}{tabs}}}'

    def visit_CompoundExpression(self, node: CompoundExpression):
        insts = ''

        for inst in node.instructions:
            insts += ' ' + f'{self.visit(inst)}'
            if isinstance(inst, Expression): insts += ';'

        return f'{{{insts} }}'

    def visit_FunctionDefinition(self, node: FunctionDefinition):
        body = self.visit_BlockStatement(node.body)

        params = ''
        if len(node.params) == 0:
            params = ''
        elif len(node.params) == 1:
            params = node.params[0]
        else:
            for a in node.params[:-1]:
                params += self.visit(a) + ', '
            params += self.visit(node.params[-1])

        return f'func {node.name}({params}) {node.ret} {{\n{body}}}'

    def visit_FunctionParam(self, node: FunctionParam):
        return f'{node.name} {node.dtype}'

    def visit_FunctionCall(self, node: FunctionCall):
        args = ''
        if len(node.args) == 0:
            args = ''
        elif len(node.args) == 1:
            args = self.visit(node.args[0])
        else:
            for a in node.args[:-1]:
                args += f'{self.visit(a)}' + ', '
            args += f'{self.visit(node.args[-1])}'
        return f'{node.name}({args})'

    def visit_ReturnStatement(self, node: ReturnStatement):
        return f'return {self.visit(node.expr)};'


def to_source(model):
    codes = []
    for node in model:
        codes.append( _NodeVisitor().visit(node) )
    return '\n'.join(codes) + '\n'