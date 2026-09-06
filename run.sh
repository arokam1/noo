#!/data/data/com.termux/files/usr/bin/bash
# اجرای برنامه — bash run.sh
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
if [ ! -f "app.py" ]; then echo "❌ app.py پیدا نشد"; exit 1; fi
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask نصب نیست. اول اجرا کن: bash install.sh"
    exit 1
fi
echo "📚 اجرا شد → مرورگر: http://127.0.0.1:5000"
python app.py
