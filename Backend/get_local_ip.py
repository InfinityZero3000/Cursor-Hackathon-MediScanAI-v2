"""
Script để lấy IP local của máy tính
Sử dụng để kết nối mobile vào backend local
"""
import socket

def get_local_ip():
    """Lấy IP local của máy tính"""
    try:
        # Kết nối tạm thời để lấy IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"⚠️ Không thể lấy IP: {e}")
        return None

if __name__ == '__main__':
    ip = get_local_ip()
    if ip:
        print("=" * 50)
        print("📱 Kết nối Mobile vào Backend Local")
        print("=" * 50)
        print(f"\n✅ IP Local của bạn: {ip}")
        print(f"\n🔗 URL Backend: http://{ip}:5000")
        print(f"\n📋 Các bước:")
        print(f"   1. Đảm bảo mobile và máy tính cùng WiFi")
        print(f"   2. Trên mobile, mở trình duyệt và truy cập:")
        print(f"      http://{ip}:5000/api/health")
        print(f"   3. Nếu thấy JSON response, đã kết nối thành công!")
        print(f"\n💡 Hoặc cấu hình trong Web/src/utils/api.js:")
        print(f'   const API_URL = "http://{ip}:5000/api";')
        print("=" * 50)
    else:
        print("❌ Không thể lấy IP local")

