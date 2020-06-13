import asyncio
import logging
import time
import aiohttp
import requests
import random
from aiogram.types import InlineQueryResultArticle, InlineQuery, InputTextMessageContent, inline_keyboard
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types, exceptions
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

import keyboard as kb
import config as cfg

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('broadcast')

# Initialize bot and dispatcher
loop = asyncio.get_event_loop()
bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
url = "https://likefilmdb.ru/"


async def get_html(url):
    timeout = aiohttp.ClientTimeout(total=30)
    ua = 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers={'User-Agent': ua},
                                     timeout=timeout) as session:
        async with session.request('get', url) as responce:
            return await responce.content.read()


@dp.message_handler(commands=['start'])
async def welcome(message):
    await bot.send_message(message.chat.id,
                           "Хеллоу, {0.first_name}!\n Я - <b> {1} </b>, бот для любителей кино".format(
                               message.from_user,
                               'Раб (помогите мне, меня заставляют работать бесплатно , именно поэтому я раб)'),
                           parse_mode='html', reply_markup=kb.main_menu_ru)


@dp.message_handler(lambda message: message.text == 'Фильмы')
async def films(message):
    await bot.send_message(message.chat.id, 'Ура, вы нашли раздел с <b>Фильмами</b>', parse_mode='html',
                           reply_markup=kb.film_menu)


@dp.message_handler(lambda message: message.text == 'Сериалы')
async def films(message):
    await bot.send_message(message.chat.id, 'Ура, вы нашли раздел с <b>Сериалами</b>', parse_mode='html',
                           reply_markup=kb.series_menu)


@dp.message_handler(lambda message: message.text == 'Случайный фильм')
async def films(message):
    await bot.send_message(message.chat.id, 'Ура, вы нашли раздел со <b>Случайными фильмами</b>', parse_mode='html',
                           reply_markup=kb.random_menu)


@dp.message_handler(lambda message: message.text == 'Случайный сериал')
async def films(message):
    await bot.send_message(message.chat.id, 'Ура, вы нашли раздел со <b>Случайными сериалами</b>', parse_mode='html',
                           reply_markup=kb.random_menu_series)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('random_film'))  # случайные фильмы
async def bests_films_year(inline_query: InlineQuery):
    result = await get_inline_films_href('/service/movies/rand/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=10)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('random_series'))  # случайные сериалы
async def bests_films_year(inline_query: InlineQuery):
    result = await get_inline_series_href('/service/tv-series/rand/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=10)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('best_films'))  # лучшие фильмы
async def bests_films_year(inline_query: InlineQuery):
    result = await get_inline_films_href('/service/movies/best/year/2020/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('best_series'))  # лучшие сериалы
async def bests_series_year(inline_query: InlineQuery):
    result = await get_inline_series_href('/service/tv-series/best/year/2020/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('new_films'))  # новые фильмы
async def new_films(inline_query: InlineQuery):
    result = await get_inline_films_href('/service/movies/new/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('new_series'))  # новые сериалы
async def new_films(inline_query: InlineQuery):
    result = await get_inline_series_href('/service/tv-series/new/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('by-category_'))  # категории фильмов
async def category_films(inline_query: InlineQuery):
    href = inline_query.query.split('_')[1]
    result = await get_inline_films_href(href)
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('ser-category_'))  # категории сериалов
async def category_series(inline_query: InlineQuery):
    href = inline_query.query.split('_')[1]
    result = await get_inline_series_href(href)
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('similar_'))  # похожие фильмы
async def add_order_to_db_film(inline_query: InlineQuery):
    href = inline_query.query.split('_')[1]
    result = await get_inline_films_href(href + 'similar/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('pohozhie-serialy_'))  # похожие сериалы
async def add_order_to_db_serial(inline_query: InlineQuery):
    href = inline_query.query.split('_')[1]
    result = await get_inline_series_href(href + 'pohozhie-serialy/')
    await bot.answer_inline_query(inline_query.id, results=result, cache_time=600)


@dp.callback_query_handler(lambda call: call.data.startswith('trailer_'))  #
async def get_trailer(call):
    href = call.data.split('_')[1]
    soup = BeautifulSoup(requests.get(url + href).text, 'lxml')
    tmp = soup.find('div', {'class': 'uiSectionV2Media'})
    play_button = tmp.find('a', {'href': '#'})
    trailer_link = str(play_button).split(',')[2].split('\'')[1][2:]
    await bot.send_message(call.from_user.id, trailer_link)


@dp.message_handler(lambda message: message.text == 'Я киноман?')
async def random_value(message):
    number = random.randint(1, 2)
    num = random.randint(1, 100)
    if number == 1:
        await bot.send_message(message.chat.id,
                               f'Я, как знаток в фильмах, а это знают <b>ВСЕ</b>, '
                               f'с уверенностью заявляю, что ты киноман на {num} %',
                               parse_mode='html')
    if number == 2:
        await bot.send_message(message.chat.id,
                               'Я, как знаток в фильмах, а это знают <b>ВСЕ</b>, '
                               f'с уверенностью заявляю, что киноман из тебя никакой!',
                               parse_mode='html')


async def get_inline_films_href(href):
    soup = BeautifulSoup(requests.get(url + href).text, 'lxml')
    best_films = soup.find_all('div', 'uiSectionV8Content')
    result = []
    counter = 0
    for film in best_films:
        if counter == 12:
            break
        film = film.find('a', 'uiH2')
        film_href = film.get('href')
        try:
            item_desctiption, film_image = get_film_content(film_href)
        except Exception:
            pass
        message = InputTextMessageContent(item_desctiption, parse_mode='html')
        film_insert = film.next
        keyboard = kb.generate_film_keyboard(film_href)
        result.append(
            InlineQueryResultArticle(
                id=str(counter),
                title=film_insert,
                thumb_url=film_image,
                thumb_height=500, thumb_width=500,
                input_message_content=message,
                reply_markup=keyboard
            )
        )
        counter += 1
    return result


async def get_inline_series_href(href):
    soup = BeautifulSoup(requests.get(url + href).text, 'lxml')
    best_films = soup.find_all('div', 'uiSectionV8Content')
    result = []
    counter = 0
    for film in best_films:
        if counter == 12:
            break
        film = film.find('a', 'uiH2')
        film_href = film.get('href')
        try:
            item_desctiption, film_image = get_film_content(film_href)
        except Exception:
            pass
        message = InputTextMessageContent(item_desctiption, parse_mode='html')
        film_insert = film.next
        keyboard = kb.generate_series_keyboard(film_href)
        result.append(
            InlineQueryResultArticle(
                id=str(counter),
                title=film_insert,
                thumb_url=film_image,
                thumb_height=500, thumb_width=500,
                input_message_content=message,
                reply_markup=keyboard
            )
        )
        counter += 1
    return result


@dp.callback_query_handler(lambda call: call.data.startswith('categories_'))
async def get_films_categories(call):
    tel_id = call.from_user.id
    current_pos = int(call.data.split('_')[1])
    href = 'service/movies/what-to-see/'
    soup = BeautifulSoup(requests.get(url + href).text, 'lxml')
    film_categories = soup.find_all('div', {'class': 'simpleMovie'})
    k = inline_keyboard.InlineKeyboardMarkup()
    counter = current_pos
    while counter <= len(film_categories):
        if counter == current_pos + 8 or counter == len(film_categories):
            break
        category_href = film_categories[counter].find('a').get('href')
        category_name = film_categories[counter].find('img').get('alt')
        k.add(inline_keyboard.InlineKeyboardButton(str(counter + 1) + ') ' + category_name,
                                                   switch_inline_query_current_chat='by-category_{0}'.format(
                                                       category_href)))
        counter += 1
    if current_pos >= 8:
        call_data_previous = 'categories_{0}'.format(current_pos - 8)
        k.add(inline_keyboard.InlineKeyboardButton('Previous⬅️', callback_data=call_data_previous))
    if len(film_categories) > current_pos + 8:
        call_data_more = 'categories_{0}'.format(current_pos + 8)
        k.add(inline_keyboard.InlineKeyboardButton('Next \U000027a1', callback_data=call_data_more))
    await bot.edit_message_text('Выберите категорию фильмов', tel_id, call.message.message_id, reply_markup=k)


@dp.callback_query_handler(lambda call: call.data.startswith('categories-series'))
async def get_serial_categories(call):
    tel_id = call.from_user.id
    current_pos = int(call.data.split('_')[1])
    href = 'service/tv-series/what-to-see/'
    soup = BeautifulSoup(requests.get(url + href).text, 'lxml')
    film_categories = soup.find_all('div', {'class': 'simpleMovie'})
    k = inline_keyboard.InlineKeyboardMarkup()
    counter = current_pos
    while counter <= len(film_categories):
        if counter == current_pos + 8 or counter == len(film_categories):
            break
        category_href = film_categories[counter].find('a').get('href')
        category_name = film_categories[counter].find('img').get('alt')
        k.add(inline_keyboard.InlineKeyboardButton(str(counter + 1) + ') ' + category_name,
                                                   switch_inline_query_current_chat='ser-category_{0}'.format(
                                                       category_href)))
        counter += 1
    if current_pos >= 8:
        call_data_previous = 'categories-series_{0}'.format(current_pos - 8)
        k.add(inline_keyboard.InlineKeyboardButton('Previous⬅', callback_data=call_data_previous))
    if len(film_categories) > current_pos + 8:
        call_data_more = 'categories-series_{0}'.format(current_pos + 8)
        k.add(inline_keyboard.InlineKeyboardButton('Next \U000027a1', callback_data=call_data_more))
    await bot.edit_message_text('Выберите категорию сериалов', tel_id, call.message.message_id, reply_markup=k)


def get_film_content(href):
    link = url + href
    soup = BeautifulSoup(requests.get(link).text, 'lxml')
    film_title = soup.find('div', {'itemtype': 'http://schema.org/Movie'}).next.next
    print(film_title)
    text = f'<b>{film_title}</b>\n\n'
    film_content = soup.find_all('div', 'uiSectionV2Content')[0]
    text += 'Cюжет\n'
    text += film_content.find('div', {'itemprop': 'description'}).text
    text += '\n\n'
    film_image = url + soup.find_all('div', 'uiSectionV2Wrapper')[0].find('div', 'uiSectionV2Preview').find('img').get(
        'src')
    film_table = soup.find('table', {'class': 'uiStandartVarList'}).find_all('tr')
    table_rows = ''
    for row in film_table:
        table_rows += row.find_all('td')[0].text + ' '
        table_rows += row.find_all('td')[1].text + '\n'
    text += table_rows
    text += f'''<a href="{film_image}">Photo</a>'''
    return text, film_image


if __name__ == '__main__':
    executor.start_polling(dp)
