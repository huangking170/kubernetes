import requests

# 1. 登录获取 token
login_url = "http://localhost:5001/api/auth/login"
login_resp = requests.post(login_url, json={"username": "admin", "password": "admin123"})
if login_resp.status_code != 200:
    print("❌ 登录失败:", login_resp.text)
    exit()
token = login_resp.json()["token"]
print("✅ 登录成功，token:", token[:50] + "...\n")

# 2. 测试商品接口（无需 token）
products_url = "http://localhost:5002/api/products"
products_resp = requests.get(products_url)
print("📦 商品服务 (product_service)")
if products_resp.status_code == 200:
    products = products_resp.json().get("data", [])
    for p in products:
        print(f"   - {p['name']}  ¥{p['price']}")
else:
    print(f"   ❌ 状态码 {products_resp.status_code}: {products_resp.text}")

print()

# 3. 测试订单接口（需要 token）
orders_url = "http://localhost:5003/api/orders"
headers = {"Authorization": f"Bearer {token}"}
orders_resp = requests.get(orders_url, headers=headers)
print("📋 订单服务 (order_service)")
if orders_resp.status_code == 200:
    orders = orders_resp.json().get("data", [])
    for o in orders:
        print(f"   - 订单#{o['id']} 用户{o['user_id']} 状态:{o['status']} 金额:{o['total_price']}")
elif orders_resp.status_code == 401:
    print("   ❌ Token 无效或过期")
else:
    print(f"   ❌ 状态码 {orders_resp.status_code}: {orders_resp.text}")