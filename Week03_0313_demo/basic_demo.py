import sqlite3
import os
import sys

# 資料庫檔案統一存放於 Database/test.db
DB_DIR = "Database"
DB_FILE = os.path.join(DB_DIR, "test.db")

class DBConnection:
    """
    資料連接 (dbConnection)
    實作上下文管理的資料庫連接函式。
    進入時會自動連接資料庫，離開時會自動 commit 或在發生錯誤時 rollback，並關閉連接。
    """
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        # 確保資料庫目錄存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        # 設定 row_factory 以便之後可用欄位名稱存取資料
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()

def create_table():
    """
    表單初始化 (createTable)
    程式啟動時檢查資料表是否存在，不存在則建立。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                address TEXT
            )
        ''')

def insert_student(name, gender, department, email, phone, address):
    """
    新增 (Insert)：輸入完整資料並正確儲存
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # 檢查 email 是否重複
        cursor.execute('SELECT id FROM Students WHERE email = ?', (email,))
        if cursor.fetchone():
            print(f"[錯誤] Email '{email}' 已經被註冊過，請確認後再試！")
            return False
            
        cursor.execute('''
            INSERT INTO Students (name, gender, department, email, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, gender, department, email, phone, address))
        print(f"[成功] 學生 {name} ({department}) 已成功新增至系統。")
        return True

def list_all_students():
    """
    列表 (Select All)：列出資料庫所有紀錄
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students')
        records = cursor.fetchall()
        
        if not records:
            print("[提示] 資料庫中目前沒有任何學生資料。")
            return
            
        print("\n=== 👨‍🎓 學生資料列表 ===")
        print(f"{'ID':<5} | {'姓名':<10} | {'性別':<4} | {'系所':<15} | {'Email':<25} | {'電話':<12}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<5} | {r['name']:<10} | {r['gender']:<4} | {r['department']:<15} | {r['email']:<25} | {r['phone']:<12}")
        print("-" * 80)

def update_student(student_id):
    """
    修改 (Update)：根據 id 修改電話或地址
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"[錯誤] 找不到 ID 為 {student_id} 的學生。請確認後再試！")
            return
            
        print(f"\n[目前學生] {student['name']} (ID: {student['id']})")
        print(f"原電話: {student['phone']} | 原地址: {student['address'] if student['address'] else '無'}")
        
        new_phone = input("請輸入新電話 (若不修改請直接按 Enter): ").strip()
        new_address = input("請輸入新地址 (若不修改請直接按 Enter): ").strip()
        
        final_phone = new_phone if new_phone else student['phone']
        final_address = new_address if new_address else student['address']
        
        cursor.execute('''
            UPDATE Students 
            SET phone = ?, address = ?
            WHERE id = ?
        ''', (final_phone, final_address, student_id))
        print(f"[成功] 已成功更新學號 {student_id} 的聯絡資訊。")

def delete_student(student_id):
    """
    刪除 (Delete)：根據 id 移除資料，並具備二次確認 (Y/N) 邏輯
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM Students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"[錯誤] 找不到 ID 為 {student_id} 的學生。")
            return
            
        # 安全機制：二次確認
        confirm = input(f"[警告] 您確定要刪除學生 '{student['name']}' 的資料嗎？(Y/N): ").strip().upper()
        if confirm == 'Y':
            cursor.execute('DELETE FROM Students WHERE id = ?', (student_id,))
            print(f"[成功] 已刪除學生 ID: {student_id} 的資料。")
        else:
            print("[提示] 操作已取消。")

def get_int_input(prompt):
    """
    處理非數字輸入的例外
    """
    while True:
        value = input(prompt).strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("[格式錯誤] 請輸入有效的數字格式 (例如：1, 2, 3)！")

def main():
    # 執行前初始化資料庫
    create_table()
    
    while True:
        print("\n" + "="*50)
        print("🏫 學生學籍管理系統 (基礎版 - 星期一進度)")
        print("="*50)
        print("  1. 新增學生資料 (Insert)")
        print("  2. 列出所有紀錄 (Select All)")
        print("  3. 修改學生資料 (Update)")
        print("  4. 刪除學生資料 (Delete)")
        print("-" * 50)
        print("  0. 登出並關閉系統")
        print("="*50)
        
        try:
            choice = get_int_input("👉 請選擇功能操作 (0-4): ")
            
            if choice == 0:
                print("\n[系統] 處理完成，安全斷開連線，感謝使用！ 👋")
                break
                
            elif choice == 1:
                name = input("輸入姓名: ").strip()
                gender = input("輸入性別: ").strip()
                department = input("輸入系所: ").strip()
                email = input("輸入 Email: ").strip()
                phone = input("輸入電話: ").strip()
                address = input("輸入地址 (選填，可直接按 Enter): ").strip()
                
                if not all([name, gender, department, email, phone]):
                    print("\n[錯誤] 姓名、性別、系所、Email 與電話均為必填，請重新操作！")
                else:
                    insert_student(name, gender, department, email, phone, address)
                    
            elif choice == 2:
                list_all_students()
                
            elif choice == 3:
                sid = get_int_input("請輸入學生的 ID: ")
                if sid is not None:
                    update_student(sid)
                    
            elif choice == 4:
                sid = get_int_input("請輸入要刪除的學生 ID: ")
                if sid is not None:
                    delete_student(sid)
                    
            else:
                print("\n[錯誤] 無效的選項，請輸入 0-4 之間的數字！")
                
        except KeyboardInterrupt:
            print("\n\n[系統] 偵測到強制中斷指令，系統安全關閉中... 👋")
            sys.exit(0)
        except Exception as e:
            print(f"\n[系統錯誤] 發生未預期的例外：{e}")

if __name__ == "__main__":
    main()
