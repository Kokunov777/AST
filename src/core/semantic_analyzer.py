"""
Семантический анализатор для объявления комплексных чисел в Rust.
Строит AST и проверяет контекстно-зависимые условия.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .analyzer import Token, TokenType
from .ast import (
    LetDeclNode, CallExprNode, PathNode, IntLiteralNode,
    FloatLiteralNode, UnaryExprNode, ASTNode, NodeType
)


@dataclass
class SemanticError:
    """Ошибка семантического анализа."""
    line: int
    column: int
    message: str
    fragment: str


class SymbolTable:
    """Таблица символов для хранения объявленных идентификаторов в текущей области видимости."""
    def __init__(self):
        self.symbols: Dict[str, Dict[str, Any]] = {}  # имя -> информация

    def add(self, name: str, node_type: str, line: int, col: int) -> bool:
        """Добавить символ. Возвращает False, если уже объявлен."""
        if name in self.symbols:
            return False
        self.symbols[name] = {"type": node_type, "line": line, "col": col}
        return True

    def contains(self, name: str) -> bool:
        """Проверить, объявлен ли символ."""
        return name in self.symbols

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о символе."""
        return self.symbols.get(name)


class SemanticAnalyzer:
    def __init__(self, tokens: List[Token]):
        # Фильтруем пробелы и ошибки лексического анализа (как в синтаксическом анализаторе)
        from .analyzer import TokenType
        self.tokens = [t for t in tokens if t.type not in (TokenType.WHITESPACE, TokenType.ERROR)]
        self.errors: List[SemanticError] = []
        self.pos = 0
        self.symbol_table = SymbolTable()
        self.ast: Optional[LetDeclNode] = None  # корень AST (объявление)
        # Предопределённые модули и функции для проверки правила 4
        self.predefined_identifiers = {
            "num": "module",
            "complex": "module",
            "Complex": "type",
            "new": "function"
        }

    def analyze(self) -> List[SemanticError]:
        """Запуск семантического анализа и построения AST."""
        self.errors.clear()
        self.pos = 0
        self.symbol_table = SymbolTable()
        
        # Ожидаем одно или несколько объявлений
        statements = []
        while self.pos < len(self.tokens):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        # В нашей грамматике только одно объявление, но на будущее
        if statements:
            self.ast = statements[0]
        return self.errors

    # ========== Вспомогательные методы для разбора ==========

    def _current_token(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _match(self, expected_type: TokenType, lexeme: Optional[str] = None) -> bool:
        token = self._current_token()
        if token and token.type == expected_type:
            if lexeme is not None and token.lexeme != lexeme:
                return False
            self.pos += 1
            return True
        return False

    def _consume(self, expected_type: TokenType, lexeme: Optional[str] = None, error_msg: str = "") -> bool:
        if self._match(expected_type, lexeme):
            return True
        token = self._current_token()
        if token:
            fragment = token.lexeme
            line = token.start_line
            col = token.start_col
        else:
            fragment = "конец файла"
            line = self.tokens[-1].end_line if self.tokens else 1
            col = self.tokens[-1].end_col if self.tokens else 1
        if not error_msg:
            expected = f"'{lexeme}'" if lexeme else expected_type.name
            error_msg = f"Ожидается {expected}, но получено '{fragment}'"
        self.errors.append(SemanticError(line, col, error_msg, fragment))
        # Пропускаем токен для продолжения
        self.pos += 1
        return False

    # ========== Правила грамматики с построением AST ==========

    def _parse_statement(self) -> Optional[LetDeclNode]:
        """<statement> → KEYWORD IDENTIFIER OPERATOR expression END_OF_STATEMENT"""
        start_token = self._current_token()
        if not start_token:
            return None
        
        # KEYWORD 'let'
        if not self._consume(TokenType.KEYWORD, "let", "Ожидается ключевое слово 'let'"):
            return None
        
        # IDENTIFIER
        ident_token = self._current_token()
        if not self._consume(TokenType.IDENTIFIER, None, "Ожидается идентификатор после 'let'"):
            return None
        ident_name = ident_token.lexeme
        
        # Проверка правила 1: уникальность идентификатора
        if not self.symbol_table.add(ident_name, "variable", ident_token.start_line, ident_token.start_col):
            self.errors.append(SemanticError(
                ident_token.start_line, ident_token.start_col,
                f"Идентификатор '{ident_name}' уже объявлен ранее",
                ident_name
            ))
        
        # OPERATOR '='
        if not self._consume(TokenType.OPERATOR, "=", "Ожидается оператор '=' после идентификатора"):
            return None
        
        # expression
        value_expr = self._parse_expression()
        if value_expr is None:
            # Ошибка уже добавлена внутри _parse_expression
            pass
        
        # END_OF_STATEMENT ';'
        self._consume(TokenType.END_OF_STATEMENT, ";", "Ожидается ';' в конце оператора")
        
        # Создаем узел объявления
        node = LetDeclNode(
            node_type=NodeType.LET_DECL,
            name=ident_name,
            value=value_expr,
            start_line=start_token.start_line,
            start_col=start_token.start_col,
            end_line=self.tokens[self.pos - 1].end_line if self.pos > 0 else start_token.end_line,
            end_col=self.tokens[self.pos - 1].end_col if self.pos > 0 else start_token.end_col
        )
        return node

    def _parse_expression(self) -> Optional[ASTNode]:
        """<expression> → path SEPARATOR '(' arguments SEPARATOR ')'"""
        start_token = self._current_token()
        if not start_token:
            return None
        
        # path
        callee_path = self._parse_path()
        if callee_path is None:
            return None
        
        # SEPARATOR '('
        if not self._consume(TokenType.SEPARATOR, "(", "Ожидается '(' после пути"):
            return None
        
        # arguments
        arguments = self._parse_arguments()
        
        # SEPARATOR ')'
        if not self._consume(TokenType.SEPARATOR, ")", "Ожидается ')' после аргументов"):
            return None
        
        # Проверка правила 4: использование идентификаторов в пути
        self._check_path_identifiers(callee_path)
        
        # Создаем узел вызова
        node = CallExprNode(
            node_type=NodeType.CALL_EXPR,
            callee=callee_path,
            arguments=arguments,
            start_line=start_token.start_line,
            start_col=start_token.start_col,
            end_line=self.tokens[self.pos - 1].end_line if self.pos > 0 else start_token.end_line,
            end_col=self.tokens[self.pos - 1].end_col if self.pos > 0 else start_token.end_col
        )
        return node

    def _parse_path(self) -> Optional[PathNode]:
        """<path> → IDENTIFIER (COLON COLON IDENTIFIER)*"""
        start_token = self._current_token()
        if not start_token:
            return None
        
        segments = []
        # Первый идентификатор обязателен
        ident_token = self._current_token()
        if not self._consume(TokenType.IDENTIFIER, None, "Ожидается идентификатор в пути"):
            return None
        segments.append(ident_token.lexeme)
        
        # Повторяем пары COLON COLON IDENTIFIER
        while self._current_token() and self._current_token().type == TokenType.COLON:
            # Пропускаем два двоеточия
            self.pos += 1
            if not self._match(TokenType.COLON):
                # Если только одно двоеточие, ошибка
                token = self._current_token()
                if token:
                    self.errors.append(SemanticError(
                        token.start_line, token.start_col,
                        "Ожидается второе ':' для оператора '::'",
                        token.lexeme
                    ))
                break
            # После '::' должен быть идентификатор
            if not self._consume(TokenType.IDENTIFIER, None, "Ожидается идентификатор после '::'"):
                break
            segments.append(self.tokens[self.pos - 1].lexeme)
        
        node = PathNode(
            node_type=NodeType.PATH,
            segments=segments,
            start_line=start_token.start_line,
            start_col=start_token.start_col,
            end_line=self.tokens[self.pos - 1].end_line if self.pos > 0 else start_token.end_line,
            end_col=self.tokens[self.pos - 1].end_col if self.pos > 0 else start_token.end_col
        )
        return node

    def _parse_arguments(self) -> List[ASTNode]:
        """<arguments> → number (SEPARATOR ',' number)*"""
        args = []
        # Первое число
        num_node = self._parse_number()
        if num_node:
            args.append(num_node)
        else:
            # Если нет числа, это ошибка, но возможно пустой список аргументов?
            # В нашей грамматике аргументы должны быть хотя бы одно число.
            token = self._current_token()
            if token:
                self.errors.append(SemanticError(
                    token.start_line, token.start_col,
                    "Ожидается число в качестве аргумента",
                    token.lexeme
                ))
            return args
        
        # Дополнительные аргументы через запятую
        while self._current_token() and self._current_token().type == TokenType.SEPARATOR and self._current_token().lexeme == ",":
            self.pos += 1  # пропускаем ','
            next_num = self._parse_number()
            if next_num:
                args.append(next_num)
            else:
                # Ошибка, но продолжаем
                pass
        
        # Проверка правила 2: совместимость типов (все аргументы должны быть числами)
        # Проверка правила 3: допустимые значения (пределы)
        for arg in args:
            self._check_number_node(arg)
        
        return args

    def _parse_number(self) -> Optional[ASTNode]:
        """<number> → INTEGER | FLOAT | OPERATOR '-' FLOAT | OPERATOR '-' INTEGER"""
        start_token = self._current_token()
        if not start_token:
            return None
        
        # Проверяем наличие унарного минуса
        if self._match(TokenType.OPERATOR, "-"):
            operator_token = start_token
            # После минуса должно быть число
            if self._match(TokenType.FLOAT):
                token = self.tokens[self.pos - 1]
                try:
                    value = -float(token.lexeme)
                except ValueError:
                    value = 0.0
                node = FloatLiteralNode(
                    node_type=NodeType.FLOAT_LITERAL,
                    value=value,
                    start_line=operator_token.start_line,
                    start_col=operator_token.start_col,
                    end_line=token.end_line,
                    end_col=token.end_col
                )
                return UnaryExprNode(
                    node_type=NodeType.UNARY_EXPR,
                    operator="-",
                    operand=node,
                    start_line=operator_token.start_line,
                    start_col=operator_token.start_col,
                    end_line=token.end_line,
                    end_col=token.end_col
                )
            elif self._match(TokenType.INTEGER):
                token = self.tokens[self.pos - 1]
                try:
                    value = -int(token.lexeme)
                except ValueError:
                    value = 0
                node = IntLiteralNode(
                    node_type=NodeType.INT_LITERAL,
                    value=value,
                    start_line=operator_token.start_line,
                    start_col=operator_token.start_col,
                    end_line=token.end_line,
                    end_col=token.end_col
                )
                return UnaryExprNode(
                    node_type=NodeType.UNARY_EXPR,
                    operator="-",
                    operand=node,
                    start_line=operator_token.start_line,
                    start_col=operator_token.start_col,
                    end_line=token.end_line,
                    end_col=token.end_col
                )
            else:
                # Ошибка: после минуса нет числа
                token = self._current_token()
                if token:
                    self.errors.append(SemanticError(
                        token.start_line, token.start_col,
                        "Ожидается число после '-'",
                        token.lexeme
                    ))
                return None
        else:
            # Без знака
            if self._match(TokenType.FLOAT):
                token = self.tokens[self.pos - 1]
                try:
                    value = float(token.lexeme)
                except ValueError:
                    value = 0.0
                return FloatLiteralNode(
                    node_type=NodeType.FLOAT_LITERAL,
                    value=value,
                    start_line=token.start_line,
                    start_col=token.start_col,
                    end_line=token.end_line,
                    end_col=token.end_col
                )
            elif self._match(TokenType.INTEGER):
                token = self.tokens[self.pos - 1]
                try:
                    value = int(token.lexeme)
                except ValueError:
                    value = 0
                return IntLiteralNode(
                    node_type=NodeType.INT_LITERAL,
                    value=value,
                    start_line=token.start_line,
                    start_col=token.start_col,
                    end_line=token.end_line,
                    end_col=token.end_col
                )
        return None

    def _check_path_identifiers(self, path_node: PathNode):
        """Проверка правила 4: использование идентификаторов в пути."""
        # Для учебного проекта считаем, что допустимы только предопределённые идентификаторы
        for segment in path_node.segments:
            if segment not in self.predefined_identifiers and not self.symbol_table.contains(segment):
                self.errors.append(SemanticError(
                    path_node.start_line, path_node.start_col,
                    f"Идентификатор '{segment}' не объявлен и не является предопределённым",
                    segment
                ))
        # Дополнительная проверка: путь должен быть num::complex::Complex::new
        if len(path_node.segments) == 4:
            expected = ["num", "complex", "Complex", "new"]
            if path_node.segments != expected:
                self.errors.append(SemanticError(
                    path_node.start_line, path_node.start_col,
                    f"Ожидается путь 'num::complex::Complex::new', получен '{'::'.join(path_node.segments)}'",
                    "::".join(path_node.segments)
                ))

    def _check_number_node(self, node: ASTNode):
        """Проверка правил 2 и 3 для числовых узлов."""
        if isinstance(node, FloatLiteralNode):
            # Проверка допустимых значений (правило 3)
            # Для f64 диапазон примерно ±1.7976931348623157e+308
            # Упрощённо: проверяем, что значение не слишком большое
            value = node.value
            if abs(value) > 1e308:
                self.errors.append(SemanticError(
                    node.start_line, node.start_col,
                    f"Вещественное значение {value} выходит за допустимые пределы",
                    str(value)
                ))
            # Правило 2: совместимость типов - для комплексных чисел ожидается f64
            # В нашем случае все вещественные числа подходят
        elif isinstance(node, IntLiteralNode):
            value = node.value
            # Для i32 диапазон -2147483648..2147483647
            if not (-2147483648 <= value <= 2147483647):
                self.errors.append(SemanticError(
                    node.start_line, node.start_col,
                    f"Целое значение {value} выходит за допустимые пределы для i32",
                    str(value)
                ))
        elif isinstance(node, UnaryExprNode):
            # Рекурсивно проверяем операнд
            self._check_number_node(node.operand)

    # ========== Публичные методы ==========

    def get_ast(self) -> Optional[LetDeclNode]:
        """Возвращает построенное AST."""
        return self.ast

    def get_ast_text(self) -> str:
        """Возвращает текстовое представление AST."""
        from .ast import PrintVisitor
        if not self.ast:
            return "AST не построено"
        visitor = PrintVisitor()
        self.ast.accept(visitor)
        return visitor.get_result()

    def get_ast_json(self) -> dict:
        """Возвращает AST в виде JSON-подобного словаря."""
        from .ast import ast_to_json
        if not self.ast:
            return {}
        return ast_to_json(self.ast)


def analyze_semantics(tokens: List[Token]) -> tuple[List[SemanticError], Optional[LetDeclNode], str, dict]:
    """
    Публичная функция для семантического анализа.
    Возвращает (ошибки, AST, текстовое представление, JSON).
    """
    analyzer = SemanticAnalyzer(tokens)
    errors = analyzer.analyze()
    ast = analyzer.get_ast()
    text_repr = analyzer.get_ast_text()
    json_repr = analyzer.get_ast_json()
    return errors, ast, text_repr, json_repr