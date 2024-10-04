from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.input_file import InputFile

from crud_functions import *
from keyboards import *


api = '______'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


initiate_db()
get_all_products()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.reply('Привет! Я бот помогающий твоему здоровью.'
                        '\nВыберите, что Вы хотите сделать:'
                        '\n',reply_markup=start_kb)


@dp.message_handler(text='Рассчитать', state='*')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=menu_kb)


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()



@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))
    calories = (10 * weight) + (6.25 * growth) - (5 * age) - 161
    await message.answer(f'Ваша норма калорий: {calories}')
    await state.finish()




@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула Миффлина-Сан Жеора для расчёта нормы калорий:\n'
                               'Калории = (10 * вес) + (6.25 * рост) - (5 * возраст) - 161')
    await call.answer()




@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = get_all_products()
    for i in range(len(products)):
        photo = InputFile(f'./files/prod{i + 1}.jpg')
        await message.answer_photo(photo=photo, caption=f'Название: {products[i][1]} | \n'
                                                        f'Описание: {products[i][2]} | \n'
                                                        f'Цена: {products[i][3]}')
    await message.answer('Выберите продукт для покупки:', reply_markup=product_kb)



@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer(text='Вы успешно приобрели продукт!')
    await call.answer()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):

    if is_included(message.text):
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()

    else:
        await state.update_data(username=str(message.text))
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=str(message.text))
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=int(message.text))
    user = await state.get_data()
    add_user(user['username'], user['email'], user['age'])
    await state.finish()
    await message.answer('Регистрация прошла успешно')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)



