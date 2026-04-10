from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sys
import os
import re
from datetime import datetime
from cinema import User


# Добавляем текущую директорию в путь, чтобы импортировать ваши модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cinema import Cinema, Ticket, User as CinemaUser, FoodOrder, HallRequest, Reminder


app = Flask(__name__)
app.config['SECRET_KEY'] = 'love_cinema_secret_key_change_in_prod'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 час

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.unauthorized_handler
def unauthorized():
    flash('Для покупки билета необходимо авторизоваться!', 'error')
    return redirect(url_for('index'))

login_manager.login_view = 'auth.login'

# Глобальный экземпляр Cinema (ваша бизнес-логика)
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

# ===== Маршруты авторизации (Blueprint в миниатюре) =====
@app.route('/')
def index():
    films = list(cinema.films.values())
    return render_template('main.html', films=films)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # GET запрос - перенаправляем на главную (страницы входа нет!)
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    # POST запрос - обработка формы
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
    # GET запрос - перенаправляем на главную
    if request.method == 'GET':
        return redirect(url_for('index'))
    
    # POST запрос - обработка формы
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    email_confirm = request.form.get('email_confirm', '').strip()
    phone = request.form.get('phone', '').strip()
    birth_date = request.form.get('birth_date', '').strip()
    agreement1 = request.form.get('agreement1')
    agreement2 = request.form.get('agreement2')
    
    # Валидация
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
    
    # Создание пользователя
    user = CinemaUser(
        id=cinema.next_user_id,
        name=name,
        phone=phone,
        email=email,
        
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

# ===== Главная страница (после входа) =====
@app.route('/main')
def main_page():
    films = list(cinema.films.values())
    return render_template('main.html', films=films)

@app.route('/profile')
@login_required
def profile():
    user = cinema.current_user
    
    # Собираем билеты текущего пользователя с данными о фильме и зале
    user_tickets = []
    for t in cinema.tickets.values():
        if t.user_id == user.id:
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


@app.route('/premiere', methods=['GET', 'POST'])
@login_required
def premiere():
    if request.method == 'POST':
        film_id = request.form.get('film_id')
        reminder_date = request.form.get('reminder_date')
        reminder_time = request.form.get('reminder_time')
        phone = request.form.get('phone', current_user.cinema_user.phone)

        if film_id and reminder_date and reminder_time:
            film = cinema.films.get(int(film_id))
            if film:
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
                cinema.reminders[cinema.next_reminder_id] = reminder
                cinema.next_reminder_id += 1
                cinema.save_to_file()
                flash('Напоминание успешно установлено!', 'success')
            else:
                flash('Фильм не найден', 'error')
        else:
            flash('Заполните все обязательные поля', 'error')
        return redirect(url_for('premiere'))

    # Подготовка данных для шаблона
    premieres = [f for f in cinema.films.values() if "премьера" in f.event.lower()]
    grouped = {}
    for f in premieres:
        grouped.setdefault(f.date_range, []).append(f)

    return render_template('premiere.html', grouped_premieres=grouped, films=cinema.films.values())

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
                # Базовая цена + наценка за опции
                base_price = hall.price_per_hour * hours
                options_price = len(options) * 500  # условно 500р за опцию
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


from flask import session

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        action = request.form.get('action')

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
                    session['cart'].append({'id': food_id, 'name': food.name, 'price': food.price, 'quantity': 1})
                session.modified = True
            return redirect(url_for('menu'))

        elif action == 'order':
            delivery_type = request.form.get('delivery_type')
            details = "Самовывоз"
            if delivery_type == 'hall':
                film = request.form.get('session_film', '')
                time = request.form.get('session_time', '')
                seat = request.form.get('session_seat', '')
                details = f"Фильм: {film}, Время: {time}, Место: {seat}"

            total = sum(item['price'] * item['quantity'] for item in session['cart'])
            order = FoodOrder(
                id=cinema.next_order_id,
                user_id=current_user.id,
                user_name=current_user.name,
                items=[(item['name'], item['quantity'], item['price']*item['quantity']) for item in session['cart']],
                total=total,
                delivery_type="доставка в зал" if delivery_type == 'hall' else "самовывоз",
                delivery_details=details
            )
            cinema.food_orders[cinema.next_order_id] = order
            cinema.next_order_id += 1
            cinema.save_to_file()
            session['cart'] = []
            session.modified = True
            flash('Заказ оформлен! Переходите к оплате.', 'success')
            return redirect(url_for('menu'))

        elif action == 'remove':
            food_id = int(request.form.get('food_id'))
            for i, item in enumerate(session['cart']):
                if item['id'] == food_id:
                    if item['quantity'] > 1:
                        session['cart'][i]['quantity'] -= 1
                    else:
                        session['cart'].pop(i)  # Удалить полностью, если 1 шт.
                    break
            session.modified = True
            return redirect(url_for('menu'))


    menu_items = list(cinema.food.values())
    cart = session.get('cart', [])
    cart_total = sum(item['price'] * item['quantity'] for item in cart)

    return render_template('menu.html', menu_items=menu_items, cart=cart, cart_total=cart_total)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('index'))

    # Обработка действий (добавить/удалить пользователя)
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
                    # Адаптируйте поля под ваш класс User, если отличаются
                    new_user = CinemaUser(
                        id=cinema.next_user_id,
                        name=name,
                        phone=phone,
                        email=email
                    )
                    # Безопасно добавляем стандартные поля, если их нет в __init__
                    for attr in ['birth_date', 'agreement1', 'agreement2']:
                        if not hasattr(new_user, attr):
                            setattr(new_user, attr, "01.01.2000" if attr == 'birth_date' else True)
                            
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

    # Сбор и обогащение данных для шаблона
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
                           food_orders=food_orders)


@app.route('/buy_ticket/<int:film_id>', methods=['GET', 'POST'])
def buy_ticket(film_id):
    if not current_user.is_authenticated:
        flash('Для покупки билета необходимо авторизоваться!', 'error')
        return redirect(url_for('index'))
    
    film = cinema.films.get(film_id)
    if not film:
        flash('Фильм не найден', 'error')
        return redirect(url_for('main_page'))
    
    # Фильтруем залы, доступные для этого фильма
    available_halls = [cinema.halls[hid] for hid in film.available_halls if hid in cinema.halls]

    if request.method == 'POST':
        hall_id = int(request.form.get('hall_id'))
        date = request.form.get('date')
        time = request.form.get('time')
        # Перенаправляем на выбор места
        return redirect(url_for('buy_seat', film_id=film_id, hall_id=hall_id, date=date, time=time))

    return render_template('buy_ticket.html', film=film, halls=available_halls)

@app.route('/buy_seat/<int:film_id>/<int:hall_id>', methods=['GET', 'POST'])
def buy_seat(film_id, hall_id):
    # 🔒 Блокировка для неавторизованных
    if not current_user.is_authenticated:
        flash('Для покупки билета необходимо авторизоваться!', 'error')
        return redirect(url_for('index'))
    
    film = cinema.films.get(film_id)
    hall = cinema.halls.get(hall_id)
    
    date = request.args.get('date')
    time = request.args.get('time')

    if request.method == 'POST':
        row = int(request.form.get('row'))
        seat = int(request.form.get('seat'))
        
        # Проверка занятости места (дубликат?)
        for t in cinema.tickets.values():
            if (t.film_id == film_id and t.hall_id == hall_id and 
                t.date == date and t.time == time and 
                t.row == row and t.seat == seat):
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
        
        flash(f'Успешно! Билет #{ticket.id} оформлен.', 'success')
        return redirect(url_for('profile'))

    return render_template('buy_seat.html', film=film, hall=hall, date=date, time=time)


#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
