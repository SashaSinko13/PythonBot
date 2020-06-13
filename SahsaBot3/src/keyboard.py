from aiogram.types import reply_keyboard, InlineKeyboardButton, InlineKeyboardMarkup, inline_keyboard

main_menu_ru = reply_keyboard.ReplyKeyboardMarkup([['Я киноман?'],
                                                   ['Фильмы', 'Сериалы'],
                                                   ['Случайный фильм', 'Случайный сериал']])


best_films_button = InlineKeyboardButton('Лучшее фильмы 2020 года', switch_inline_query_current_chat='best_films')
new_films_button = InlineKeyboardButton('Новые фильмы', switch_inline_query_current_chat='new_films')
categories_films = InlineKeyboardButton('Фильмы по категориям', callback_data='categories_0')
film_menu = InlineKeyboardMarkup().add(best_films_button).add(new_films_button).add(categories_films)


best_series_button = InlineKeyboardButton('Лучшее сериалы 2020 года', switch_inline_query_current_chat='best_series')
new_series_button = InlineKeyboardButton('Новые сериалы', switch_inline_query_current_chat='new_series')
choose_series_button = InlineKeyboardButton('Сериалы по категориям', callback_data='categories-series_0')
series_menu = InlineKeyboardMarkup().add(best_series_button).add(new_series_button).add(choose_series_button)


random_film_button = InlineKeyboardButton('\U00002753Выбрать случайный фильм\U00002753', switch_inline_query_current_chat='random_film')
random_menu = InlineKeyboardMarkup().add(random_film_button)


random_series_button = InlineKeyboardButton('\U00002753Выбрать случайный сериал\U00002753', switch_inline_query_current_chat='random_series')
random_menu_series = InlineKeyboardMarkup().add(random_series_button)


def generate_film_keyboard(href):
    if len(href) < 55:
        trailer_button = InlineKeyboardButton('Трейлер', callback_data=f'trailer_{href}')
        similar_button_film = InlineKeyboardButton('Похожие фильмы', switch_inline_query_current_chat=f'similar_{href}')
        return InlineKeyboardMarkup().add(trailer_button).add(similar_button_film)
    else:
        return film_menu


def generate_series_keyboard(href):
    if len(href) < 55:
        trailer_button = InlineKeyboardButton('Трейлер', callback_data=f'trailer_{href}')
        similar_button_series = InlineKeyboardButton('Похожие сериалы', switch_inline_query_current_chat=f'pohozhie-serialy_{href}')
        return InlineKeyboardMarkup().add(trailer_button).add(similar_button_series)
    else:
        return series_menu


def orders_by_phone(films, current_pos=0):
    k = inline_keyboard.InlineKeyboardMarkup()
    counter = 1
    for film in films:
        k.add(inline_keyboard.InlineKeyboardButton(film, switch_inline_query_current_chat='order_{0}'.format(film)))
        if counter == current_pos+5:
            break
        counter += 1

    more = 'Показать еще ⬇️'

    if len(films) > current_pos + 5:
        call_data_more = 'more_orders_{0}|{1}'.format(phone, current_pos + 5)
        k.add(inline_keyboard.InlineKeyboardButton(more, callback_data=call_data_more))

    return k
