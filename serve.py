from waitress import serve
from app import app

if __name__ == '__main__':
    print("بدء تشغيل الخادم على العنوان http://0.0.0.0:5000")
    serve(app, host='0.0.0.0', port=5000)