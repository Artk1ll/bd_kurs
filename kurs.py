import psycopg2
import sys
import hashlib

# Список таблиц, к которым имеют доступ разные роли
USER_TABLES = ['dogovor', 'excursion', 'food', 'auto', 'hotel']
ALL_TABLES = ['tourburo', 'dogovor', 'customer', 'excursion', 'tour', 'autorent', 'hotel', 'food', 'users']

# Представления
VIEWS = {
    '1': 'tour_agency_view',
    '2': 'tour_excursion_view',
    '3': 'auto_rent_view'
}

# Глобальные переменные для авторизации
current_user = None
current_role = None

# Подключение к БД
def get_connection():
    try:
        connection = psycopg2.connect(
            user="st1092",
            password="pwd1092",
            host="172.20.7.9",
            port="5432",
            database="db1092_01"
        )
        connection.autocommit = False
        return connection
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        sys.exit(1)

# Авторизация в приложении
def login(conn):
    global current_user, current_role

    # Словарь с логинами и паролями
    users_db = {
        "vangogh": "$1$7e.bk2Vv$Q5N/sASBP/QyINTYGTI7U/",
        "davinci": "$1$H2ls/XtP$jhIrT2UwIuFDJMIJvE6ME/",
        "picasso": "$1$k2VBQ7mM$Yga6TuxatrJwO1GJblYzM1",
        "banksy": "$1$p5vtsfSu$qfLMmgKpnWmhHFzgXCpbJ0"
    }

    print("\n=== Авторизация ===")
    username = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()

    # Проверка правильности логина и пароля
    if username in users_db and users_db[username] == password:
        current_user = username
        # Для простоты добавим роли вручную для каждого пользователя (можно подключить базу данных для ролей)
        roles = {
            "vangogh": "администратор",
            "davinci": "модератор",
            "picasso": "турагент",
            "banksy": "пользователь"
        }
        current_role = roles[username]
        print(f"Добро пожаловать, {current_user}! Ваша роль: {current_role}")
        return True
    else:
        print("Ошибка: Неверный логин или пароль.")
        return False


# Функция для отображения таблиц
def print_table(cursor, description, rows):
    if not rows:
        print("Данные отсутствуют.")
        return

    headers = [desc[0] for desc in description]
    print(" | ".join(headers))
    print("-" * (len(" | ".join(headers)) + 5))

    for row in rows:
        print(" | ".join(map(str, row)))


def view_tables(conn):
    print("\n--- Просмотр таблиц ---")

    if current_role == "пользователь":
        available_tables = USER_TABLES
    else:
        available_tables = ALL_TABLES

    for i, table in enumerate(available_tables, 1):
        print(f"{i}. {table}")

    choice = input("Введите номер таблицы: ").strip()

    try:
        table_name = available_tables[int(choice) - 1]
    except (IndexError, ValueError):
        print("Неверный выбор.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            print(f"\nДанные таблицы '{table_name}':")
            print_table(cur, cur.description, rows)
    except Exception as e:
        print(f"Ошибка при просмотре таблицы {table_name}: {e}")


def view_database_views(conn):
    print("\n--- Просмотр представлений ---")

    for key, view in VIEWS.items():
        print(f"{key}. {view}")

    choice = input("Введите номер представления: ").strip()
    view_name = VIEWS.get(choice)

    if not view_name:
        print("Неверный выбор.")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {view_name}")
            rows = cur.fetchall()
            print(f"\nДанные представления '{view_name}':")
            print_table(cur, cur.description, rows)
    except Exception as e:
        print(f"Ошибка при просмотре представления {view_name}: {e}")


def find_service_combination(conn):
    print("\n--- Поиск комбинации услуг ---")
    target_servicecost = input("Введите лимит стоимости услуги: ")

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT find_service_combination(%s)", (target_servicecost,))
            rows = cur.fetchall()
            print("\nНайденные комбинации услуг:")
            print_table(cur, cur.description, rows)
    except Exception as e:
        print(f"Ошибка при поиске комбинации услуг: {e}")

def add_tourburo(conn):
    print("\n--- Добавление нового турбюро ---")
    new_name = input("Введите название турбюро: ")
    new_address = input("Введите адрес турбюро: ")
    new_phone = input("Введите телефон (11 цифр): ")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tourburo (name, address, phone)
                VALUES (%s, %s, %s)
            """, (new_name, new_address, new_phone))

            conn.commit()
            print("Турбюро успешно добавлено!")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении турбюро: {e}")

def add_customer(conn):
    print("\n--- Добавление нового клиента ---")
    new_fam = input("Введите фамилию: ")
    new_imya = input("Введите имя: ")
    new_otch = input("Введите отчество: ")
    new_passport = input("Введите паспорт (10 цифр): ")
    new_address = input("Введите адрес: ")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO customer (fam, imya, otch, passport, address)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_fam, new_imya, new_otch, new_passport, new_address))

            conn.commit()
            print("Клиент успешно добавлен!")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении клиента: {e}")

def delete_customer(conn):
    print("\n--- Удаление клиента по ID ---")
    id_cust = input("Введите ID клиента для удаления: ")

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id_cust FROM customer WHERE id_cust = %s", (id_cust,))
            if not cur.fetchone():
                print("Ошибка: клиент с таким ID не найден!")
                return

            cur.execute("DELETE FROM customer WHERE id_cust = %s", (id_cust,))
            conn.commit()
            print("Клиент успешно удалён!")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении клиента: {e}")

def reset_customer_sequence(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(id_cust) FROM customer")  # Получаем максимальный id
            max_id = cur.fetchone()[0] or 0  # Если таблица пуста, начинаем с 1

            cur.execute("ALTER SEQUENCE customer_id_cust_seq RESTART WITH %s", (max_id + 1,))
            conn.commit()
            print(f"Счётчик ID клиентов сброшен. Следующий ID: {max_id + 1}")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при сбросе ID последовательности: {e}")

def update_autorent(conn):
    print("\n--- Обновление информации об автомобиле ---")
    new_id_auto = input("Введите ID автомобиля для обновления: ")
    new_mark = input("Введите новую марку: ")
    new_autocost = input("Введите новую стоимость автомобиля: ")
    new_luxury = input("Введите новый уровень роскоши: ")

    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE autorent 
                SET mark = %s, autocost = %s, luxury = %s
                WHERE id_auto = %s
            """, (new_mark, new_autocost, new_luxury, new_id_auto))

            conn.commit()
            print("Информация об автомобиле успешно обновлена!")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при обновлении информации об автомобиле: {e}")

def execute_sql_query(conn):
    if current_role != "администратор":
        print("Ошибка: у вас нет прав для выполнения SQL-запросов.")
        return

    print("\n--- Выполнение SQL-запроса ---")
    query = input("Введите SQL-запрос: ").strip()

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            if query.lower().startswith("select"):
                rows = cur.fetchall()
                print_table(cur, cur.description, rows)
            else:
                conn.commit()
                print("Запрос выполнен успешно.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка выполнения запроса: {e}")


def main_menu():
    print("\nВыберите действие:")

    print("1. Просмотреть таблицы")
    print("2. Просмотреть представления")

    if current_role in ["пользователь", "турагент", "модератор", "администратор"]:
        print("3. Найти комбинацию услуг по лимиту")

    if current_role == "модератор" or current_role == "администратор":
        print("4. Добавить клиента")
        print("5. Добавить турбюро")
        print("6. Удалить клиента")
        print("7. Обновить информацию об автомобиле")

    if current_role == "администратор":
        print("8. Выполнить SQL-запрос")

    print("0. Выход")


def main():
    conn = get_connection()

    # Авторизация перед запуском
    while not login(conn):
        pass

    while True:
        main_menu()
        choice = input("Введите номер действия: ").strip()

        if choice == "1":
            view_tables(conn)
        elif choice == "2":
            view_database_views(conn)
        elif choice == "3" and current_role in ["пользователь", "турагент", "модератор", "администратор"]:
            find_service_combination(conn)
        elif choice == "4" and (current_role == "модератор" or current_role == "администратор"):
            add_customer(conn)
        elif choice == "5" and (current_role == "модератор" or current_role == "администратор"):
            add_tourburo(conn)
        elif choice == "6" and (current_role == "модератор" or current_role == "администратор"):
            delete_customer(conn)
        elif choice == "7" and (current_role == "модератор" or current_role == "администратор"):
            update_autorent(conn)
        elif choice == "8" and current_role == "администратор":
            execute_sql_query(conn)
        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

    conn.close()


if __name__ == '__main__':
    main()
