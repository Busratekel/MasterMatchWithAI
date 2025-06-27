from main import app, db

def update_log_table():
    with app.app_context():
        try:
            # Yeni sütunu ekle
            db.engine.execute("ALTER TABLE kullanici_log ADD vki_sayisal VARCHAR(10)")
            print("✅ vki_sayisal sütunu başarıyla eklendi!")
        except Exception as e:
            print(f"❌ Hata: {e}")
            print("Sütun zaten mevcut olabilir.")

if __name__ == "__main__":
    update_log_table() 