#!/usr/bin/env python3
"""
Тест графической визуализации AST.
"""
import sys
sys.path.insert(0, '.')

from src.core.analyzer import scan_rust
from src.core.semantic_analyzer import analyze_semantics
from src.ui.ast_graphics import show_ast_graphics
from PySide6.QtWidgets import QApplication

def test():
    code = "let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
    tokens, _ = scan_rust(code)
    _, ast, _, _ = analyze_semantics(tokens)
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Показать диалог
    from src.ui.ast_graphics import ASTVisualizerDialog
    dialog = ASTVisualizerDialog(ast)
    dialog.show()
    
    # Закрыть через 3 секунды
    from PySide6.QtCore import QTimer
    QTimer.singleShot(3000, dialog.close)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test()