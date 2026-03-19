import sqlite3
import os
import sys

# 2. 開發規範與環境: 資料庫檔案統一存放於 Database/test.db
DB_DIR = "Database"
DB_FILE = os.path.join(DB_DIR, "test.db")

# ==============================================================================
# A. 基礎資料維護 (正課基礎)
# ==============================================================================

class DBConnection:
    """
    A1. 資料連接 (dbConnection)
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
        # 設定 row_factory 以便之後可用欄位名稱存取資料 (如 row['name'])
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                # 發生例外，退回這段期間的所有資料庫操作
                self.conn.rollback()
            else:
                # 正常結束，提交操作
                self.conn.commit()
            self.conn.close()

def create_table():
    """
    A2. 表單初始化 (createTable)
    程式啟動時檢查資料表是否存在，不存在則根據規格建立。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        # 3. 資料庫結構規格 (Table: Students)
        # 助教提示：這裡展示了 SQLite 建立資料表的基礎語法，需特別注意 PRIMARY KEY 及 NOT NULL 限制
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
    A3. 新增學生 (insert_student)
    包含重複 Email 檢查與參數化查詢以防止 SQL Injection。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # [進階邏輯] 寫入前需先查詢 email 是否已存在 (因為資料表有限制 UNIQUE，可以事先擋下)
        cursor.execute('SELECT id FROM Students WHERE email = ?', (email,))
        if cursor.fetchone():
            print(f"[錯誤] Email '{email}' 已經被註冊過，請確認後再試！")
            return False
            
        # 使用參數化查詢 (?, ?, ...) 防止 SQL 注入
        cursor.execute('''
            INSERT INTO Students (name, gender, department, email, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, gender, department, email, phone, address))
        print(f"[成功] 學生 {name} ({department}) 已成功新增至系統。")
        return True

def list_all_students():
    """
    A4. 列出全部 (list_all_students)
    從資料庫檢索所有行，並格式化輸出於終端機。
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
    A5. 修改資料 (update_student)
    輸入 id 後，允許修改該生的電話與地址。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # 5. 異常處理: 防呆處理 - 若輸入的 id 不存在，提示錯誤訊息
        cursor.execute('SELECT * FROM Students WHERE id = ?', (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"[錯誤] 找不到 ID 為 {student_id} 的學生。請確認後再試！")
            return
            
        print(f"\n[目前學生] {student['name']} (ID: {student['id']})")
        print(f"原電話: {student['phone']} | 原地址: {student['address'] if student['address'] else '無'}")
        
        # 使用者可以選擇不修改，直接按 Enter
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
    A6. 刪除資料 (delete_student)
    根據 id 刪除特定行，並實作安全機制進行二次確認。
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

# ==============================================================================
# B. 資料統計與搜尋 (實習挑戰)
# ==============================================================================

def count_by_department():
    """
    B1. 系所人數統計
    使用 GROUP BY 與 COUNT(*) 列出各系所現有人數。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        # 助教提示：此處展示 SQL 聚合函數 (Aggregate Functions) 的應用
        cursor.execute('''
            SELECT department, COUNT(*) as student_count 
            FROM Students 
            GROUP BY department
            ORDER BY student_count DESC
        ''')
        records = cursor.fetchall()
        
        if not records:
            print("[提示] 目前沒有任何學生資料。")
            return
            
        print("\n=== 📊 系所人數統計 ===")
        print(f"{'系所名稱':<20} | {'人數':<5}")
        print("-" * 30)
        for r in records:
            print(f"{r['department']:<20} | {r['student_count']:<5}")
        print("-" * 30)

def search_students(keyword):
    """
    B2. 模糊搜尋功能
    在 name 或 address 欄位中使用 LIKE %keyword% 進行比對。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # 助教提示：LIKE 文法需要加上 % 代表任意字元
        pattern = f"%{keyword}%"
        cursor.execute('''
            SELECT id, name, department, address 
            FROM Students 
            WHERE name LIKE ? OR address LIKE ?
        ''', (pattern, pattern))
        records = cursor.fetchall()
        
        if not records:
            print(f"\n[提示] 找不到包含關鍵字 '{keyword}' 的學生。")
            return
            
        print(f"\n=== 🔍 搜尋結果 (關鍵字: '{keyword}') ===")
        for r in records:
            address_text = r['address'] if r['address'] else "未填寫"
            print(f"ID: {r['id']:<3} | 姓名: {r['name']:<10} | 系所: {r['department']:<15} | 地址: {address_text}")

def get_student_detail(student_id):
    """
    B3. 單筆精確查詢
    輸入 id 顯示該生的完整詳細資料。
    """
    with DBConnection(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students WHERE id = ?', (student_id,))
        r = cursor.fetchone()
        
        if not r:
            print(f"[錯誤] 找不到 ID 為 {student_id} 的學生。")
            return
            
        print(f"\n=== 📄 學生詳細資料 (ID: {r['id']}) ===")
        print(f"姓名     : {r['name']}")
        print(f"性別     : {r['gender']}")
        print(f"系所     : {r['department']}")
        print(f"Email    : {r['email']}")
        print(f"電話     : {r['phone']}")
        print(f"地址     : {r['address'] if r['address'] else '未填寫'}")
        print(f"建檔時間 : {r['created_at']}")
        print("==============================")

# ==============================================================================
# UI 輔助函式
# ==============================================================================

def get_int_input(prompt):
    """
    5. 異常處理: 處理非數字輸入的例外
    """
    while True:
        value = input(prompt).strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            print("[格式錯誤] 請輸入有效的數字格式 (例如：1, 2, 3)！")

# ==============================================================================
# 主程式進入點
# ==============================================================================

def main():
    # 執行前初始化資料庫
    create_table()
    
    # 5. 介面與異常處理: 使用 while True 建立主選單介面
    while True:
        print("\n" + "="*50)
        print("🏫 學生學籍管理系統 (v2.0)")
        print("="*50)
        print("【基礎維護】")
        print("  1. 新增學生資料")
        print("  2. 列出所有學生")
        print("  3. 修改學生資料 (電話/地址)")
        print("  4. 刪除學生資料")
        print("【進階功能】")
        print("  5. 系所人數統計")
        print("  6. 關鍵字模糊搜尋 (姓名/地址)")
        print("  7. 查詢單筆詳細資料 (依 ID)")
        print("-" * 50)
        print("  0. 登出並關閉系統")
        print("="*50)
        
        try:
            choice = get_int_input("👉 請選擇功能操作 (0-7): ")
            
            if choice == 0:
                # 退出機制: 迴圈被 break 後程式自然結束。因為每次操作都是新的上下文管理，因此沒有殘留連接
                print("\n[系統] 處理完成，安全斷開連線，感謝使用！ 👋")
                break
                
            elif choice == 1:
                name = input("輸入姓名: ").strip()
                gender = input("輸入性別: ").strip()
                department = input("輸入系所: ").strip()
                email = input("輸入 Email: ").strip()
                phone = input("輸入電話: ").strip()
                address = input("輸入地址 (選填，可直接按 Enter): ").strip()
                
                # 必填防呆
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
                    
            elif choice == 5:
                count_by_department()
                
            elif choice == 6:
                kw = input("請輸入搜尋關鍵字: ").strip()
                if kw:
                    search_students(kw)
                else:
                    print("[錯誤] 關鍵字不可為空白！")
                    
            elif choice == 7:
                sid = get_int_input("請輸入要查詢的學生 ID: ")
                if sid is not None:
                    get_student_detail(sid)
                    
            else:
                print("\n[錯誤] 無效的選項，請輸入 0-7 之間的數字！")
                
        except KeyboardInterrupt:
            # 處理使用者按下 Ctrl+C 的情況
            print("\n\n[系統] 偵測到強制中斷指令，系統安全關閉中... 👋")
            sys.exit(0)
        except Exception as e:
            # 防呆：避免未預期中斷
            print(f"\n[系統錯誤] 發生未預期的例外：{e}")

if __name__ == "__main__":
    main()
