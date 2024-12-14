from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State
from aiogram.dispatcher.filters.state import StatesGroup
import asyncio


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()
    activity = State()


api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(f'Привет, {message.from_user["first_name"]}! '
                         f'Я бот помогающий твоему здоровью.')
    await message.answer('Для расчета нормы калорий введите слово: "Calories"')


@dp.message_handler(text=['Calories', 'calories'])
async def set_gender(message):
    await message.answer('Введите свой пол (М или Ж):')
    await UserState.gender.set()


@dp.message_handler(state=UserState.gender)
async def set_activity(message, state):
    await state.update_data(gender=message.text.lower())
    await message.answer('Введите свой уровень активности:\n'
                         '1 - Минимальная активность\n'
                         '2 - Слабая активность\n'
                         '3 - Средняя активность\n'
                         '4 - Высокая активность\n'
                         '5 - Экстра активность')
    await UserState.activity.set()


@dp.message_handler(state=UserState.activity)
async def set_age(message, state):
    await state.update_data(activity=message.text)
    await message.answer('Введите свой возраст:')
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
    level_activity = {'1': 1.2, '2': 1.375, '3': 1.55,
                      '4': 1.725, '5': 1.9}
    if data['gender'] == 'м':
        result = ((10*data['weight'] + 6.25*data['growth'] - 5*data['age'] + 5) *
                  level_activity.setdefault(data['activity'], level_activity['1']))
    elif data['gender'] == 'ж':
        result = ((10*data['weight'] + 6.25*data['growth'] - 5*data['age'] - 161) *
                  level_activity.setdefault(data['activity'], level_activity['1']))
    else:
        result = None
    if result:
        await message.answer(f'Ваша норма калорий: {round(result, 2)}')
    else:
        await message.answer('Произошла ошибка. Повторите попытку. Введите команду /start')

    await state.finish()


@dp.message_handler()
async def all_messages(message):
    # print('Введите команду /start, чтобы начать общение.')
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
