import tkinter as tk
from tkinter import ttk
import psycopg2


class Main:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("900x500")
        self.root.title("Записная книжка")
        self.conn = psycopg2.connect(database="neto_db", user="postgres", password="Kirill123!")
        self.create_db()
        self.inter()
        self.table_info()
        self.root.mainloop()

    # Создание таблицы в базе данных
    def create_db(self):
        with self.conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS phonebook(
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        surname VARCHAR(50) NOT NULL,
                        email VARCHAR(50) NOT NULL,
                        phone VARCHAR(50));""")
            self.conn.commit()

    # Заполнение таблицы tree
    def table_info(self):
        self.tree.delete(*self.tree.get_children())
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, surname, email, phone FROM phonebook")
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    self.tree.insert("", "end", values=row)

    # Информация по выбраной строке
    def label_text_info(self, event):
        try:
            self.label_text.delete(0, tk.END)
            info = self.tree.item(self.tree.focus())["values"]
            self.label_text.insert(tk.END, f"ID: {info[0]}")
            self.label_text.insert(tk.END, f"Имя: {info[1]}")
            self.label_text.insert(tk.END, f"Фамилия: {info[2]}")
            self.label_text.insert(tk.END, f"Email: {info[3]}")
            phones = str(info[4]).split(",")
            if len(phones) == 1:
                self.label_text.insert(tk.END, f"Телефон: {info[4]}")
            else:
                for i in phones:
                    self.label_text.insert(tk.END, f"Телефон {phones.index(i) + 1}: {i}")
        except IndexError:
            pass

    # Интерфейс
    def inter(self):
        self.entry_name = tk.Entry(self.root)
        self.entry_name.grid(row=1, column=0, padx=5, pady=5)
        self.entry_surname = tk.Entry(self.root)
        self.entry_surname.grid(row=1, column=1, padx=5, pady=5)
        self.entry_email = tk.Entry(self.root)
        self.entry_email.grid(row=1, column=2, padx=5, pady=5)
        self.entry_phone = tk.Text(self.root, width=20, height=3)
        self.entry_phone.grid(row=1, column=3, rowspan=2, padx=5, pady=5)

        self.label_name = tk.Label(self.root, text="Имя*")
        self.label_name.grid(row=0, column=0)
        self.label_surname = tk.Label(self.root, text="Фамилия*")
        self.label_surname.grid(row=0, column=1)
        self.label_email = tk.Label(self.root, text="Email")
        self.label_email.grid(row=0, column=2)
        self.label_phone = tk.Label(self.root, text="Телефон")
        self.label_phone.grid(row=0, column=3)

        self.add_btn = tk.Button(self.root, text="Добавить запись", command=self.add_client)
        self.add_btn.grid(row=1, column=5)
        self.del_btn = tk.Button(self.root, text="Удалить запись", command=self.delete_client)
        self.del_btn.grid(row=1, column=6)
        self.update_btn = tk.Button(self.root, text="Обновить запись", command=self.change_client)
        self.update_btn.grid(row=2, column=5)
        self.search_btn = tk.Button(self.root, text="Поиск", command=self.find_client)
        self.search_btn.grid(row=2, column=6)
        self.add_phone_btn = tk.Button(self.root, text="Добавить телефон", command=self.add_phone)
        self.add_phone_btn.grid(row=3, column=5)
        self.del_phone_btn = tk.Button(self.root, text="Удалить телефон", command=self.delete_phone)
        self.del_phone_btn.grid(row=3, column=6)

        self.tree = ttk.Treeview(self.root, columns=("id", "Имя", "Фамилия", "Email", "Телефон"), show="headings")
        self.tree.grid(row=4, column=0, columnspan=4)
        self.tree.heading("#1", text="ID")
        self.tree.heading("#2", text="Имя")
        self.tree.heading("#3", text="Фамилия")
        self.tree.heading("#4", text="Email")
        self.tree.heading("#5", text="Телефон")
        self.tree.column("#1", width=30)
        self.tree.column("#2", width=150)
        self.tree.column("#3", width=150)
        self.tree.column("#4", width=150)
        self.tree.column("#5", width=150)
        self.tree.bind("<<TreeviewSelect>>", self.label_text_info)

        self.label_text = tk.Listbox(self.root, width=40)
        self.label_text.grid(row=4, column=5, columnspan=2)

    # Редактирование информации в записи
    def change_client(self):
        info = self.tree.item(self.tree.focus())["values"]
        phone = self.entry_phone.get("1.0", "end").strip().split("\n")
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE phonebook SET name = %s, surname = %s, email = %s, phone = %s WHERE id = %s",
                (self.entry_name.get(), self.entry_surname.get(), self.entry_email.get(),
                 ','.join(phone), info[0])
            )
            self.conn.commit()
        self.table_info()

    # Поиск нужной записи
    def find_client(self):
        if (self.entry_name.get() == "" and self.entry_surname.get() == "" and
                self.entry_email.get() == "" and self.entry_phone.get("1.0", "end").strip() == ""):
            self.table_info()
            return
        self.tree.delete(*self.tree.get_children())
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, surname, email, phone FROM phonebook WHERE LOWER(name) = %s OR "
                "LOWER(surname) = %s OR LOWER(email) = %s OR phone = %s",
                (self.entry_name.get().lower(), self.entry_surname.get().lower(), self.entry_email.get().lower(),
                 self.entry_phone.get("1.0", "end").strip()))
            rows = cur.fetchall()

            if rows:
                for row in rows:
                    self.tree.insert("", "end", values=row)

    # Добавление новой записи
    def add_client(self):
        if self.entry_name.get() != "" and self.entry_surname.get() != "":
            phone = self.entry_phone.get("1.0", "end").strip().split("\n")
            phones_to_add = [ph for ph in phone if ph]
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO phonebook(name, surname, email, phone) VALUES (%s, %s, %s, %s)",
                    (self.entry_name.get(), self.entry_surname.get(), self.entry_email.get(), ','.join(phones_to_add)),
                )
                self.conn.commit()
            self.table_info()
            self.entry_name.delete(0, "end")
            self.entry_surname.delete(0, "end")
            self.entry_email.delete(0, "end")
            self.entry_phone.delete("1.0", "end")
        else:
            msg = tk.Message(self.root, text="Заполните обязательные поля (*)", width=200)
            msg.grid(row=2, column=0, columnspan=4)
            msg.after(2000, msg.destroy)

    # Удаление записи
    def delete_client(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            data = self.tree.item(item, "values")
            with self.conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM phonebook WHERE id = %s AND name = %s AND surname = %s AND email = %s AND phone = %s",
                    (data[0], data[1], data[2], data[3], data[4])
                )
                self.conn.commit()
        self.table_info()

    # Добавление номера
    def add_phone(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            data = self.tree.item(item, "values")
            new_phones = self.entry_phone.get("1.0", "end").strip().split("\n")

            for phone in new_phones:
                if phone:
                    with self.conn.cursor() as cur:
                        cur.execute(
                            "UPDATE phonebook SET phone = CONCAT_WS(',', phone, %s) WHERE id = %s "
                            "AND name = %s AND surname = %s AND email = %s",
                            (phone, data[0], data[1], data[2], data[3])
                        )
                        self.conn.commit()
        self.table_info()

    # Удаление выбранного номера
    def delete_phone(self):
        selected_items = self.tree.selection()
        data = self.tree.item(selected_items[0], "values")
        phone_numbers = data[4].split(",")

        new_window = tk.Toplevel(self.root)
        new_window.geometry("200x300")
        new_window.title("Удалить номер")

        def delete_number(phone):
            phone_numbers.remove(phone)
            with self.conn.cursor() as cur:
                cur.execute(
                    "UPDATE phonebook SET phone = %s WHERE id = %s",
                    (','.join(phone_numbers), data[0])
                )
                self.conn.commit()
            self.table_info()
            new_window.destroy()

        for item in range(len(phone_numbers)):
            phone = phone_numbers[item]
            btn = tk.Button(new_window, text=phone, command=lambda phone=phone: delete_number(phone))
            btn.grid(row=item, column=0, padx=5, pady=2)


if __name__ == "__main__":
    m = Main()
    m.conn.close()
