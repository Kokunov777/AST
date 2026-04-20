#!/usr/bin/env python3
"""
Тестирование семантического анализатора на примере объявления комплексного числа.
"""
import sys
sys.path.insert(0, '.')

from src.core.analyzer import scan_rust
from src.core.semantic_analyzer import analyze_semantics

def test_example():
    code = "let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
    print("Исходный код:", code)
    
    tokens, lex_errors = scan_rust(code)
    print(f"Лексем: {len(tokens)}, лексических ошибок: {len(lex_errors)}")
    
    semantic_errors, ast, ast_text, ast_json = analyze_semantics(tokens)
    print(f"Семантических ошибок: {len(semantic_errors)}")
    for err in semantic_errors:
        print(f"  Строка {err.line}:{err.column} - {err.message}")
    
    if ast:
        print("\nТекстовое представление AST:")
        print(ast_text)
        
        print("\nJSON представление AST:")
        import json
        print(json.dumps(ast_json, indent=2, ensure_ascii=False))
    else:
        print("AST не построено.")

def test_error_cases():
    print("\n--- Тест с повторным объявлением ---")
    code = "let x = num::complex::Complex::new(1.0, 2.0);\nlet x = num::complex::Complex::new(3.0, 4.0);"
    tokens, _ = scan_rust(code)
    semantic_errors, _, _, _ = analyze_semantics(tokens)
    print(f"Ошибки: {len(semantic_errors)}")
    for err in semantic_errors:
        print(f"  {err.message}")
    
    print("\n--- Тест с недопустимым путем ---")
    code = "let y = wrong::path::new(1.0, 2.0);"
    tokens, _ = scan_rust(code)
    semantic_errors, _, _, _ = analyze_semantics(tokens)
    print(f"Ошибки: {len(semantic_errors)}")
    for err in semantic_errors:
        print(f"  {err.message}")
    
    print("\n--- Тест с большим числом ---")
    code = "let z = num::complex::Complex::new(1e400, 2.0);"
    tokens, _ = scan_rust(code)
    semantic_errors, _, _, _ = analyze_semantics(tokens)
    print(f"Ошибки: {len(semantic_errors)}")
    for err in semantic_errors:
        print(f"  {err.message}")

if __name__ == "__main__":
    test_example()
    test_error_cases()