import flet as ft
import sqlite3

MUNICIPALITIES = [
    "تيسمسيلت", "أولاد بسام", "خميستي", "العيون", "ثنية الحد",
    "سيدي بوتشنت", "لرجام", "ملعب", "سيدي عابد", "تملاحت",
    "برج بونعامة", "بني شعيب", "بني لحسن", "سيدي سليمان",
    "عماري", "معصم", "الأزهرية", "بوقايد", "الأربعاء",
    "برج الأمير عبد القادر", "اليوسفية", "سيدي العنتري"
]

# اسم ملف قاعدة البيانات المحلية التي ستنشأ تلقائياً في الهاتف
DB_NAME = "supporters.db"

# دالة تهيئة قاعدة البيانات وإنشاء الجدول
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS supporters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            municipality TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# دالة جلب البيانات من قاعدة البيانات
def load_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, municipality FROM supporters")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "mun": row[2]} for row in rows]

# دالة إضافة مؤيد جديد
def save_data(name, mun):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO supporters (name, municipality) VALUES (?, ?)", (name, mun))
    conn.commit()
    conn.close()

# دالة حذف مؤيد 
def delete_voter_from_db(voter_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM supporters WHERE id = ?", (voter_id,))
    conn.commit()
    conn.close()


def main(page: ft.Page):
    page.title = "دعم ساعد ولد قدور"
    page.rtl = True
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # إنشاء وتجهيز قاعدة البيانات عند التشغيل
    init_db()

    name_field = ft.TextField(
        label="الاسم واللقب",
        width=350
    )

    municipality = ft.Dropdown(
        label="البلدية",
        width=350,
        options=[ft.dropdown.Option(x) for x in MUNICIPALITIES]
    )

    stats = ft.Column()
    voters = ft.Column(width=400)

    def show_message(text):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text)
        )
        page.snack_bar.open = True
        page.update()

    def delete_voter(voter_id):
        try:
            delete_voter_from_db(voter_id)
            refresh()
            show_message("تم الحذف بنجاح")
        except Exception as e:
            show_message(f"خطأ أثناء الحذف: {e}")

    def add_voter(e):
        if not name_field.value:
            show_message("أدخل الاسم واللقب")
            return

        if not municipality.value:
            show_message("اختر البلدية")
            return

        try:
            save_data(name_field.value, municipality.value)
            
            name_field.value = ""
            municipality.value = None

            refresh()
            show_message("تمت الإضافة بنجاح")
        except Exception as e:
            show_message(f"خطأ أثناء الحفظ: {e}")

    def refresh():
        try:
            data = load_data()
        except Exception as e:
            data = []
            print(f"Error: {e}")

        stats.controls.clear()
        voters.controls.clear()

        stats.controls.append(
            ft.Text(
                f"إجمالي المؤيدين: {len(data)}",
                size=20,
                weight=ft.FontWeight.BOLD
            )
        )

        count = {}
        for item in data:
            mun = item["mun"]
            count[mun] = count.get(mun, 0) + 1

        for mun, total in count.items():
            stats.controls.append(
                ft.Text(f"{mun}: {total}")
            )

        for item in reversed(data):
            voters.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    f"{item['name']} - {item['mun']}",
                                    expand=True
                                ),
                                ft.IconButton(
                                    icon="delete",  # التعديل: استخدام الكلمة النصية
                                    icon_color="red",
                                    on_click=lambda e, idx=item['id']: delete_voter(idx)
                                )
                            ]
                        )
                    )
                )
            )

        page.update()

    page.add(
        ft.Text(
            "دعم ساعد ولد قدور",
            size=24,
            weight=ft.FontWeight.BOLD
        ),

        ft.Image(
            src="logo.png",  
            width=160,
            height=160,
            fit=ft.BoxFit.CONTAIN,
            border_radius=10
        ),

        ft.Divider(),

        name_field,
        municipality,

        ft.ElevatedButton(
            "إضافة مؤيد",
            icon="add",  # التعديل: استخدام الكلمة النصية
            width=350,
            on_click=add_voter
        ),

        ft.Divider(),

        stats,

        ft.Divider(),

        ft.Text(
            "قائمة المؤيدين",
            size=18,
            weight=ft.FontWeight.BOLD
        ),

        voters,

        ft.Divider(),

        ft.Text(
            "تم التطوير من طرف الأستاذ: بارد رابح والأستاذ: غبال محمد",
            size=12
        ),

        ft.Text(
            "اللهم ارحم والدي واغفر لهما كما ربياني صغيراً",
            size=12
        )
    )

    refresh()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")