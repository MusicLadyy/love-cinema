import pickle
import datetime
import re
import sys

#console_io.py --------------------
class ConsoleIO:
    def input(self, field, defvalue=None):
        if defvalue:
            return input(f"{field} [{defvalue}]: ")
        return input(f"{field}: ")
    
    def output(self, title, field):
        print(f"{title}: {field}")
    
    def output_raw(self, text):
        print(text)
#----------------------------------

#storage_io.py --------------------
class PickleStorage:
    def __init__(self, cinema):
        self.cinema = cinema
    
    def store(self):
        data = {
            'users': self.cinema.users,
            'films': self.cinema.films,
            'food': self.cinema.food,
            'halls': self.cinema.halls,
            'tickets': self.cinema.tickets,
            'reminders': self.cinema.reminders,
            'hall_requests': self.cinema.hall_requests,
            'food_orders': self.cinema.food_orders,
            'next_user_id': self.cinema.next_user_id,
            'next_film_id': self.cinema.next_film_id,
            'next_food_id': self.cinema.next_food_id,
            'next_hall_id': self.cinema.next_hall_id,
            'next_ticket_id': self.cinema.next_ticket_id,
            'next_reminder_id': self.cinema.next_reminder_id,
            'next_request_id': self.cinema.next_request_id,
            'next_order_id': self.cinema.next_order_id,
            'current_user': self.cinema.current_user,
            'available_halls': {film_id: film.available_halls for film_id, film in self.cinema.films.items()}
            
        }
        pickle.dump(data, open("cinema.dat", "wb"))
        
    def load(self):
        try:
            data = pickle.load(open("cinema.dat", "rb"))
            self.cinema.users = data['users']
            self.cinema.films = data['films']
            
            available_halls = data.get('available_halls', {})
            for film_id, halls in available_halls.items():
                if film_id in self.cinema.films:
                    self.cinema.films[film_id].available_halls = halls
                    
            self.cinema.food = data['food']
            self.cinema.halls = data['halls']
            self.cinema.tickets = data.get('tickets', {})
            self.cinema.reminders = data.get('reminders', {})
            self.cinema.hall_requests = data.get('hall_requests', {})
            self.cinema.food_orders = data.get('food_orders', {})
            self.cinema.next_user_id = data['next_user_id']
            self.cinema.next_film_id = data['next_film_id']
            self.cinema.next_food_id = data['next_food_id']
            self.cinema.next_hall_id = data['next_hall_id']
            self.cinema.next_ticket_id = data.get('next_ticket_id', 1)
            self.cinema.next_reminder_id = data.get('next_reminder_id', 1)
            self.cinema.next_request_id = data.get('next_request_id', 1)
            self.cinema.next_order_id = data.get('next_order_id', 1)
            self.cinema.current_user = data['current_user']
            return True
        except:
            print("Файл не найден или поврежден")
            return False


#models.py 
class User:
    def __init__(self, id=0, name="", phone="", email="", password=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.password = password
        self.birth_date = ""
        self.agreement1 = False
        self.agreement2 = False
        self.is_admin = False
        self.io = ConsoleIO()
        
    def read(self):
        print("\n РЕГИСТРАЦИЯ ")
        
        # Имя (русские буквы)
        while True:
            self.name = self.io.input('Имя')
            if re.match(r'^[а-яА-ЯёЁ\s]+$', self.name):
                break
            print("Ошибка. Имя должно содержать только русские буквы.")
        
        # Email (латиница + @ + цифры)
        while True:
            self.email = self.io.input('Email')
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
                break
            print("Ошибка. Неверный формат email.")
        
        # Подтверждение email
        while True:
            email_confirm = self.io.input('Повторите Email')
            if email_confirm == self.email:
                break
            print("Ошибка. Email не совпадает.")
        
        # Телефон (только цифры)
        while True:
            self.phone = self.io.input('Мобильный номер')
            if re.match(r'^[0-9+\-\s]+$', self.phone):
                break
            print("Ошибка! Телефон должен содержать только цифры.")
        
        # Пароль по умолчанию
        self.password = "1288"
        
        # Дата рождения (только цифры в формате дд.мм.гггг)
        while True:
            self.birth_date = self.io.input('Дата рождения (дд.мм.гггг)')
            if re.match(r'^\d{2}\.\d{2}\.\d{4}$', self.birth_date):
                break
            print("Ошибка! Используйте формат дд.мм.гггг.")
        
        # Согласие с правилами
        agree = self.io.input('Я согласен с правилами Программы Лояльности (1 - да, 0 - нет)')
        self.agreement1 = (agree == '1')
        
        agree = self.io.input('Я согласен с правилами обработки персональных данных (1 - да, 0 - нет)')
        self.agreement2 = (agree == '1')
        
        if not (self.agreement1 and self.agreement2):
            print("Регистрация невозможна без согласия с правилами.")
            return False
        
        print("Регистрация успешно завершена.")
        return True
        
    def write(self):
        self.io.output('Имя', self.name)
        self.io.output('Телефон', self.phone)
        self.io.output('Email', self.email)
        self.io.output('Дата рождения', self.birth_date)

    def edit(self):
        print("\n РЕДАКТИРОВАНИЕ ПРОФИЛЯ ")
    
        # Имя (русские буквы)
        while True:
            new_name = self.io.input('Имя', self.name)
            if new_name == self.name:  # оставили текущее
                break
            if re.match(r'^[а-яА-ЯёЁ\s]+$', new_name):
                self.name = new_name
                break
            print("Ошибка. Имя должно содержать только русские буквы.")
    
        # Email (латиница + @ + цифры)
        while True:
            new_email = self.io.input('Email', self.email)
            if new_email == self.email:  # оставили текущее
                break
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
                # Запросим подтверждение нового email
                email_confirm = self.io.input('Повторите Email')
                if email_confirm == new_email:
                    self.email = new_email
                    break
                else:
                    print("Ошибка. Email не совпадает.")
            else:
                print("Ошибка. Неверный формат email.")
    
        # Телефон (только цифры)
        while True:
            new_phone = self.io.input('Мобильный номер', self.phone)
            if new_phone == self.phone:  # оставили текущее
                break
            if re.match(r'^[0-9+\-\s]+$', new_phone):
                self.phone = new_phone
                break
            print("Ошибка! Телефон должен содержать только цифры.")
    
        # Дата рождения (только цифры в формате дд.мм.гггг)
        while True:
            new_birth_date = self.io.input('Дата рождения (дд.мм.гггг)', self.birth_date)
            if new_birth_date == self.birth_date:  # оставили текущее
                break
            if re.match(r'^\d{2}\.\d{2}\.\d{4}$', new_birth_date):
                self.birth_date = new_birth_date
                break
            print("Ошибка! Используйте формат дд.мм.гггг.")
    
        print("Профиль успешно обновлен.")


class Film:
    def __init__(self, id=0, title="", photo="", genre="", event="", date_range=""):
        self.id = id
        self.title = title
        self.photo = photo
        self.genre = genre  # формат (ужасы/триллер/комедия)
        self.event = event  # событие (премьера/к 14 февраля/летнее)
        self.date_range = date_range  # диапазон дат показа
        self.available_halls = []  # список ID залов, где показывается фильм
        self.io = ConsoleIO()
    
    def read(self):
        self.title = self.io.input('Название фильма')
        self.photo = self.io.input('Ссылка на фото')
        self.genre = self.io.input('Формат (ужасы/триллер/комедия)')
        self.event = self.io.input('Событие (премьера/к 14 февраля/летнее)')
        self.date_range = self.io.input('Диапазон дат показа')
    
    def write(self):
        self.io.output('ID', self.id)
        self.io.output('Название', self.title)
        self.io.output('Фото', self.photo)
        self.io.output('Формат', self.genre)
        self.io.output('Событие', self.event)
        self.io.output('Даты показа', self.date_range)


class Food:
    def __init__(self, id=0, name="", price=0):
        self.id = id
        self.name = name
        self.price = price
        self.io = ConsoleIO()
    
    def read(self):
        self.name = self.io.input('Название')
        self.price = int(self.io.input('Цена', '0'))
    
    def write(self):
        self.io.output('ID', self.id)
        self.io.output('Название', self.name)
        self.io.output('Цена', f"{self.price} руб.")


class Hall:
    def __init__(self, id=0, name="", capacity=0, price_per_hour=0):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.price_per_hour = price_per_hour
        self.scheme = self.generate_seat_scheme(capacity)
        self.io = ConsoleIO()
    
    def generate_seat_scheme(self, capacity):
        # Генерируем схему мест (ряды и места)
        scheme = {}
        rows = (capacity + 9) // 10  # примерно 10 мест в ряду
        seats_per_row = (capacity + rows - 1) // rows
        
        for row in range(1, rows + 1):
            scheme[row] = list(range(1, seats_per_row + 1))
        
        return scheme
    
    def read(self):
        self.name = self.io.input('Название зала')
        self.capacity = int(self.io.input('Вместимость (человек)', '0'))
        self.price_per_hour = int(self.io.input('Цена за час (руб.)', '0'))
        self.scheme = self.generate_seat_scheme(self.capacity)
    
    def write(self):
        self.io.output('ID', self.id)
        self.io.output('Название', self.name)
        self.io.output('Вместимость', f"{self.capacity} чел.")
        self.io.output('Цена за час', f"{self.price_per_hour} руб.")


class CartItem:
    def __init__(self, food, quantity=1):
        self.food = food
        self.quantity = quantity
        self.total = food.price * quantity


class Ticket:
    def __init__(self, id, user_id, film_id, hall_id, date, time, row, seat, price, status='active'):
        self.id = id; self.user_id = user_id; self.film_id = film_id
        self.hall_id = hall_id; self.date = date; self.time = time
        self.row = row; self.seat = seat; self.price = price
        self.status = status  # 'active' или 'returned'
        
    
    def write(self):
        print(f"Билет #{self.id}")
        print(f"Фильм: {self.film_id}")
        print(f"Дата: {self.date} Время: {self.time}")
        print(f"Зал: {self.hall_id}, Ряд: {self.row}, Место: {self.seat}")
        print(f"Цена: {self.price} руб.")


class Reminder:
    def __init__(self, id=0, user_id=0, user_name="", phone="", film_id=0, film_title="", date="", time=""):
        self.id = id
        self.user_id = user_id
        self.user_name = user_name
        self.phone = phone
        self.film_id = film_id
        self.film_title = film_title
        self.date = date
        self.time = time


class HallRequest:
    def __init__(self, id=0, user_id=0, user_name="", phone="", hall_id=0, hall_name="", hours=0, total=0, notes=""):
        self.id = id
        self.user_id = user_id
        self.user_name = user_name
        self.phone = phone
        self.hall_id = hall_id
        self.hall_name = hall_name
        self.hours = hours
        self.total = total
        self.notes = notes


class FoodOrder:
    def __init__(self, id=0, user_id=0, user_name="", items=None, total=0, delivery_type="", delivery_details=""):
        self.id = id
        self.user_id = user_id
        self.user_name = user_name
        self.items = items or []
        self.total = total
        self.delivery_type = delivery_type
        self.delivery_details = delivery_details


#cinema_movies
class Cinema:
    def __init__(self):
        self.users = {}
        self.films = {}
        self.food = {}
        self.halls = {}
        self.tickets = {}
        self.reminders = {}
        self.hall_requests = {}
        self.food_orders = {}
        
        self.next_user_id = 1
        self.next_film_id = 1
        self.next_food_id = 1
        self.next_hall_id = 1
        self.next_ticket_id = 1
        self.next_reminder_id = 1
        self.next_request_id = 1
        self.next_order_id = 1
        
        self.current_user = None
        self.cart = []
        
        self.storage = PickleStorage(self)
        self.io = ConsoleIO()

        self.init_test_data()

        # Всегда создаем суперпользователя, если его нет
        superuser_exists = False
        for user in self.users.values():
            if user.phone == "89268841288":
                superuser_exists = True
                break
    
        if not superuser_exists:
            self.init_superuser()
    
    def init_superuser(self):
        # Создаем суперпользователя (админа)
        admin = User(
            id=self.next_user_id,
            name="Любовь Константиновна",
            phone="89268841288",
            email="lfilippova00@list.ru",
            password="0812"
        )
        admin.is_admin = True
        admin.birth_date = "08.12.2006"
        admin.agreement1 = True
        admin.agreement2 = True
        self.users[self.next_user_id] = admin
        self.next_user_id += 1

    def is_admin(self):
        return self.current_user and self.current_user.is_admin

    # ========== АДМИНИСТРИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ ==========
    def show_all_users(self):
        """Показать всех пользователей в виде таблицы"""
        if not self.is_admin():
            print("Доступ запрещен! Только для администратора.")
            return
    
        if not self.users:
            print("Список пользователей пуст")
            return
    
        print("\n" )
        print(f"{'ID':<5} {'Имя':<25} {'Телефон':<15} {'Email':<30} {'Дата рождения':<12} {'Админ':<6}")
        print()
    
        for user in self.users.values():
            admin_mark = "Да" if user.is_admin else "Нет"
            print(f"{user.id:<5} {user.name:<25} {user.phone:<15} {user.email:<30} {user.birth_date:<12} {admin_mark:<6}")
    
        print()

    def add_user_admin(self):
        """Добавить нового пользователя (от имени администратора)"""
        if not self.is_admin():
            print("Доступ запрещен! Только для администратора.")
            return
    
        print("\n ДОБАВЛЕНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ (АДМИНИСТРАТОР)")
        user = User(self.next_user_id)
    
        # Ввод данных с проверками
        while True:
            user.name = user.io.input('Имя')
            if re.match(r'^[а-яА-ЯёЁ\s]+$', user.name):
                break
            print("Ошибка. Имя должно содержать только русские буквы.")
    
        while True:
            user.email = user.io.input('Email')
            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user.email):
                # Проверим уникальность email
                email_exists = False
                for existing_user in self.users.values():
                    if existing_user.email == user.email:
                        print("Пользователь с таким email уже существует!")
                        email_exists = True
                        break
                if not email_exists:
                    break
            else:
                print("Ошибка. Неверный формат email.")
    
        while True:
            user.phone = user.io.input('Мобильный номер')
            if re.match(r'^[0-9+\-\s]+$', user.phone):
                # Проверим уникальность телефона
                phone_exists = False
                for existing_user in self.users.values():
                    if existing_user.phone == user.phone:
                        print("Пользователь с таким номером телефона уже существует.")
                        phone_exists = True
                        break
                if not phone_exists:
                    break
            else:
                print("Ошибка! Телефон должен содержать только цифры.")
    
        while True:
            user.birth_date = user.io.input('Дата рождения (дд.мм.гггг)')
            if re.match(r'^\d{2}\.\d{2}\.\d{4}$', user.birth_date):
                break
            print("Ошибка! Используйте формат дд.мм.гггг.")
    
        # Пароль по умолчанию
        user.password = "1288"
    
        # Можно ли сделать пользователя администратором?
        make_admin = user.io.input('Сделать администратором? (1 - да, 0 - нет)', '0')
        user.is_admin = (make_admin == '1')
    
        # Автоматически соглашаемся с правилами
        user.agreement1 = True
        user.agreement2 = True
    
        self.users[self.next_user_id] = user
        print(f"Пользователь {user.name} добавлен с ID {self.next_user_id}")
        self.next_user_id += 1

    def delete_user_admin(self):
        """Удалить пользователя (от имени администратора)"""
        if not self.is_admin():
            print("Доступ запрещен! Только для администратора.")
            return
    
        self.show_all_users()
    
        try:
            user_id = int(self.io.input('\nВведите ID пользователя для удаления'))
        
            if user_id not in self.users:
                print("Пользователь с таким ID не найден.")
                return
        
            # Не даем удалить самого себя (администратора)
            if user_id == self.current_user.id:
                print("Нельзя удалить самого себя.")
                return
        
            # Не даем удалить суперпользователя (Любовь Константиновна)
            if self.users[user_id].phone == "89268841288":
                print("Нельзя удалить суперпользователя.")
                return
        
            deleted_user = self.users.pop(user_id)
            print(f"Пользователь {deleted_user.name} (ID: {user_id}) удален.")
        
        except ValueError:
            print("Некорректный ID")

    def edit_user_admin(self):
        """Изменить данные пользователя (от имени администратора)"""
        if not self.is_admin():
            print("Доступ запрещен! Только для администратора.")
            return
    
        self.show_all_users()
    
        try:
            user_id = int(self.io.input('\nВведите ID пользователя для редактирования'))
        
            if user_id not in self.users:
                print("Пользователь с таким ID не найден.")
                return
        
            user = self.users[user_id]
        
            print(f"\nРедактирование пользователя: {user.name}")
            print("Выберите поле для изменения:")
            print("1. Имя")
            print("2. Телефон")
            print("3. Email")
            print("4. Дата рождения")
            print("5. Права администратора")
            print("0. Отмена")
        
            field_choice = int(self.io.input('Ваш выбор', '0'))
        
            if field_choice == 0:
                return
            elif field_choice == 1:
                # Изменение имени
                while True:
                    new_value = self.io.input('Новое имя', user.name)
                    if new_value == user.name:
                        break
                    if re.match(r'^[а-яА-ЯёЁ\s]+$', new_value):
                        user.name = new_value
                        print("Имя обновлено")
                        break
                    print("Ошибка. Имя должно содержать только русские буквы.")
        
            elif field_choice == 2:
                # Изменение телефона
                while True:
                    new_value = self.io.input('Новый телефон', user.phone)
                    if new_value == user.phone:
                        break
                    if re.match(r'^[0-9+\-\s]+$', new_value):
                        # Проверим уникальность
                        phone_exists = False
                        for existing_user in self.users.values():
                            if existing_user.id != user_id and existing_user.phone == new_value:
                                print("Этот номер телефона уже используется.")
                                phone_exists = True
                                break
                        if not phone_exists:
                            user.phone = new_value
                            print("Телефон обновлен")
                            break
                    else:
                        print("Ошибка! Телефон должен содержать только цифры.")
        
            elif field_choice == 3:
                # Изменение email
                while True:
                    new_value = self.io.input('Новый email', user.email)
                    if new_value == user.email:
                        break
                    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_value):
                        # Проверим уникальность
                        email_exists = False
                        for existing_user in self.users.values():
                            if existing_user.id != user_id and existing_user.email == new_value:
                                print("Этот email уже используется.")
                                email_exists = True
                                break
                        if not email_exists:
                            user.email = new_value
                            print("Email обновлен")
                            break
                    else:
                        print("Ошибка. Неверный формат email.")
        
            elif field_choice == 4:
                # Изменение даты рождения
                while True:
                    new_value = self.io.input('Новая дата рождения', user.birth_date)
                    if new_value == user.birth_date:
                        break
                    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', new_value):
                        user.birth_date = new_value
                        print("Дата рождения обновлена.")
                        break
                    print("Ошибка! Используйте формат дд.мм.гггг.")
        
            elif field_choice == 5:
                # Изменение прав администратора
                if user_id == self.current_user.id:
                    print("Нельзя изменить свои права администратора.")
                    return
                if user.phone == "89268841288":
                    print("Нельзя изменить права суперпользователя.")
                    return
            
                new_value = self.io.input('Сделать администратором? (1 - да, 0 - нет)', 
                                      '1' if user.is_admin else '0')
                user.is_admin = (new_value == '1')
                print(f"Права администратора: {'Да' if user.is_admin else 'Нет'}")
        
            else:
                print("Неверный выбор")
            
        except ValueError:
            print("Некорректный ввод")

    def cleanup_with_admin(self):
        """Очистить файл, но сохранить администратора"""
        if not self.is_admin():
            print("Доступ запрещен! Только для администратора.")
            return
    
        print("\nОЧИСТКА ДАННЫХ С СОХРАНЕНИЕМ АДМИНИСТРАТОРА")
        print("Будут удалены:")
        print("- Все обычные пользователи")
        print("- Все фильмы")
        print("- Все позиции меню")
        print("- Все залы")
        print("- Все билеты, напоминания, заказы")
        print("- Корзина")
        print("\nАдминистратор будет сохранен")
    
        confirm = self.io.input('Продолжить? (1 - да, 0 - нет)', '0')
    
        if confirm == '1':
            # Сохраняем администратора
            admin_user = None
            for user in self.users.values():
                if user.phone == "89268841288":
                    admin_user = user
                    break
        
            # Очищаем все
            self.users.clear()
            self.films.clear()
            self.food.clear()
            self.halls.clear()
            self.tickets.clear()
            self.reminders.clear()
            self.hall_requests.clear()
            self.food_orders.clear()
            self.cart.clear()
        
            # Восстанавливаем администратора
            if admin_user:
                admin_user.id = 1
                self.users[1] = admin_user
                self.next_user_id = 2
                self.current_user = admin_user
            else:
                # Если админ не найден, создаем нового
                self.init_superuser()
        
            # Восстанавливаем тестовые данные
            self.init_test_data()
        
            print("Данные очищены. Администратор сохранен.")

    # ========== РЕДАКТИРОВАНИЕ ПРОФИЛЯ ==========
    def edit_profile(self):
        if not self.current_user:
            print("Вы не авторизованы!")
            return
    
        print("\n РЕДАКТИРОВАНИЕ ПРОФИЛЯ ")
    
        # Сохраняем старый телефон для проверки
        old_phone = self.current_user.phone
    
        # Редактируем профиль
        self.current_user.edit()
    
        # Если телефон изменился, проверяем, не занят ли он другим пользователем
        if old_phone != self.current_user.phone:
            for user_id, user in self.users.items():
                if user.id != self.current_user.id and user.phone == self.current_user.phone:
                    print("Этот номер телефона уже используется другим пользователем.")
                    # Возвращаем старый телефон
                    self.current_user.phone = old_phone
                    return
    
    def init_test_data(self):
        films_data = [
            ["Аватар", "avatar.jpg", "фантастика", "летнее", "15.04-30.04"],
            ["Оно", "ono.jpg", "ужасы", "летнее", "01.05-15.05"],
            ["Дюна", "dune.jpg", "фантастика", "летнее", "10.04-25.04"],
            ["Чебурашка", "cheb.jpg", "комедия", "к 14 февраля", "10.04-20.04"],
            ["Драйв", "drive.jpg", "триллер", "летнее", "20.04-05.05"],
            ["Барби", "barbie.jpg", "комедия", "летнее", "01.05-15.05"],
            ["Крик", "krik.jpg", "ужасы", "хэллоуин", "25.05-05.05"],
            ["1+1", "1plus1.jpg", "комедия", "выходные", "каждые выходные"],
            ["Зеркала. Пожиратели душ", "mirrors.jpg", "триллер", "премьера", "15.06-28.06"],
            ["Преступление на третьем этаже", "crime.jpg", "комедия", "премьера", "01.06-23.06"]
        ]
        
        for title, photo, genre, event, date_range in films_data:
            film = Film(self.next_film_id, title, photo, genre, event, date_range)
            self.films[self.next_film_id] = film
            self.next_film_id += 1
        
        # Еда
        food_data = [
            ["Картошка фри", 250],
            ["Попкорн соленый", 200],
            ["Попкорн сладкий", 220],
            ["Сок яблочный", 150],
            ["Мороженное (ваниль)", 80],
            ["Кола", 120],
            ["Начос", 180]
        ]
        
        for name, price in food_data:
            food = Food(self.next_food_id, name, price)
            self.food[self.next_food_id] = food
            self.next_food_id += 1
        
        # Залы
        halls_data = [
            ["Малый зал", 30, 1000],
            ["Средний зал", 50, 1500],
            ["Большой зал", 100, 2500],
            ["VIP зал", 20, 2000]
        ]
        
        for name, capacity, price in halls_data:
            hall = Hall(self.next_hall_id, name, capacity, price)
            self.halls[self.next_hall_id] = hall
            self.next_hall_id += 1
        
        # Привязываем фильмы к залам
        film_halls = {
            1: [1, 2],  # Аватар: Малый и Средний залы
            2: [1],      # Оно: Малый зал
            3: [2, 3],   # Дюна: Средний и Большой
            4: [1],      # Чебурашка: Малый зал
            5: [2, 4],   # Драйв: Средний и VIP
            6: [3],      # Барби: Большой зал
            7: [1, 4],   # Крик: Малый и VIP
            8: [1, 2, 3] # 1+1: все залы кроме VIP
        }
        
        for film_id, hall_ids in film_halls.items():
            if film_id in self.films:
                self.films[film_id].available_halls = hall_ids
    
    # ========== АВТОРИЗАЦИЯ ==========
    def login(self):
        print("\n ВХОД В СИСТЕМУ ")
        phone = self.io.input('Введите номер телефона')
        code = self.io.input('Введите SMS-код')
        
        # Ищем пользователя
        for user in self.users.values():
            if user.phone == phone and user.password == code:
                self.current_user = user
                if user.is_admin:
                    print(f"Добро пожаловать, {user.name}!")
                else:
                    print(f"Добро пожаловать, {user.name}!")
                return
        
        print("Неверный номер телефона или SMS-код.")
    
    # ========== РЕГИСТРАЦИЯ ==========
    def register(self):
        user = User(self.next_user_id)
        if user.read():
            for existing_user in self.users.values():
                if existing_user.phone == user.phone:
                    print("Пользователь с таким номером телефона уже существует.")
                    return
            
            self.users[self.next_user_id] = user
            self.next_user_id += 1
            self.current_user = user
            print("Регистрация успешно завершена.")
    
    # ========== ВЫХОД ==========
    def logout(self):
        self.current_user = None
        print("Вы вышли из системы.")
    
    # ========== ПРОСМОТР ПРОФИЛЯ ==========
    def view_profile(self):
        if not self.current_user:
            print("Вы не авторизованы.")
            return
        
        print("\n ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ")
        self.current_user.write()
        
        # Показываем купленные билеты
        self.show_user_tickets()
    
    def show_user_tickets(self):
        user_tickets = [t for t in self.tickets.values() if t.user_id == self.current_user.id]
        
        if not user_tickets:
            print("\n У вас нет купленных билетов.")
            return
        
        print("\n ВАШИ БИЛЕТЫ ")
        for ticket in user_tickets:
            film = self.films.get(ticket.film_id, None)
            hall = self.halls.get(ticket.hall_id, None)
            
            print(f"\nБилет #{ticket.id}")
            print(f"Фильм: {film.title if film else 'Неизвестный фильм'}")
            print(f"Дата: {ticket.date} Время: {ticket.time}")
            print(f"Зал: {hall.name if hall else 'Неизвестный зал'}, Ряд: {ticket.row}, Место: {ticket.seat}")
            print(f"Цена: {ticket.price} руб.")
            print(f"Ссылка на оплату: {ticket.payment_link}")
    
    # ========== ПОКУПКА БИЛЕТОВ ==========
    def buy_tickets_page(self):
        if not self.current_user:
            print("Для покупки билетов необходимо авторизоваться.")
            return
        
        while True:
            print("\nПОКУПКА БИЛЕТОВ")
            print("1. Выбрать фильм")
            print("2. Мои билеты")
            print("0. Назад")
            
            try:
                choice = int(self.io.input('Выберите действие', ''))
                
                if choice == 0:
                    return
                elif choice == 1:
                    self.select_film_for_ticket()
                elif choice == 2:
                    self.show_user_tickets()
                else:
                    print("Неверный выбор.")
                    
                input("\n Нажмите Enter для продолжения...")
            except:
                print("Ошибка ввода")
    
    def select_film_for_ticket(self):
        print("\n ДОСТУПНЫЕ ФИЛЬМЫ")
        for film in self.films.values():
            print(f"{film.id}. {film.title} ({film.genre}) - {film.date_range}")
        
        try:
            film_id = int(self.io.input('Выберите ID фильма'))
            if film_id not in self.films:
                print("Фильм не найден.")
                return
            
            film = self.films[film_id]
            
            # Показываем доступные залы для этого фильма
            print(f"\n Доступные залы для фильма '{film.title}':")
            available_halls = []
            for hall_id in film.available_halls:
                if hall_id in self.halls:
                    hall = self.halls[hall_id]
                    print(f"{hall.id}. {hall.name} - вместимость: {hall.capacity} мест")
                    available_halls.append(hall)
            
            if not available_halls:
                print("Для этого фильма нет доступных залов")
                return
            
            hall_id = int(self.io.input('Выберите ID зала'))
            if hall_id not in [h.id for h in available_halls]:
                print("Зал не доступен для этого фильма!")
                return
            
            hall = self.halls[hall_id]
            
            # Выбор даты и времени
            date = self.io.input('Дата сеанса (дд.мм.гггг)')
            time = self.io.input('Время сеанса (чч:мм)')
            
            # Показываем схему зала
            print(f"\nСхема зала {hall.name}:")
            print("Доступные ряды и места:")
            for row, seats in hall.scheme.items():
                print(f"Ряд {row}: места {min(seats)}-{max(seats)}")
            
            # Выбор места
            row = int(self.io.input('Выберите ряд'))
            if row not in hall.scheme:
                print("Неверный номер ряда!")
                return
            
            seat = int(self.io.input('Выберите место'))
            if seat not in hall.scheme[row]:
                print("Неверный номер места!")
                return
            
            # Проверяем, не занято ли место
            for ticket in self.tickets.values():
                if (ticket.film_id == film_id and ticket.hall_id == hall_id and 
                    ticket.date == date and ticket.time == time and 
                    ticket.row == row and ticket.seat == seat):
                    print("Это место уже занято!")
                    return
            
            # Цена билета (базовая цена + наценка за VIP)
            base_price = 350
            if hall.name == "VIP зал":
                price = base_price * 2
            else:
                price = base_price + (hall.capacity // 10) * 50
            
            print(f"\n Стоимость билета: {price} руб.")
            print(f" Ссылка для оплаты: https://tbank.sbp/Love")
            
            confirm = self.io.input('Подтвердить покупку? (1 - да, 0 - нет)', '0')
            
            if confirm == '1':
                # Создаем билет
                ticket = Ticket(
                    id=self.next_ticket_id,
                    user_id=self.current_user.id,
                    film_id=film_id,
                    hall_id=hall_id,
                    date=date,
                    time=time,
                    row=row,
                    seat=seat,
                    price=price
                )
                
                self.tickets[self.next_ticket_id] = ticket
                self.next_ticket_id += 1
                
                print("Билет успешно куплен!")
            
        except ValueError:
            print("Некорректный ввод")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    # ========== ПРОСМОТР ВСЕХ ФИЛЬМОВ С СОРТИРОВКОЙ ==========
    def view_films_sorted(self):
        if not self.films:
            print("Список фильмов пуст")
            return
        
        print("\nФИЛЬМЫ")
        print("Выберите сортировку:")
        print("1. По формату (жанру)")
        print("2. По событию")
        print("3. По дате показа")
        
        try:
            sort_choice = int(self.io.input('Ваш выбор', '1'))
            
            films_list = list(self.films.values())
            
            if sort_choice == 1:
                films_list.sort(key=lambda x: x.genre)
                print("\nФИЛЬМЫ ПО ФОРМАТУ (ЖАНРУ)")
            elif sort_choice == 2:
                films_list.sort(key=lambda x: x.event)
                print("\nФИЛЬМЫ ПО СОБЫТИЮ")
            elif sort_choice == 3:
                films_list.sort(key=lambda x: x.date_range)
                print("\n ФИЛЬМЫ ПО ДАТЕ ПОКАЗА ")
            else:
                print("Неверный выбор")
                return
            
            for film in films_list:
                film.write()
                print('-' * 33)
                
        except Exception as e:
            print(f"Ошибка: {e}")
    
    # ========== ГЛАВНАЯ СТРАНИЦА ==========
    def main_page(self):
        while True:
            print("\nГЛАВНАЯ СТРАНИЦА")
            print("1. Просмотр всех фильмов")
            print("2. Просмотр фильмов с сортировкой")
            print("3. Купить билеты")
            print("4. Контакты")
            print("0. Назад")
            
            try:
                choice = int(self.io.input('Выберите действие', ''))
                
                if choice == 0:
                    return
                elif choice == 1:
                    self.view_all_films_simple()
                elif choice == 2:
                    self.view_films_sorted()
                elif choice == 3:
                    self.buy_tickets_page()
                elif choice == 4:
                    self.show_info()
                else:
                    print("Неверный выбор.")
                
                input("\nНажмите Enter для продолжения...")
            except:
                print("Ошибка ввода")

    def view_all_films_simple(self):
        if not self.films:
            print("Список фильмов пуст")
            return
        
        print("\nВСЕ ФИЛЬМЫ ")
        for film in self.films.values():
            film.write()
            print("-" * 33)
    
    # ========== ПРЕМЬЕРА ==========
    def premiere_page(self):
        while True:
            print("\nПРЕМЬЕРЫ ")
            print("1. Посмотреть все премьеры")
            print("2. Установить напоминание о премьере")
            print("0. Назад")
            
            try:
                choice = int(self.io.input('Выберите действие', '0'))
                
                if choice == 0:
                    return
                elif choice == 1:
                    self.view_premieres()
                elif choice == 2:
                    self.set_premiere_reminder()
                else:
                    print("Неверный выбор!")
                    
                input("\nНажмите Enter для продолжения...")
            except:
                print("Ошибка ввода")
    
    def view_premieres(self):
        print("\nПРЕМЬЕРЫ")
        premieres = [f for f in self.films.values() if "премьера" in f.event.lower()]
        
        if not premieres:
            print("Сейчас нет премьер")
            return
        
        for film in premieres:
            film.write()
            print("-" * 40)
    
    def set_premiere_reminder(self):
        print("\nУСТАНОВИТЬ НАПОМИНАНИЕ О ПРЕМЬЕРЕ")
        
        # Показываем список премьер
        premieres = [f for f in self.films.values() if "премьера" in f.event.lower()]
        
        if not premieres:
            print("Сейчас нет премьер для напоминания")
            return
        
        print("Доступные премьеры:")
        for film in premieres:
            print(f"{film.id}. {film.title} (с {film.date_range})")
        
        try:
            film_id = int(self.io.input('Выберите ID фильма для напоминания'))
            if film_id not in self.films or "премьера" not in self.films[film_id].event.lower():
                print("Фильм не найден или это не премьера!")
                return
            
            film = self.films[film_id]
            
            # Дата и время напоминания
            print("\nУкажите, когда напомнить:")
            reminder_date = self.io.input('Дата напоминания (дд.мм.гггг)')
            reminder_time = self.io.input('Время напоминания (чч:мм)')
            
            # Телефон для напоминания
            if self.current_user:
                phone = self.current_user.phone
                user_name = self.current_user.name
                user_id = self.current_user.id
            else:
                phone = self.io.input('Введите номер телефона для напоминания')
                user_name = "Неизвестный пользователь"
                user_id = 0
            
            # Сохраняем напоминание
            reminder = Reminder(
                id=self.next_reminder_id,
                user_id=user_id,
                user_name=user_name,
                phone=phone,
                film_id=film_id,
                film_title=film.title,
                date=reminder_date,
                time=reminder_time
            )
            
            self.reminders[self.next_reminder_id] = reminder
            self.next_reminder_id += 1
            
            print(f"\nНапоминание о премьере '{film.title}' установлено на {reminder_date} в {reminder_time}")
            print(f"Номер для уведомления: {phone}")
            
        except ValueError:
            print("Некорректный ID")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    # ========== МЕРОПРИЯТИЯ ==========
    def events_page(self):
        while True:
            print("\n МЕРОПРИЯТИЯ ")
            print("1. Просмотр мероприятий по категориям")
            print("2. Наши залы")
            print("3. Калькулятор аренды зала")
            print("0. Назад")
        
            try:
                choice = int(self.io.input('Выберите действие', '0'))
            
                if choice == 0:
                    return
                elif choice == 1:
                    self.view_events_by_category()
                elif choice == 2:
                    self.view_halls()
                elif choice == 3:
                    self.hall_rental_calculator()
                else:
                    print("Неверный выбор!")
                
                input("\nНажмите Enter для продолжения...")
            except:
                print("Ошибка ввода")

    def view_events_by_category(self):
        print("\nМЕРОПРИЯТИЯ ПО КАТЕГОРИЯМ")
        events = {}
        for film in self.films.values():
            if film.event not in events:
                events[film.event] = []
            events[film.event].append(film)
    
        for event_name, films_list in events.items():
            print(f"\n--- {event_name.upper()} ---")
            for film in films_list:
                print(f"  • {film.title} ({film.date_range})")

    # ========== ПРОСМОТР ЗАЛОВ ==========
    def view_halls(self):
        print("\nНАШИ ЗАЛЫ")
        for hall in self.halls.values():
            hall.write()
            print("-" * 33)
    
    # ========== КАЛЬКУЛЯТОР АРЕНДЫ ЗАЛА ==========
    def hall_rental_calculator(self):
        print("\n КАЛЬКУЛЯТОР АРЕНДЫ ЗАЛА")
        
        print("Доступные залы:")
        for hall in self.halls.values():
            print(f"{hall.id}. {hall.name} - {hall.capacity} чел., {hall.price_per_hour} руб./час")
        
        try:
            hall_id = int(self.io.input('Выберите ID зала'))
            if hall_id not in self.halls:
                print("Зал не найден.")
                return
            
            hall = self.halls[hall_id]
            
            print("Доступное время аренды: 1-5 часов")
            hours = int(self.io.input('Количество часов:', ''))
            if hours < 1 or hours > 5:
                print("Некорректное время!")
                return
            
            total = hall.price_per_hour * hours
            notes = self.io.input('Примечания (необязательно)')
            
            # Сохраняем заявку
            if self.current_user:
                request = HallRequest(
                    id=self.next_request_id,
                    user_id=self.current_user.id,
                    user_name=self.current_user.name,
                    phone=self.current_user.phone,
                    hall_id=hall_id,
                    hall_name=hall.name,
                    hours=hours,
                    total=total,
                    notes=notes
                )
            else:
                phone = self.io.input('Введите ваш телефон для связи')
                request = HallRequest(
                    id=self.next_request_id,
                    user_id=0,
                    user_name="Неизвестный пользователь",
                    phone=phone,
                    hall_id=hall_id,
                    hall_name=hall.name,
                    hours=hours,
                    total=total,
                    notes=notes
                )
            
            self.hall_requests[self.next_request_id] = request
            self.next_request_id += 1
            
            print(f"\nИТОГО: {total} руб.")
            print("Спасибо за заявку! Мы с вами свяжемся.")
            
        except ValueError:
            print("Некорректный ввод")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    # ========== МЕНЮ И КОРЗИНА (ОБЪЕДИНЕНЫ) ==========
    def menu_and_cart_page(self):
        while True:
            print("\nМЕНЮ И КОРЗИНА")
            print("1. Посмотреть меню и добавить в корзину")
            print("2. Посмотреть корзину")
            print("0. Назад")
            
            try:
                choice = int(self.io.input('Выберите действие', '0'))
                
                if choice == 0:
                    return
                elif choice == 1:
                    self.add_to_cart()
                elif choice == 2:
                    self.view_cart()
                else:
                    print("Неверный выбор!")
                    
            except ValueError:
                print("Ошибка ввода")
    
    def add_to_cart(self):
        print("\nМЕНЮ")
        for food in self.food.values():
            print(f"{food.id}. {food.name} - {food.price} руб.")
        print("\n0. Назад")
        
        try:
            food_id = int(self.io.input('Выберите ID еды для добавления в корзину'))
            if food_id == 0:
                return
            if food_id not in self.food:
                print("Еда не найдена!")
                return
            
            quantity = int(self.io.input('Количество:', ''))
            if quantity <= 0:
                print("Количество должно быть положительным!")
                return
                
            food = self.food[food_id]
            cart_item = CartItem(food, quantity)
            self.cart.append(cart_item)
            
            print(f"{food.name} x{quantity} добавлено в корзину")
        except ValueError:
            print("Некорректный ввод")
        except Exception as e:
            print(f"Ошибка при добавлении в корзину: {e}")
    
    def view_cart(self):
        if not self.cart:
            print("\nВы ничего не добавили в корзину")
            return
        
        print("\nВАША КОРЗИНА")
        total = 0
        for i, item in enumerate(self.cart, 1):
            print(f"{i}. {item.food.name} x{item.quantity} - {item.total} руб.")
            total += item.total
        
        print(f"\nИТОГО: {total} руб.")
        
        print("\nВыберите действие:")
        print("1. Заберу сам")
        print("2. Принести в зал")
        print("3. Удалить позицию из корзины")
        print("4. Продолжить покупки")
        print("0. Назад")
    
        try:
            choice = self.io.input('Ваш выбор', '0')
        
            if choice == '1':
                # Сохраняем заказ
                if self.current_user:
                    order = FoodOrder(
                        id=self.next_order_id,
                        user_id=self.current_user.id,
                        user_name=self.current_user.name,
                        items=[(item.food.name, item.quantity, item.total) for item in self.cart],
                        total=total,
                        delivery_type="самовывоз",
                        delivery_details="Заберу сам"
                    )
                    self.food_orders[self.next_order_id] = order
                    self.next_order_id += 1
                
                print("Заказ оформлен! Можете забрать его самостоятельно.")
                self.cart.clear()
            elif choice == '2':
                self.order_to_hall()
            elif choice == '3':
                self.remove_from_cart()
            elif choice == '4':
                self.add_to_cart()
        except Exception as e:
            print(f"Ошибка при выборе: {e}")

    def remove_from_cart(self):
        if not self.cart:
            print("Корзина пуста")
            return
    
        print("\nУДАЛЕНИЕ ИЗ КОРЗИНЫ")
        for i, item in enumerate(self.cart, 1):
            print(f"{i}. {item.food.name} x{item.quantity} - {item.total} руб.")
    
        try:
            item_num = int(self.io.input('Введите номер позиции для удаления', '0'))
        
            if item_num < 1 or item_num > len(self.cart):
                print("Неверный номер позиции!")
                return
        
            removed = self.cart.pop(item_num - 1)
            print(f" {removed.food.name} удален из корзины")
        
        except ValueError:
            print("Некорректный ввод")
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
    
    def order_to_hall(self):
        print("\nДОСТАВКА В ЗАЛ")
        
        if not self.current_user:
            print("Для заказа в зал необходимо авторизоваться!")
            return
        
        print("Текущие сеансы:")
        for film in self.films.values():
            print(f"{film.id}. {film.title}")
        
        try:
            film_id = int(self.io.input('Выберите ID фильма'))
            if film_id not in self.films:
                print("Фильм не найден!")
                return
        except:
            print("Некорректный ID")
            return
        
        print("Залы:")
        for hall in self.halls.values():
            print(f"{hall.id}. {hall.name}")
        
        try:
            hall_id = int(self.io.input('Выберите ID зала'))
            if hall_id not in self.halls:
                print("Зал не найден!")
                return
        except:
            print("Некорректный ID")
            return
        
        time = self.io.input('Время сеанса (чч:мм)')
        row = self.io.input('Ряд')
        seat = self.io.input('Место')
        
        # Сохраняем заказ
        total = sum(item.total for item in self.cart)
        delivery_details = f"Фильм: {self.films[film_id].title}, Зал: {self.halls[hall_id].name}, Время: {time}, Ряд: {row}, Место: {seat}"
        
        order = FoodOrder(
            id=self.next_order_id,
            user_id=self.current_user.id,
            user_name=self.current_user.name,
            items=[(item.food.name, item.quantity, item.total) for item in self.cart],
            total=total,
            delivery_type="доставка в зал",
            delivery_details=delivery_details
        )
        self.food_orders[self.next_order_id] = order
        self.next_order_id += 1
        
        print(f"\nЗаказ оформлен!")
        print(f"Фильм: {self.films[film_id].title}")
        print(f"Зал: {self.halls[hall_id].name}")
        print(f"Время: {time}")
        print(f"Место: ряд {row}, место {seat}")
        print("\nСсылка для оплаты: https://tbank.spv/Love")
        print("После оплаты заказ будет доставлен в зал!")
        
        self.cart.clear()
    
    # ========== АДМИН-ПАНЕЛЬ ==========
    def admin_dashboard(self):
        if not self.is_admin():
            print("Доступ запрещен! Только для администратора.")
            return
        
        while True:
            print("\n" + "-"*60)
            print("АДМИНИСТРАТОРСКАЯ ПАНЕЛЬ")
            print("-"*60)
            print("1. Управление пользователями")
            print("2. Заказы еды")
            print("3. Напоминания о премьерах")
            print("4. Заявки на аренду залов")
            print("5. Купленные билеты")
            print("6. Статистика")
            print("0. Назад")
            
            try:
                choice = int(self.io.input('Выберите раздел', '0'))
                
                if choice == 0:
                    return
                elif choice == 1:
                    self.user_management_menu()
                elif choice == 2:
                    self.show_food_orders()
                elif choice == 3:
                    self.show_reminders()
                elif choice == 4:
                    self.show_hall_requests()
                elif choice == 5:
                    self.show_all_tickets()
                elif choice == 6:
                    self.show_stats()
                else:
                    print("Неверный выбор!")
                    
                input("\nНажмите Enter для продолжения...")
            except ValueError:
                print("Введите число!")
    
    def user_management_menu(self):
        while True:
            print("\n УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ")
            print("1. Показать всех пользователей")
            print("2. Добавить пользователя")
            print("3. Удалить пользователя")
            print("4. Редактировать пользователя")
            print("5. Очистить данные (с сохранением админа)")
            print("0. Назад")
            
            try:
                admin_choice = int(input("Выберите действие: "))
                
                if admin_choice == 0:
                    break
                elif admin_choice == 1:
                    self.show_all_users()
                elif admin_choice == 2:
                    self.add_user_admin()
                elif admin_choice == 3:
                    self.delete_user_admin()
                elif admin_choice == 4:
                    self.edit_user_admin()
                elif admin_choice == 5:
                    self.cleanup_with_admin()
                else:
                    print("Неверный выбор!")
                
                input("\nНажмите Enter для продолжения...")
            except ValueError:
                print("Введите число!")
    
    def show_food_orders(self):
        if not self.food_orders:
            print("\nНет заказов еды")
            return
        
        print("\n" + "-"*100)
        print("ЗАКАЗЫ ЕДЫ")
        print("-"*100)
        print(f"{'ID':<5} {'Пользователь':<25} {'Телефон':<15} {'Тип доставки':<15} {'Сумма':<10} {'Детали':<30}")
        print("-"*100)
        
        for order in self.food_orders.values():
            user = self.users.get(order.user_id)
            phone = user.phone if user else "Неизвестно"
            
            items_str = ", ".join([f"{item[0]} x{item[1]}" for item in order.items])
            print(f"{order.id:<5} {order.user_name:<25} {phone:<15} {order.delivery_type:<15} {order.total:<10} {items_str[:30]}")
    
    def show_reminders(self):
        if not self.reminders:
            print("\nНет напоминаний о премьерах")
            return
        
        print("\n" + "-"*100)
        print("НАПОМИНАНИЯ О ПРЕМЬЕРАХ")
        print("-"*100)
        print(f"{'ID':<5} {'Пользователь':<25} {'Телефон':<15} {'Фильм':<30} {'Дата':<12} {'Время':<8}")
        print("-"*100)
        
        for reminder in self.reminders.values():
            print(f"{reminder.id:<5} {reminder.user_name:<25} {reminder.phone:<15} {reminder.film_title[:30]:<30} {reminder.date:<12} {reminder.time:<8}")
    
    def show_hall_requests(self):
        if not self.hall_requests:
            print("\nНет заявок на аренду залов")
            return
        
        print("\n" + "-"*100)
        print("ЗАЯВКИ НА АРЕНДУ ЗАЛОВ")
        print("-"*100)
        print(f"{'ID':<5} {'Пользователь':<25} {'Телефон':<15} {'Зал':<15} {'Часы':<6} {'Сумма':<10} {'Примечания':<25}")
        print("-"*100)
        
        for req in self.hall_requests.values():
            print(f"{req.id:<5} {req.user_name:<25} {req.phone:<15} {req.hall_name:<15} {req.hours:<6} {req.total:<10} {req.notes[:25]:<25}")
    
    def show_all_tickets(self):
        if not self.tickets:
            print("\nНет купленных билетов")
            return
        
        print("\n" + "-"*120)
        print("ВСЕ КУПЛЕННЫЕ БИЛЕТЫ")
        print("-"*120)
        print(f"{'ID':<5} {'Пользователь':<25} {'Телефон':<15} {'Фильм':<25} {'Дата':<12} {'Время':<8} {'Зал':<10} {'Место':<10} {'Цена':<8}")
        print("-"*120)
        
        for ticket in self.tickets.values():
            user = self.users.get(ticket.user_id)
            user_name = user.name if user else "Неизвестно"
            phone = user.phone if user else "Неизвестно"
            film = self.films.get(ticket.film_id)
            film_title = film.title if film else "Неизвестно"
            hall = self.halls.get(ticket.hall_id)
            hall_name = hall.name if hall else "Неизвестно"
            
            print(f"{ticket.id:<5} {user_name[:25]:<25} {phone:<15} {film_title[:25]:<25} {ticket.date:<12} {ticket.time:<8} {hall_name:<10} {ticket.row}/{ticket.seat:<9} {ticket.price:<8}")
    
    def show_stats(self):
        print("\n" + "-"*60)
        print("СТАТИСТИКА")
        print("-"*60)
        
        total_users = len([u for u in self.users.values() if not u.is_admin])
        total_admins = len([u for u in self.users.values() if u.is_admin])
        total_films = len(self.films)
        total_tickets = len(self.tickets)
        total_orders = len(self.food_orders)
        total_reminders = len(self.reminders)
        total_requests = len(self.hall_requests)
        
        # Выручка
        ticket_revenue = sum(t.price for t in self.tickets.values())
        food_revenue = sum(o.total for o in self.food_orders.values())
        hall_revenue = sum(r.total for r in self.hall_requests.values())
        
        print(f"Пользователей: {total_users}")
        print(f"Администраторов: {total_admins}")
        print(f"Фильмов в прокате: {total_films}")
        print(f"Продано билетов: {total_tickets}")
        print(f"Заказов еды: {total_orders}")
        print(f"Напоминаний: {total_reminders}")
        print(f"Заявок на аренду: {total_requests}")
        print("-"*40)
        print(f"Выручка с билетов: {ticket_revenue} руб.")
        print(f"Выручка с еды: {food_revenue} руб.")
        print(f"Выручка с аренды: {hall_revenue} руб.")
        print(f"ОБЩАЯ ВЫРУЧКА: {ticket_revenue + food_revenue + hall_revenue} руб.")
    
    # ========== ИНФОРМАЦИЯ ==========
    def show_info(self):
        print("\n=== КОНТАКТЫ ===")
        print("Наши ссылки:")
        print("Telegram: @mus_lady")
        print("Телефон: +7 (926) 884 12 88")
    
    # ========== СОХРАНЕНИЕ ==========
    def save_to_file(self):
        self.storage.store()
        print("Данные сохранены в файл cinema.dat")
    
    # ========== ЗАГРУЗКА ==========
    def load_from_file(self):
        if self.storage.load():
            print("Данные загружены из файла cinema.dat")
    
    # ========== ОЧИСТКА ==========
    def clear_list(self):
        confirm = self.io.input('Очистить все данные? (1 - да, 0 - нет)', '0')
        if confirm == '1':
            self.users.clear()
            self.films.clear()
            self.food.clear()
            self.halls.clear()
            self.tickets.clear()
            self.reminders.clear()
            self.hall_requests.clear()
            self.food_orders.clear()
            self.cart.clear()
            self.current_user = None
            self.next_user_id = 1
            self.next_film_id = 1
            self.next_food_id = 1
            self.next_hall_id = 1
            self.next_ticket_id = 1
            self.next_reminder_id = 1
            self.next_request_id = 1
            self.next_order_id = 1
            self.init_test_data()
            self.init_superuser()
            print("Данные очищены и восстановлены тестовые данные")


# ========== main.py ==========
def main():
    cinema = Cinema()
    cinema.load_from_file()
    
    while True:
        if not cinema.current_user:
            # Меню для неавторизованного пользователя
            print("\n" + "-"*60)
            print("КИНОТЕАТР: LOVE cinema")
            print("-"*60)
            print("1. Вход")
            print("2. Регистрация")
            print("0. Выход")
            
            try:
                choice = int(input("\nВыберите действие: "))
                
                if choice == 0:
                    cinema.save_to_file()
                    print("\nДо свидания! Ждем вас снова в LOVE cinema!")
                    sys.exit(0)
                elif choice == 1:
                    cinema.login()
                elif choice == 2:
                    cinema.register()
                else:
                    print("Неверный выбор!")
                    
            except ValueError:
                print("Введите число!")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        else:
            # Меню для авторизованного пользователя
            print("\n" + "-"*60)
            print(f"КИНОТЕАТР: LOVE cinema")
            print(f"Пользователь: {cinema.current_user.name}")
            if cinema.current_user.is_admin:
                print("АДМИНИСТРАТОР")
            print("-"*60)
            
            if cinema.current_user.is_admin:
                # Расширенное меню для администратора
                print("1. Главная страница")
                print("2. Премьера")
                print("3. Мероприятия")
                print("4. Меню и корзина")
                print("5. Профиль")
                print("6. Редактировать профиль")
                print("7. АДМИН-ПАНЕЛЬ")
                print("8. Выход")
            else:
                # Обычное меню для пользователя
                print("1. Главная страница")
                print("2. Премьера")
                print("3. Мероприятия")
                print("4. Меню и корзина")
                print("5. Профиль")
                print("6. Редактировать профиль")
                print("7. Выход")
            
            try:
                choice = int(input("\nВыберите действие: "))
                
                if cinema.current_user.is_admin:
                    # Обработка для администратора
                    if choice == 1:
                        cinema.main_page()
                    elif choice == 2:
                        cinema.premiere_page()
                    elif choice == 3:
                        cinema.events_page()
                    elif choice == 4:
                        cinema.menu_and_cart_page()
                    elif choice == 5:
                        cinema.view_profile()
                    elif choice == 6:
                        cinema.edit_profile()
                    elif choice == 7:
                        cinema.admin_dashboard()
                    elif choice == 8:
                        cinema.logout()
                    else:
                        print("Неверный выбор!")
                else:
                    # Обработка для обычного пользователя
                    if choice == 1:
                        cinema.main_page()
                    elif choice == 2:
                        cinema.premiere_page()
                    elif choice == 3:
                        cinema.events_page()
                    elif choice == 4:
                        cinema.menu_and_cart_page()
                    elif choice == 5:
                        cinema.view_profile()
                    elif choice == 6:
                        cinema.edit_profile()
                    elif choice == 7:
                        cinema.logout()
                    else:
                        print("Неверный выбор!")
                
                if (cinema.current_user.is_admin and choice != 8) or (not cinema.current_user.is_admin and choice != 7):
                    input("\nНажмите Enter для продолжения...")
                                                
            except ValueError:
                print("Введите число!")
            except Exception as e:
                print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
