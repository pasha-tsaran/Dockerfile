"""Flask API для тестирования Docker и простых вычислений."""

import math
import socket

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["MAX_CONTENT_LENGTH"] = 4096


@app.get("/")
def index():
    return jsonify(message="Приложение работает!", hostname=socket.gethostname())


@app.get("/health")
@app.get("/api/health")
def health():
    return jsonify(status="ok", hostname=socket.gethostname())


@app.post("/api/calculate")
def calculate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Передайте JSON-объект с полями a, b и operation."), 400
    operation = data.get("operation")
    if operation not in ("add", "subtract"):
        return jsonify(error="Операция должна быть add или subtract."), 400
    numbers = []
    for field in ("a", "b"):
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return jsonify(error=f"Поле {field} должно быть числом."), 400
        try:
            number = float(value)
        except OverflowError:
            return jsonify(error=f"Число {field} слишком большое."), 400
        if not math.isfinite(number):
            return jsonify(error=f"Поле {field} должно быть конечным числом."), 400
        numbers.append(number)
    a, b = numbers
    result = a + b if operation == "add" else a - b
    if not math.isfinite(result):
        return jsonify(error="Результат слишком большой."), 400
    return jsonify(a=a, b=b, operation=operation, result=result,
                   hostname=socket.gethostname())


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="Маршрут не найден."), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="Метод запроса не поддерживается."), 405


@app.errorhandler(413)
def too_large(error):
    return jsonify(error="Тело запроса слишком большое."), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
