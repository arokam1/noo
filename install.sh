#!/data/data/com.termux/files/usr/bin/bash
# ============================================
#  نصب خودکار مدیریت بوکمارک‌ها — Termux
#  اجرا: bash install.sh
# ============================================

echo "================================"
echo "  📚 نصب‌کننده مدیریت بوکمارک‌ها"
echo "================================"

echo "[1/4] آپدیت پکیج‌ها..."
pkg update -y || echo "⚠️ آپدیت ناموفق بود، ادامه می‌دهیم..."

echo "[2/4] نصب پایتون..."
command -v python >/dev/null 2>&1 || pkg install python -y
echo "✅ پایتون: $(python --version 2>&1)"

echo "[3/4] نصب Flask..."
pip install --upgrade pip -q
pip install flask -q
if [ $? -ne 0 ]; then
    echo "❌ نصب Flask ناموفق بود. دستی اجرا کن: pip install flask"
    exit 1
fi
echo "✅ Flask نصب شد"

echo "[4/4] بررسی فایل app.py..."
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/app.py" ]; then
    echo "✅ app.py پیدا شد: $DIR"
else
    echo "⚠️ app.py در این پوشه نیست!"
    exit 1
fi

cat > "$DIR/bm" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
echo "📚 در حال اجرا... (توقف: Volume Down + C)"
python app.py
EOF
chmod +x "$DIR/bm"

echo ""
echo "================================"
echo "  ✅ نصب کامل شد!"
echo "================================"
echo "برای اجرا بنویس:  ./bm"
echo "سپس در مرورگر:    http://127.0.0.1:5000"
