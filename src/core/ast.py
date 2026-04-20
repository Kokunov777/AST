"""
Абстрактное синтаксическое дерево (AST) для объявления комплексных чисел в Rust.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union, Any
from enum import Enum


class NodeType(Enum):
    """Типы узлов AST."""
    LET_DECL = "LetDecl"
    CALL_EXPR = "CallExpr"
    PATH = "Path"
    INT_LITERAL = "IntLiteral"
    FLOAT_LITERAL = "FloatLiteral"
    UNARY_EXPR = "UnaryExpr"
    BINARY_EXPR = "BinaryExpr"


@dataclass
class ASTNode:
    """Базовый класс узла AST."""
    node_type: NodeType
    start_line: int = 1
    start_col: int = 1
    end_line: int = 1
    end_col: int = 1

    def accept(self, visitor: 'ASTVisitor'):
        """Принятие посетителя для обхода дерева."""
        method_name = f'visit_{self.node_type.value.lower()}'
        visitor_method = getattr(visitor, method_name, visitor.visit_generic)
        return visitor_method(self)


@dataclass
class LetDeclNode(ASTNode):
    """Узел объявления переменной через let."""
    name: str = ""
    value: Optional['ExprNode'] = None
    type_annotation: Optional[str] = None  # например, "Complex<f64>", но в нашем случае не указан

    def __post_init__(self):
        self.node_type = NodeType.LET_DECL


@dataclass
class ExprNode(ASTNode):
    """Базовый класс для выражений."""
    pass


@dataclass
class CallExprNode(ExprNode):
    """Узел вызова функции."""
    callee: 'PathNode' = None
    arguments: List['ExprNode'] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.CALL_EXPR


@dataclass
class PathNode(ExprNode):
    """Узел пути (например, num::complex::Complex::new)."""
    segments: List[str] = field(default_factory=list)  # ["num", "complex", "Complex", "new"]

    def __post_init__(self):
        self.node_type = NodeType.PATH


@dataclass
class IntLiteralNode(ExprNode):
    """Узел целочисленного литерала."""
    value: int = 0

    def __post_init__(self):
        self.node_type = NodeType.INT_LITERAL


@dataclass
class FloatLiteralNode(ExprNode):
    """Узел вещественного литерала."""
    value: float = 0.0

    def __post_init__(self):
        self.node_type = NodeType.FLOAT_LITERAL


@dataclass
class UnaryExprNode(ExprNode):
    """Узел унарного выражения (например, -4.2)."""
    operator: str = ""  # "-"
    operand: ExprNode = None

    def __post_init__(self):
        self.node_type = NodeType.UNARY_EXPR


# Для совместимости типов
ExprNode = Union[CallExprNode, PathNode, IntLiteralNode, FloatLiteralNode, UnaryExprNode]


class ASTVisitor:
    """Базовый посетитель для обхода AST."""
    def visit_generic(self, node: ASTNode):
        """Общий метод для узлов, для которых нет специализированного метода."""
        pass

    def visit_letdecl(self, node: LetDeclNode):
        self.visit_generic(node)

    def visit_callexpr(self, node: CallExprNode):
        self.visit_generic(node)

    def visit_path(self, node: PathNode):
        self.visit_generic(node)

    def visit_intliteral(self, node: IntLiteralNode):
        self.visit_generic(node)

    def visit_floatliteral(self, node: FloatLiteralNode):
        self.visit_generic(node)

    def visit_unaryexpr(self, node: UnaryExprNode):
        self.visit_generic(node)


class PrintVisitor(ASTVisitor):
    """Посетитель для печати AST в виде дерева с отступами."""
    def __init__(self):
        self.level = 0
        self.lines = []

    def _indent(self):
        return "    " * self.level

    def visit_generic(self, node: ASTNode):
        self.lines.append(f"{self._indent()}{node.node_type.value}")

    def visit_letdecl(self, node: LetDeclNode):
        self.lines.append(f"{self._indent()}LetDeclNode")
        self.lines.append(f"{self._indent()}├── name: \"{node.name}\"")
        if node.type_annotation:
            self.lines.append(f"{self._indent()}├── type: {node.type_annotation}")
        self.lines.append(f"{self._indent()}└── value:")
        self.level += 1
        if node.value:
            node.value.accept(self)
        self.level -= 1

    def visit_callexpr(self, node: CallExprNode):
        self.lines.append(f"{self._indent()}CallExprNode")
        self.lines.append(f"{self._indent()}├── callee:")
        self.level += 1
        node.callee.accept(self)
        self.level -= 1
        self.lines.append(f"{self._indent()}└── arguments:")
        self.level += 1
        for i, arg in enumerate(node.arguments):
            if i < len(node.arguments) - 1:
                self.lines.append(f"{self._indent()}├── [{i}]:")
            else:
                self.lines.append(f"{self._indent()}└── [{i}]:")
            self.level += 1
            arg.accept(self)
            self.level -= 1
        self.level -= 1

    def visit_path(self, node: PathNode):
        self.lines.append(f"{self._indent()}PathNode")
        self.lines.append(f"{self._indent()}└── segments: {node.segments}")

    def visit_intliteral(self, node: IntLiteralNode):
        self.lines.append(f"{self._indent()}IntLiteralNode")
        self.lines.append(f"{self._indent()}└── value: {node.value}")

    def visit_floatliteral(self, node: FloatLiteralNode):
        self.lines.append(f"{self._indent()}FloatLiteralNode")
        self.lines.append(f"{self._indent()}└── value: {node.value}")

    def visit_unaryexpr(self, node: UnaryExprNode):
        self.lines.append(f"{self._indent()}UnaryExprNode")
        self.lines.append(f"{self._indent()}├── operator: \"{node.operator}\"")
        self.lines.append(f"{self._indent()}└── operand:")
        self.level += 1
        node.operand.accept(self)
        self.level -= 1

    def get_result(self) -> str:
        return "\n".join(self.lines)


def ast_to_json(node: ASTNode) -> dict:
    """Преобразование AST в JSON-подобный словарь."""
    if isinstance(node, LetDeclNode):
        return {
            "type": "LetDecl",
            "name": node.name,
            "value": ast_to_json(node.value) if node.value else None,
            "type_annotation": node.type_annotation,
            "position": f"{node.start_line}:{node.start_col}-{node.end_line}:{node.end_col}"
        }
    elif isinstance(node, CallExprNode):
        return {
            "type": "CallExpr",
            "callee": ast_to_json(node.callee),
            "arguments": [ast_to_json(arg) for arg in node.arguments],
            "position": f"{node.start_line}:{node.start_col}-{node.end_line}:{node.end_col}"
        }
    elif isinstance(node, PathNode):
        return {
            "type": "Path",
            "segments": node.segments,
            "position": f"{node.start_line}:{node.start_col}-{node.end_line}:{node.end_col}"
        }
    elif isinstance(node, IntLiteralNode):
        return {
            "type": "IntLiteral",
            "value": node.value,
            "position": f"{node.start_line}:{node.start_col}-{node.end_line}:{node.end_col}"
        }
    elif isinstance(node, FloatLiteralNode):
        return {
            "type": "FloatLiteral",
            "value": node.value,
            "position": f"{node.start_line}:{node.start_col}-{node.end_line}:{node.end_col}"
        }
    elif isinstance(node, UnaryExprNode):
        return {
            "type": "UnaryExpr",
            "operator": node.operator,
            "operand": ast_to_json(node.operand),
            "position": f"{node.start_line}:{node.start_col}-{node.end_line}:{node.end_col}"
        }
    else:
        return {"type": "Unknown"}