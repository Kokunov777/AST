"""
Графическая визуализация AST с использованием QGraphicsScene.
"""
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QFont, QPen, QColor, QPainter
from typing import Optional
from ..core.ast import ASTNode, LetDeclNode, CallExprNode, PathNode, IntLiteralNode, FloatLiteralNode, UnaryExprNode, NodeType

# Цвета для различных типов узлов
NODE_COLORS = {
    NodeType.LET_DECL: QColor(255, 255, 200),   # светло-жёлтый
    NodeType.CALL_EXPR: QColor(200, 255, 200),  # светло-зелёный
    NodeType.PATH: QColor(200, 200, 255),       # светло-синий
    NodeType.INT_LITERAL: QColor(255, 200, 200), # светло-красный
    NodeType.FLOAT_LITERAL: QColor(255, 200, 255), # светло-пурпурный
    NodeType.UNARY_EXPR: QColor(255, 220, 200), # светло-оранжевый
    NodeType.BINARY_EXPR: QColor(200, 255, 255), # светло-голубой
}


class ASTGraphicsNode(QGraphicsRectItem):
    """Графический узел AST."""
    def __init__(self, node: ASTNode, x: float, y: float, width: float = 150, height: float = 60):
        super().__init__(0, 0, width, height)
        self.node = node
        self.setPos(x, y)
        
        # Отладочная информация о типе узла
        print(f"Тип узла: {node.node_type}, тип данных: {type(node.node_type)}")
        
        # Цвет фона в зависимости от типа узла
        bg_color = NODE_COLORS.get(node.node_type, QColor(255, 255, 200))
        self.setBrush(bg_color)
        self.setPen(QPen(Qt.red, 3))  # красный контур
        
        # Текст типа узла
        node_type_text = node.node_type.value if node.node_type else "UNKNOWN"
        print(f"Создаём узел {node_type_text} на ({x}, {y})")
        text = QGraphicsTextItem(node_type_text, self)
        text.setDefaultTextColor(Qt.blue)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        if font.exactMatch():
            text.setFont(font)
        else:
            text.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        text_rect = text.boundingRect()
        print(f"  ширина текста: {text_rect.width()}, высота: {text_rect.height()}")
        text.setPos(width / 2 - text_rect.width() / 2, 8)
        
        # Дополнительная информация (имя, значение)
        if isinstance(node, LetDeclNode):
            info = f"name: {node.name}"
        elif isinstance(node, CallExprNode):
            info = f"call"
        elif isinstance(node, PathNode):
            info = f"segments: {node.segments}"
        elif isinstance(node, IntLiteralNode):
            info = f"value: {node.value}"
        elif isinstance(node, FloatLiteralNode):
            info = f"value: {node.value}"
        elif isinstance(node, UnaryExprNode):
            info = f"op: {node.operator}"
        else:
            info = ""
        
        if info:
            detail = QGraphicsTextItem(info, self)
            detail.setDefaultTextColor(Qt.darkMagenta)
            detail.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            detail.setPos(width / 2 - detail.boundingRect().width() / 2, 30)


class ASTGraphicsView(QGraphicsView):
    """Виджет для отображения AST."""
    def __init__(self, ast: Optional[ASTNode] = None):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QColor(245, 245, 245))
        self.setSceneRect(-100, -100, 2000, 2000)
        self.setViewportUpdateMode(self.ViewportUpdateMode.FullViewportUpdate)
        
        if ast:
            self.draw_ast(ast)
    
    def draw_ast(self, ast: ASTNode):
        """Рекурсивно отрисовать AST."""
        self.scene.clear()
        if not ast:
            print("AST пустой, нечего рисовать")
            return
        
        # Временный стиль для отладки видимости
        self.setStyleSheet("border: 5px solid red; background-color: lightblue;")
        
        # Явно задаём позицию корня
        root_x = 500  # центр по X
        root_y = 50   # отступ сверху
        print(f"Рисуем корень AST в ({root_x}, {root_y})")
        
        # Расположение узлов в виде дерева
        self._layout_node(ast, root_x, root_y, 0)
        
        # После построения устанавливаем сцену с отступами
        rect = self.scene.itemsBoundingRect()
        print(f"Bounding rect сцены: {rect}")
        if rect.width() > 0 and rect.height() > 0:
            self.setSceneRect(rect.adjusted(-200, -200, 200, 200))
            # Центрируем вид на середине дерева
            self.centerOn(rect.center())
            # Сброс масштабирования (убедимся, что текст не слишком мал)
            self.resetTransform()
            # Принудительное обновление сцены и вида
            self.scene.update()
            self.viewport().update()
            # Дополнительные вызовы для гарантии отрисовки
            self.show()
            self.raise_()
            self.repaint()
            self.scene.invalidate()
            print("Сцена установлена, вид центрирован, трансформация сброшена, обновление вызвано")
    
    def _layout_node(self, node: ASTNode, x: float, y: float, level: int) -> ASTGraphicsNode:
        """Создать графический узел и расположить дочерние узлы."""
        node_width = 150
        node_height = 60
        horizontal_spacing = 100
        vertical_spacing = 120
        
        print(f"Рисую узел: {node.node_type} at ({x}, {y}), size={node_width}x{node_height}, level={level}")
        
        gnode = ASTGraphicsNode(node, x, y, node_width, node_height)
        self.scene.addItem(gnode)
        
        # Определяем дочерние узлы
        children = []
        if isinstance(node, LetDeclNode) and node.value:
            children.append(node.value)
        elif isinstance(node, CallExprNode):
            children.append(node.callee)
            children.extend(node.arguments)
        elif isinstance(node, UnaryExprNode) and node.operand:
            children.append(node.operand)
        # PathNode, IntLiteralNode, FloatLiteralNode не имеют дочерних
        
        print(f"  дочерних узлов: {len(children)}")
        
        if not children:
            return gnode
        
        # Распределяем дочерние узлы по горизонтали
        total_width = len(children) * node_width + (len(children) - 1) * horizontal_spacing
        start_x = x - total_width / 2 + node_width / 2
        
        for i, child in enumerate(children):
            child_x = start_x + i * (node_width + horizontal_spacing)
            child_y = y + vertical_spacing
            child_gnode = self._layout_node(child, child_x, child_y, level + 1)
            
            # Линия от родителя к ребенку
            line = QGraphicsLineItem(
                x + node_width / 2, y + node_height,
                child_x + node_width / 2, child_y
            )
            line.setPen(QPen(Qt.darkGray, 2, Qt.PenStyle.SolidLine))
            line.setZValue(-1)  # под узлами
            self.scene.addItem(line)
        
        return gnode


class ASTVisualizerDialog(QDialog):
    """Диалоговое окно для визуализации AST."""
    def __init__(self, ast: Optional[ASTNode] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Визуализация AST")
        self.resize(1000, 700)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Абстрактное синтаксическое дерево (AST)")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Графическое представление
        self.view = ASTGraphicsView(ast)
        self.view.setVisible(True)  # явно
        layout.addWidget(self.view)
        
        # Отладочная информация
        print(f"View visible: {self.view.isVisible()}")
        scene = self.view.scene  # атрибут, который мы создали
        print(f"View scene: {scene}")
        if scene:
            print(f"Scene items: {len(scene.items())}")
        else:
            print("Scene is None")
        
        # Кнопки
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


def show_ast_graphics(ast: Optional[ASTNode], parent=None):
    """Показать диалог с графической визуализацией AST."""
    dialog = ASTVisualizerDialog(ast, parent)
    dialog.exec()