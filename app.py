from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import sys
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import datetime
from flask import jsonify

def parse_date_range(date_range_str):
    """Парсит диапазон дат и возвращает первую дату"""
    try:
        # Формат: "15.06-28.06"
        match = re.match(r'(\d{2})\.(\d{2})', date_range_str)
        if match:
            day, month = match.groups()
            return datetime(2026, int(month), int(day))
    except:
        pass
    return None

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cinema import Cinema, User as CinemaUser, FoodOrder, HallRequest, Reminder, Ticket

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'love_cinema_secret_key_change_in_prod')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# ===== СЛОВАРЬ МЕСЯЦЕВ И ФУНКЦИЯ ФОРМАТИРОВАНИЯ =====
MONTHS = {
    '01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
    '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
    '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'
}

def format_premiere_date(date_range_str):
    """Превращает '15.06-28.06' в 'С 15 июня!'"""
    try:
        # Берем первую часть (до тире)
        start_date = date_range_str.split('-')[0]
        day, month = start_date.split('.')
        return f"С {int(day)} {MONTHS[month]}!"
    except:
        return date_range_str

# ===== ДЕЛАЕМ ФУНКЦИЮ ДОСТУПНОЙ В ШАБЛОНАХ =====
app.jinja_env.globals['format_premiere_date'] = format_premiere_date


# 🔗 ССЫЛКА НА ОПЛАТУ 
PAYMENT_LINK = "https://www.tinkoff.ru/rm/r_BleCAybEsC.ZirtaPyZfs/Lwo3R19320"

# Middleware для поддержки PATCH и DELETE в формах
@app.before_request
def method_override():
    """Позволяет использовать PATCH и DELETE через скрытое поле _method в формах"""
    if request.method == 'POST' and '_method' in request.form:
        method = request.form['_method'].upper()
        if method in ['PATCH', 'DELETE', 'PUT']:
            request.method = method

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    flash('Для покупки билета необходимо авторизоваться!', 'error')
    return redirect(url_for('index'))

login_manager.login_view = 'index'

# Глобальный экземпляр Cinema
cinema = Cinema()
cinema.load_from_file()

# Адаптер пользователя для Flask-Login
class FlaskUser(UserMixin):
    def __init__(self, cinema_user):
        self.cinema_user = cinema_user
        self.id = cinema_user.id
        self.name = cinema_user.name
        self.is_admin = cinema_user.is_admin
    
    def get_phone(self):
        return self.cinema_user.phone

@login_manager.user_loader
def load_user(user_id):
    user = cinema.users.get(int(user_id))
    if user:
        return FlaskUser(user)
    return None


# Хелпер для работы с Москвой
MSK = ZoneInfo("Europe/Moscow")

def validate_date_time(date_str, time_str):
    """Проверка формата и адекватности даты/времени (МСК)"""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
        dt_msk = dt.replace(tzinfo=MSK)
        now_msk = datetime.now(MSK)
        
        if dt_msk.year != 2026:
            return False, "Год должен быть 2026"
        if dt_msk < now_msk:
            return False, "Дата/время не могут быть в прошлом"
        return True, dt_msk
    except ValueError:
        return False, "Неверный формат даты или времени"


# ===== МАРШРУТЫ =====

@app.route('/')
def index():
    # Берем ВСЕ фильмы
    all_films = list(cinema.films.values())
    
    # ФИЛЬТРУЕМ: убираем премьеры, оставляем только обычные фильмы
    main_films = [f for f in all_films if "премьера" not in f.event.lower()]
    
    return render_template('main.html', films=main_films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    phone = request.form.get('phone', '').strip()
    code = request.form.get('code', '').strip()
    
    if not phone:
        flash('Введите номер телефона', 'error')
        return redirect(url_for('index'))
    
    if not code:
        flash('Введите код', 'error')
        return redirect(url_for('index'))
    
    for user in cinema.users.values():
        if user.phone == phone:
            expected_code = '0812' if user.is_admin else '1288'
            if code == expected_code:
                flask_user = FlaskUser(user)
                login_user(flask_user)
                cinema.current_user = user
                cinema.save_to_file()
                flash('Добро пожаловать!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный код подтверждения', 'error')
                return redirect(url_for('index'))
    
    flash('Пользователь с таким номером не найден', 'error')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    email_confirm = request.form.get('email_confirm', '').strip()
    phone = request.form.get('phone', '').strip()
    birth_date = request.form.get('birth_date', '').strip()
    agreement1 = request.form.get('agreement1')
    agreement2 = request.form.get('agreement2')
    
    if not name or not re.match(r'^[а-яА-ЯёЁ\s]+$', name):
        flash('Имя должно содержать только русские буквы', 'error')
        return redirect(url_for('index'))
    
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        flash('Неверный формат email', 'error')
        return redirect(url_for('index'))
    
    if email != email_confirm:
        flash('Email не совпадает', 'error')
        return redirect(url_for('index'))
    
    if not phone or not re.match(r'^[0-9+\-\s]+$', phone):
        flash('Телефон должен содержать только цифры', 'error')
        return redirect(url_for('index'))
    
    for user in cinema.users.values():
        if user.phone == phone:
            flash('Пользователь с таким номером уже существует', 'error')
            return redirect(url_for('index'))
    
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birth_date):
        flash('Используйте формат даты дд.мм.гггг', 'error')
        return redirect(url_for('index'))
    
    if not (agreement1 and agreement2):
        flash('Необходимо согласие с правилами', 'error')
        return redirect(url_for('index'))
    
    user = CinemaUser(
        id=cinema.next_user_id,
        name=name,
        phone=phone,
        email=email
    )
    user.birth_date = birth_date
    user.agreement1 = True
    user.agreement2 = True
    user.is_admin = False
    
    cinema.users[cinema.next_user_id] = user
    cinema.next_user_id += 1
    cinema.current_user = user
    cinema.save_to_file()
    
    flask_user = FlaskUser(user)
    login_user(flask_user)
    
    flash('Регистрация успешно завершена!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    cinema.current_user = None
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/main')
def main_page():
    films = list(cinema.films.values())
    return render_template('main.html', films=films)

@app.route('/profile')
@login_required
def profile():
    user = cinema.users.get(current_user.id)
    
    user_tickets = []
    for t in cinema.tickets.values():
        if t.user_id == user.id and t.status != 'returned':  # ← Только активные!
            film = cinema.films.get(t.film_id)
            hall = cinema.halls.get(t.hall_id)
            user_tickets.append({
                'id': t.id,
                'film_title': film.title if film else 'Неизвестно',
                'date': t.date,
                'time': t.time,
                'hall': hall.name if hall else 'Неизвестно',
                'row': t.row,
                'seat': t.seat,
                'price': t.price
            })
            
    return render_template('profile.html', user=user, tickets=user_tickets)

@app.route('/profile/edit', methods=['POST', 'PATCH'])
@login_required
def edit_profile():
    user = cinema.users.get(current_user.id)
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('profile'))
    
    new_name = request.form.get('name', '').strip()
    new_phone = request.form.get('phone', '').strip()
    new_email = request.form.get('email', '').strip()
    
    if new_name and not re.match(r'^[а-яА-ЯёЁ\s]+$', new_name):
        flash('Имя должно содержать только русские буквы', 'error')
        return redirect(url_for('profile'))
    if new_email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
        flash('Неверный формат email', 'error')
        return redirect(url_for('profile'))
    if new_phone and not re.match(r'^[0-9+\-\s]+$', new_phone):
        flash('Телефон должен содержать только цифры', 'error')
        return redirect(url_for('profile'))
        
    if new_name: user.name = new_name
    if new_phone: user.phone = new_phone
    if new_email: user.email = new_email
    cinema.save_to_file()
    flash('Данные профиля успешно обновлены!', 'success')
    return redirect(url_for('profile'))


@app.route('/ticket/<int:ticket_id>', methods=['POST', 'DELETE'])
@login_required
def cancel_ticket(ticket_id):
    ticket = cinema.tickets.get(ticket_id)
    if ticket and ticket.user_id == current_user.id:
        ticket.status = 'returned'  # Меняем статус, не удаляем из базы
        cinema.save_to_file()
        flash('Билет успешно возвращен', 'success')
    else:
        flash('Не удалось вернуть билет', 'error')
    return redirect(url_for('profile'))

@app.route('/premiere', methods=['GET', 'POST'])
@login_required
def premiere():
    if request.method == 'POST':
        film_id = request.form.get('film_id')
        reminder_date = request.form.get('reminder_date')
        reminder_time = request.form.get('reminder_time')
        phone = request.form.get('phone', current_user.cinema_user.phone if current_user.is_authenticated else '')

        if film_id and reminder_date and reminder_time:
            film = cinema.films.get(int(film_id))
            if film:
                reminder = Reminder(
                    id=cinema.next_reminder_id,
                    user_id=current_user.id if current_user.is_authenticated else 0,
                    user_name=current_user.name if current_user.is_authenticated else 'Гость',
                    phone=phone,
                    film_id=int(film_id),
                    film_title=film.title,
                    date=reminder_date,
                    time=reminder_time
                )
                cinema.reminders[cinema.next_reminder_id] = reminder
                cinema.next_reminder_id += 1
                cinema.save_to_file()
                flash('Напоминание успешно установлено!', 'success')
            else:
                flash('Фильм не найден', 'error')
        else:
            flash('Заполните все обязательные поля', 'error')
        return redirect(url_for('premiere'))

    # Получаем все фильмы с типом "премьера"
    all_premieres = [f for f in cinema.films.values() if "премьера" in f.event.lower()]
    
    # Фильтруем: показываем только фильмы, первая дата которых > СЕГОДНЯ (19.04.2026)
    today = datetime.now()
    filtered_premieres = []
    for film in all_premieres:
        first_date = parse_date_range(film.date_range)
        if first_date and first_date > today:
            filtered_premieres.append(film)
    
    # Группируем по диапазону дат
    grouped = {}
    for f in filtered_premieres:
        grouped.setdefault(f.date_range, []).append(f)

    return render_template('premiere.html', grouped_premieres=grouped, films=filtered_premieres)

@app.route('/set_reminder', methods=['POST'])
@login_required
def set_reminder():
    film_id = request.form.get('film_id')
    reminder_date = request.form.get('reminder_date')
    reminder_time = request.form.get('reminder_time')
    phone = request.form.get('phone', '').strip()

    # Валидация полей
    if not all([film_id, reminder_date, reminder_time, phone]):
        flash('Заполните все обязательные поля', 'error')
        return redirect(url_for('premiere'))

    film = cinema.films.get(int(film_id))
    if not film:
        flash('Фильм не найден', 'error')
        return redirect(url_for('premiere'))

    # Создаем объект напоминания (используем класс из cinema.py)
    reminder = Reminder(
        id=cinema.next_reminder_id,
        user_id=current_user.id,
        user_name=current_user.name,
        phone=phone,
        film_id=int(film_id),
        film_title=film.title,
        date=reminder_date,
        time=reminder_time
    )

    # Сохраняем в базу
    cinema.reminders[cinema.next_reminder_id] = reminder
    cinema.next_reminder_id += 1
    cinema.save_to_file()

    flash('Напоминание успешно установлено!', 'success')
    return redirect(url_for('premiere'))


@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    if request.method == 'POST':
        hall_id = request.form.get('hall_id')
        people = int(request.form.get('people', 0))
        hours = int(request.form.get('hours', 0))
        options = request.form.getlist('options')
        notes = request.form.get('notes', '')
        
        if hall_id and hours > 0:
            hall = cinema.halls.get(int(hall_id))
            if hall:
                base_price = hall.price_per_hour * hours
                options_price = len(options) * 500
                total = base_price + options_price
                
                req = HallRequest(
                    id=cinema.next_request_id,
                    user_id=current_user.id,
                    user_name=current_user.name,
                    phone=current_user.cinema_user.phone,
                    hall_id=int(hall_id),
                    hall_name=hall.name,
                    hours=hours,
                    total=total,
                    notes=f"Людей: {people}, Опции: {', '.join(options)}; {notes}"
                )
                cinema.hall_requests[cinema.next_request_id] = req
                cinema.next_request_id += 1
                cinema.save_to_file()
                flash(f'Заявка принята! Итого: {total} руб.', 'success')
            else:
                flash('Зал не найден', 'error')
        else:
            flash('Заполните обязательные поля', 'error')
        return redirect(url_for('events'))
    
    halls_list = list(cinema.halls.values())
    return render_template('events.html', halls=halls_list)



@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    if 'cart' not in session:
        session['cart'] = []

    # ==================== POST-ЗАПРОСЫ ====================
    if request.method == 'POST':
        action = request.form.get('action')

        # ➕ Добавление товара
        if action == 'add':
            food_id = int(request.form.get('food_id'))
            if food_id in cinema.food:
                food = cinema.food[food_id]
                found = False
                for item in session['cart']:
                    if item['id'] == food_id:
                        item['quantity'] += 1
                        found = True
                        break
                if not found:
                    session['cart'].append({
                        'id': food_id, 
                        'name': food.name, 
                        'price': food.price, 
                        'quantity': 1
                    })
                session.modified = True
            return redirect(url_for('menu'))

        # ➖ Удаление товара
        elif action == 'remove':
            food_id = int(request.form.get('food_id'))
            for i, item in enumerate(session['cart']):
                if item['id'] == food_id:
                    if item['quantity'] > 1:
                        session['cart'][i]['quantity'] -= 1
                    else:
                        session['cart'].pop(i)
                    break
            session.modified = True
            return redirect(url_for('menu'))

        # 💳 Оформление заказа
        elif action == 'order':
            try:
                delivery_type = request.form.get('delivery_type', 'self')
                details = "Самовывоз"
                
                if delivery_type == 'hall':
                    details = (f"Фильм: {request.form.get('session_film')}, "
                               f"Дата: {request.form.get('session_date')}, "
                               f"Время: {request.form.get('session_time')}, "
                               f"Место: {request.form.get('session_seat')}")

                # Безопасный расчёт суммы
                cart = session.get('cart', [])
                total = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart)

                # Создание заказа
                from cinema import FoodOrder
                order = FoodOrder(
                    id=cinema.next_order_id,
                    user_id=current_user.id,
                    user_name=current_user.name,
                    items=[(item['name'], item['quantity'], item['price']*item['quantity']) for item in cart],
                    total=total,
                    delivery_type="доставка в зал" if delivery_type == 'hall' else "самовывоз",
                    delivery_details=details
                )
                
                cinema.food_orders[cinema.next_order_id] = order
                cinema.next_order_id += 1
                cinema.save_to_file()
                
                session['cart'] = []
                session.modified = True

                # ✅ Если это AJAX-запрос — возвращаем JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True, 
                        'payment_url': 'https://www.tinkoff.ru'
                    })
                
                # ✅ Обычный редирект для не-AJAX
                flash('Заказ оформлен! Переходите к оплате.', 'success')
                return redirect('https://www.tinkoff.ru')

            except Exception as e:
                print(f"🔥 ОШИБКА В /menu: {e}")
                import traceback
                traceback.print_exc()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': str(e)}), 500
                flash(f'Ошибка оформления заказа: {e}', 'error')
                return redirect(url_for('menu'))

    # ==================== GET-ЗАПРОС ====================
    # Подготовка данных для шаблона
    menu_items = list(cinema.food.values())
    cart = session.get('cart', [])
    cart_total = sum(item['price'] * item['quantity'] for item in cart)
    
    # ✅ Список ID фильмов, на которые у пользователя есть активные билеты
    user_ticket_film_ids = []
    for t in cinema.tickets.values():
        if t.user_id == current_user.id and t.status == 'active':
            if t.film_id not in user_ticket_film_ids:
                user_ticket_film_ids.append(t.film_id)
                
    # ✅ Данные всех фильмов для JS (чтобы брать даты)
    films_data = [
        {'id': f.id, 'title': f.title, 'date_range': f.date_range} 
        for f in cinema.films.values()
    ]
    
    return render_template('menu.html', 
                          menu_items=menu_items, 
                          cart=cart, 
                          cart_total=cart_total,
                          user_ticket_film_ids=user_ticket_film_ids,
                          films_data=films_data)

@app.route('/buy_ticket/<int:film_id>', methods=['GET', 'POST'])
def buy_ticket(film_id):
    if not current_user.is_authenticated:
        flash('Для покупки билета необходимо авторизоваться!', 'error')
        return redirect(url_for('index'))
    
    film = cinema.films.get(film_id)
    if not film:
        flash('Фильм не найден', 'error')
        return redirect(url_for('index'))
    
    available_halls = [cinema.halls[hid] for hid in film.available_halls if hid in cinema.halls]

    if request.method == 'POST':
        hall_id = int(request.form.get('hall_id'))
        date = request.form.get('date')
        time = request.form.get('time')
        return redirect(url_for('buy_seat', film_id=film_id, hall_id=hall_id, date=date, time=time))

    return render_template('buy_ticket.html', film=film, halls=available_halls)


from flask import jsonify  # ← Добавьте в импорты

@app.route('/buy_seat/<int:film_id>/<int:hall_id>', methods=['GET', 'POST'])
def buy_seat(film_id, hall_id):
    if not current_user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Необходима авторизация'}), 401
        flash('Для покупки билета необходимо авторизоваться!', 'error')
        return redirect(url_for('index'))
    
    film = cinema.films.get(film_id)
    hall = cinema.halls.get(hall_id)
    
    if not film or not hall:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Фильм или зал не найден'}), 404
        flash('Фильм или зал не найден', 'error')
        return redirect(url_for('index'))
    
    date = request.args.get('date')
    time = request.args.get('time')

    if request.method == 'POST':
        row = int(request.form.get('row'))
        seat = int(request.form.get('seat'))
        
        # Проверка занятости места
        for t in cinema.tickets.values():
            if (t.film_id == film_id and t.hall_id == hall_id and 
                t.date == date and t.time == time and 
                t.row == row and t.seat == seat):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Место уже занято'}), 409
                flash('Это место уже занято!', 'error')
                return redirect(url_for('buy_seat', film_id=film_id, hall_id=hall_id, date=date, time=time))
        
        # Расчёт цены
        price = 350
        if hall.name == "VIP зал":
            price = 700
        else:
            price = 350 + (hall.capacity // 10) * 50
            
        # Создание билета
        ticket = Ticket(
            id=cinema.next_ticket_id,
            user_id=current_user.id,
            film_id=film_id,
            hall_id=hall_id,
            date=date,
            time=time,
            row=row,
            seat=seat,
            price=price
        )
        cinema.tickets[cinema.next_ticket_id] = ticket
        cinema.next_ticket_id += 1
        cinema.save_to_file()
        
        # ✅ ВОЗВРАЩАЕМ JSON ВМЕСТО REDIRECT
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'payment_url': 'https://www.tbank.ru/'  # ← ЗАМЕНИТЕ!
            })
        
        # Для обычных запросов (без AJAX)
        flash('Билет успешно куплен! Открываем оплату...', 'success')
        return redirect('https://www.tbank.ru/')

    return render_template('buy_seat.html', film=film, hall=hall, date=date, time=time)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_user':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            is_admin = request.form.get('is_admin') == 'on'
            
            if name and phone:
                if any(u.phone == phone for u in cinema.users.values()):
                    flash('Пользователь с таким номером уже существует', 'error')
                else:
                    new_user = CinemaUser(
                        id=cinema.next_user_id,
                        name=name,
                        phone=phone,
                        email=email
                    )
                    new_user.is_admin = is_admin
                    if not hasattr(new_user, 'birth_date'):
                        new_user.birth_date = "01.01.2000"
                    if not hasattr(new_user, 'agreement1'):
                        new_user.agreement1 = True
                    if not hasattr(new_user, 'agreement2'):
                        new_user.agreement2 = True
                        
                    cinema.users[new_user.id] = new_user
                    cinema.next_user_id += 1
                    cinema.save_to_file()
                    flash('Пользователь успешно добавлен', 'success')
            else:
                flash('Заполните имя и телефон', 'error')
                
        elif action == 'delete_user':
            user_id = int(request.form.get('user_id'))
            if user_id in cinema.users:
                if user_id == current_user.id:
                    flash('Нельзя удалить самого себя', 'error')
                else:
                    del cinema.users[user_id]
                    cinema.save_to_file()
                    flash('Пользователь удалён', 'success')
            else:
                flash('Пользователь не найден', 'error')
                
        return redirect(url_for('admin_panel'))

    users = list(cinema.users.values())
    
    tickets = []
    for t in cinema.tickets.values():
        u = cinema.users.get(t.user_id)
        f = cinema.films.get(t.film_id)
        h = cinema.halls.get(t.hall_id)
        tickets.append({
            **t.__dict__,
            'user_name': u.name if u else 'Удалён',
            'film_title': f.title if f else '?',
            'hall_name': h.name if h else '?'
        })

    reminders = list(cinema.reminders.values())
    hall_requests = list(cinema.hall_requests.values())
    food_orders = list(cinema.food_orders.values())

    stats = {
        'users': len(users),
        'tickets': len(tickets),
        'reminders': len(reminders),
        'requests': len(hall_requests),
        'orders': len(food_orders),
        'revenue': sum(t['price'] for t in tickets) + sum(o.total for o in food_orders)
    }

    return render_template('admin.html',
                           stats=stats,
                           users=users,
                           tickets=tickets,
                           reminders=reminders,
                           hall_requests=hall_requests,
                           food_orders=food_orders,
                           films=cinema.films.values())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
