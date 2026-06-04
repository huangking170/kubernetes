"""
auth_service - 用户认证微服务
端口: 5001
API:
  - POST /api/auth/login    : 用户登录，返回 JWT token
  - POST /api/auth/verify   : 校验 JWT token 有效性
"""

import hashlib
from datetime import datetime, timedelta

import jwt
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# ======================== 配置 ========================
JWT_SECRET = "mysecretkey"
JWT_EXPIRY_HOURS = 1

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


# ======================== 工具函数 ========================
def generate_token(user_id, username):
    """生成 JWT token，有效期 1 小时"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def verify_token(token):
    """校验 JWT token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # token 已过期
    except jwt.InvalidTokenError:
        return None  # token 无效


# ======================== API ========================
@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    用户登录接口
    请求体: {"username": "...", "password": "..."}
    返回:   {"code": 200, "token": "...", "message": "登录成功"}
    """
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"code": 400, "message": "用户名和密码不能为空"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = %s AND password = %s",
            (username, password),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({"code": 500, "message": f"数据库错误: {str(e)}"}), 500

    if not user:
        return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

    token = generate_token(user["id"], user["username"])
    return jsonify({"code": 200, "token": token, "message": "登录成功"})


@app.route("/api/auth/verify", methods=["POST"])
def verify():
    """
    校验 token 接口
    请求体: {"token": "..."}
    返回:   {"code": 200, "valid": true, ...} 或 {"code": 401, "valid": false, ...}
    """
    data = request.get_json(force=True)
    token = data.get("token", "")

    if not token:
        return jsonify({"code": 400, "valid": False, "message": "token 不能为空"}), 400

    payload = verify_token(token)
    if payload is None:
        return jsonify({"code": 401, "valid": False, "message": "token 无效或已过期"}), 401

    return jsonify({
        "code": 200,
        "valid": True,
        "user_id": payload["user_id"],
        "username": payload["username"],
        "message": "token 有效",
    })


@app.route("/api/auth/health", methods=["GET"])
def health():
    """健康检查接口"""
    return jsonify({"status": "ok", "service": "auth_service"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)