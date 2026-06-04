"""
product_service - 商品微服务
端口: 5002
API:
  - GET /api/products : 获取商品列表（无需 token）
  - GET /api/health   : 健康检查
"""

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# ======================== 配置 ========================
DB_CONFIG = {
    "host": "192.168.10.240",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "ecommerce",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


# ======================== 数据库工具 ========================
def get_db():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


# ======================== API ========================
@app.route("/api/products", methods=["GET"],strict_slashes=False)
def get_products():
    """
    获取商品列表（公开接口，无需 token）
    返回: {"code": 200, "data": [...], "total": N}
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products ORDER BY id")
        products = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            "code": 200,
            "data": products,
            "total": len(products),
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"数据库错误: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """健康检查接口"""
    return jsonify({"status": "ok", "service": "product_service"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)