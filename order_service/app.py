"""
order_service - 订单微服务
端口: 5003
API:
  - GET /api/orders : 获取订单列表（需要有效 JWT token）
  - GET /api/health : 健康检查
"""

import os
import jwt
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# ======================== 配置 ========================
JWT_SECRET = "mysecretkey"

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


# ======================== JWT 校验 ========================
def verify_token(token):
    """校验 JWT token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_token_from_header():
    """从请求头中提取 Bearer token"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return ""


# ======================== API ========================
@app.route("/api/orders", methods=["GET"],strict_slashes=False)
def get_orders():
    """
    获取订单列表（需要有效 token）
    请求头: Authorization: Bearer <token>
    返回:   {"code": 200, "data": [...], "total": N}
    """
    # ---- JWT 校验 ----
    token = get_token_from_header()
    payload = verify_token(token)
    if payload is None:
        return jsonify({"code": 401, "message": "token 无效或已过期，请重新登录"}), 401

    user_id = payload.get("user_id")

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.id, o.user_id, u.username, o.product_id, p.name AS product_name,
                   o.quantity, o.total_price, o.status, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
            """,
            (user_id,),
        )
        orders = cursor.fetchall()
        cursor.close()
        conn.close()

        # 将 Decimal 转换为 float（JSON 序列化需要）
        for order in orders:
            order["total_price"] = float(order["total_price"])

        return jsonify({
            "code": 200,
            "data": orders,
            "total": len(orders),
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"数据库错误: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """健康检查接口"""
    return jsonify({"status": "ok", "service": "order_service"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)