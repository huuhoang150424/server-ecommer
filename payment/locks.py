from django_redis import get_redis_connection
from django.utils import timezone
from order.models import orderModel, orderDetailModel
from product.models import ProductModel
from .models import PaymentMethod,PaymentStatus
import uuid
import time
import json
import time
from redis import Redis



def lock_product(product_id):
    redis_conn = get_redis_connection("default")
    if not redis_conn:
        raise Exception("Không thể kết nối đến Redis.")
    print(f"Đang khóa sản phẩm với ID: {product_id}")
    lock_key = f"lock:product:{str(product_id)}" 
    lock = redis_conn.lock(lock_key, timeout=10)  # Khóa tồn tại 10 giây
    return lock


# Thêm đơn hàng vào hàng đợi Redis
def add_order_to_queue(order_data):
    order_data['order_id'] = str(order_data['order_id'])  
    redis_conn = get_redis_connection("default")
    redis_conn.rpush("order_queue", json.dumps(order_data)) 

def process_order_queue():
    redis_conn = get_redis_connection("default")
    while True:
        order_data = redis_conn.lpop("order_queue")  # Lấy đơn hàng đầu tiên trong hàng đợi
        if order_data:
            # Xử lý đơn hàng
            process_order(order_data)
        else:
            time.sleep(5)  # Chờ 5 giây trước khi kiểm tra lại hàng đợi

# Xử lý đơn hàng từ hàng đợi
def process_order(order_data):
    order_id = order_data.get("order_id")
    order = orderModel.objects.get(id=order_id)
    order.payment_status = PaymentStatus.PENDING
    order.save()
    print(f"Processing order: {order_id}")
    PaymentModel.objects.create(
        order=order,
        payment_method="MOMO",
        payment_status=PaymentStatus.PENDING,
        transaction_id=str(uuid.uuid4())  
    )
    order.payment_status = PaymentStatus.COMPLETED
    order.save()


