#!/usr/bin/env python3
"""Тест арифметического анализатора с новой версией."""
import sys
sys.path.insert(0, '.')
from src.core.arithmetic_parser import parse_arithmetic, evaluate_poliz

def test_expression(expr):
    print(f"\nВыражение: '{expr}'")
    success, errors, quads, poliz, has_id = parse_arithmetic(expr)
    print(f"  Успех: {success}")
    if errors:
        print(f"  Ошибки:")
        for err in errors:
            print(f"    [{err.line}:{err.column}] {err.message} ({err.fragment})")
    else:
        print(f"  Ошибок нет")
    if quads:
        print(f"  Тетрады:")
        for q in quads:
            print(f"    ({q.op}, {q.arg1}, {q.arg2}, {q.result})")
    if poliz:
        print(f"  ПОЛИЗ: {' '.join(poliz)}")
        if not has_id:
            value = evaluate_poliz(poliz)
            if value is not None:
                print(f"  Значение: {value}")
            else:
                print(f"  Ошибка вычисления (деление на ноль или другая)")
    print(f"  Есть идентификаторы: {has_id}")

if __name__ == "__main__":
    test_expression("2 + 3 * 4")
    test_expression("(2 + 3) * 4")
    test_expression("a + b")
    test_expression("2 + ")
    test_expression("2 + * 3")
    test_expression("2 + 3 % 2")
    test_expression("2 + 3 / 0")
    test_expression("2 + 3.5")
    test_expression("2 + 3 * (4 - 1)")
    test_expression("10 / 3")
    test_expression("10 % 3")