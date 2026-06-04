"""
product_service - 商品微服务
端口: 5002
API:
  - GET /api/products : 获取商品列表（无需 token）
  - GET /api/health   : 健康检查
"""

import os
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# ======================== 配置 ========================
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"), # 找不到环境变量时，默认连本地 localhost
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "123456"),
    "database": os.environ.get("DB_NAME", "ecommerce"),
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