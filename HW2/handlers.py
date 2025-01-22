from aiogram import  types, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from states import Profile, LogData
from utils import main_temp, get_water_cal, get_calorie_cal, get_calories_info, translate_text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router_prof = Router()
router_log = Router()

DATA = {}
FOOD = "nutrients"
EXERCISES = "exercise"


async def is_profile(message, state):
    if not  await state.get_data():
       await message.answer(f"Сначало заполните профиль")
    else: return True


# Хэндлер на команду /start
@router_prof.message(Command("start"))
async def cmd_start(message: types.Message):
    name = message.from_user.first_name
    await message.answer(f"Hello!, my dear {name} {message.from_user.last_name if message.from_user.last_name else ""}!")
    await message.answer(f"{name}, нужно заполнить Ваш профиль, введите команду /set_profile")

@router_prof.message(Command("set_profile"))
async def start_profile(message: types.Message, state=FSMContext):
    await state.set_state(Profile.age)
    await message.answer("Введите ваш возраст")

@router_prof.message(Profile.age)
async def profile_age(message: types.Message, state=FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Profile.weight)
    await message.answer("Введите ваш вес (в кг)")

@router_prof.message(Profile.weight)
async def profile_weight(message: types.Message, state=FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(Profile.height)
    await message.answer("Введите ваш рост (в см)")

@router_prof.message(Profile.height)
async def profile_height(message: types.Message, state=FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(Profile.activity)
    await message.answer("Сколько минут активности у вас в день?")

@router_prof.message(Profile.activity)
async def profile_activity(message: types.Message, state=FSMContext):
    await state.update_data(activity=message.text)
    await state.set_state(Profile.city)
    await message.answer("В каком городе вы находитесь?")

@router_prof.message(Profile.city)
async def profile_city(message: types.Message, state=FSMContext):
    logging.info(f"В блоке city")
    await state.update_data(city=message.text)
    logging.info(f"В блоке city - temp")
    # await state.set_state(Profile.current_temp)
    city = await state.get_data()
    city = city.get("city")
    try:
        logging.info(f"В блоке city - try")
        cur_temp = await main_temp(city)
        await state.update_data(current_temp=cur_temp)
        await state.set_state(Profile.water_goal)
        await message.answer(f"температура в вашем городе установлена автоматически")

    except Exception as e:
        logging.info(f"В блоке city - except")
        await message.answer(f"Проблемы при автоматической загрузке температуры в вашем городе. Пожалуйста, введите температуру вручную:")
        await state.set_state(Profile.current_temp)
        await profile_current_temp()
    finally:
        logging.info(f"В блоке city water_goal")
        profile = await state.get_data()
        await message.answer(f"{profile}")
        water_cal = await get_water_cal(profile)
        await state.update_data(water_goal=water_cal)
        # await state.set_state(Profile.calorie_goal)
        await message.answer(f"Исходя из ваших параметров цель воды посчитана автоматически: {water_cal} мл")

        logging.info(f"В блоке city calorie_goal")
        profile = await state.get_data()
        await message.answer(f"{profile}")
        calorie_goal = await get_calorie_cal(profile)
        await state.update_data(calorie_goal=calorie_goal)
        await message.answer(f"Исходя из ваших параметров цель калорий посчитана автоматически: {calorie_goal} ккал")
        await message.answer(f"Создание профиля завершено. Профиль- {profile}")


@router_prof.message(Profile.current_temp)
async def profile_current_temp(message: types.Message, state=FSMContext):
    logging.info(f"В блоке current_temp")
    await state.update_data(current_temp=message.text)
    # await state.set_state(Profile.water_goal)
    await message.answer(f"Температура установлена")


# логирование воды
@router_log.message(Command("log_water"))
async def log_water(message: types.Message, state=FSMContext):
    is_prof = await is_profile(message, state)
    if is_prof:
        await state.set_state(LogData.logged_water)
        await message.answer("Введите кол-во выпитой воды в мл")

@router_log.message(LogData.logged_water)
async def log_water_handler(message: types.Message, state=FSMContext):
    current_water = await state.get_data()
    current_water = int(current_water.get("logged_water", 0))
    current_water += int(message.text)
    await state.update_data(logged_water=current_water)
    logging.info(f"Вы ввели --------- {message.text}")
    profile = await state.get_data()
    logging.info(f"profile.get('water_goal') - {profile.get("water_goal")}")
    water_goal = int(profile.get("water_goal"))
    logging.info(f"profile.get('logged_water') - {profile.get("logged_water")}")
    log_water = int(profile.get("logged_water"))
    await message.answer(f"Выпито {message.text} мл, осталось выпить: {max(water_goal-log_water, 0)} мл")
    await state.set_state(state=None)


# логирование калорий
@router_log.message(Command("log_calories"))
async def log_calories(message: types.Message, state=FSMContext):
    is_prof = await is_profile(message, state)
    if is_prof:
        await state.set_state(LogData.logged_calories2)
        await message.answer("Введите кол-во съеденых калорий ")

@router_log.message(LogData.logged_calories2)
async def log_calories_handler(message: types.Message, state=FSMContext):
    current_calor = await state.get_data()
    current_calor = int(current_calor.get("logged_calories1", 0))
    current_calor += int(message.text)
    await state.update_data(logged_calories1=current_calor, logged_calories2=current_calor)
    logging.info(f"Вы ввели --------- {message.text}")
    profile = await state.get_data()
    logging.info(f"profile.get('calorie_goal') - {profile.get("calorie_goal")}")
    calorie_goal = int(profile.get("calorie_goal"))
    logging.info(f"profile.get('logged_calories') - {profile.get("logged_calories")}")
    log_cal = int(profile.get("logged_calories1"))
    await message.answer(f"Съедено {message.text} ккал, осталось съесть: {max(calorie_goal-log_cal, 0)} ккал")
    await state.set_state(state=None)


# логирование продуктов
@router_log.message(Command("log_food"))
async def log_food(message: types.Message, state=FSMContext):
    is_prof = await is_profile(message, state)
    if is_prof:
        await state.set_state(LogData.logged_calories1)
        await message.answer("Введите съеденный продукт:  (Например банан 2 штуки или курица 250 грамм)")

# логирование продуктов
@router_log.message(LogData.logged_calories1)
async def log_food_handler(message: types.Message, state=FSMContext):
    try:
        product = await translate_text(message.text)
    except Exception as e:
        logging.warning(f"Неполучилось перевести текст: {e}")
    try:
        resp = await get_calories_info(product, FOOD)
        await message.answer(f"По калориям это примерно: {resp}")
        DATA = await state.get_data()
        current_calories = int(DATA.get("logged_calories", 0))
        current_calories += int(resp)
        await state.update_data(logged_calories1=current_calories, logged_calories2=current_calories)
        # DATA.update(logged_calories1=current_calories, logged_calories2=current_calories)
        # DATA["product_history"] = []
        # DATA["product_history"].append(product)
        calorie_goal = int(DATA.get("calorie_goal", 0))
        await message.answer(f"Осталось съесть: {max(calorie_goal - current_calories, 0)} ккал")

    except Exception as e:
        logging.warning(f"Не получилось обратиться к апи: {e}")
    await state.set_state(state=None)


# фиксирование тренировок
@router_log.message(Command("log_training"))
async def log_traning(message: types.Message, state=FSMContext):
    is_prof = await is_profile(message, state)
    if is_prof:
        await state.set_state(LogData.workout)
        await message.answer("Введите вашу активность: (Например: Бег)")

@router_log.message(LogData.workout)
async def log_traning(message: types.Message, state=FSMContext):
        logging.info("блок activ_time")
        await state.update_data(workout=message.text)
        await state.set_state(LogData.activ_time)
        logging.info("переход в состояние activ_time")
        await message.answer(f"Введите продолжительность тренировки в минутах: (Например 30)")

@router_log.message(LogData.activ_time)
async def log_traning(message: types.Message, state=FSMContext):
    await state.update_data(activ_time=message.text)
    DATA = await state.get_data()
    message.answer(f"{DATA}")
    activiti = DATA.get("workout")

    try:
        activiti = await translate_text(activiti)
    except Exception as e:
        logging.warning(f"Неполучилось перевести текст: {e}")

    activ_time = DATA.get("activ_time", 0)
    query = activiti + " " + activ_time + " " + "min"

    try:
        logging.info(f"В БЛОКЕ TRY   {DATA}")
        logging.info(f"  {activiti}")
        logging.info(f"  {query}")
        resp = await get_calories_info(query, EXERCISES)
        await message.answer(f"Потрачено калорий примерно: {resp}")
        await state.update_data(burned_calories=resp)
        dop_water = 200 * int(activ_time) // 30 
        water_goal = int(DATA.get("water_goal"))
        water_goal += dop_water
        await state.update_data(water_goal=water_goal)
        await message.answer(f"Дополнительно выпейте {dop_water} мл воды. Цель по воде пересчитана.")
    except Exception as e:
        logging.warning(f"Не получилось обратиться к апи: {e}")

    await state.set_state(state=None)


# прогресс
@router_log.message(Command("check_progress"))
async def check_progress(message: types.Message, state=FSMContext):
    await message.answer("П Р О Г Р Е С С:")
    DATA = await state.get_data()
    # вода
    log_water = int(DATA.get("logged_water", 0))
    goal_water = int(DATA.get("water_goal", 0))
    await message.answer("Вода:")
    await message.answer(f"     -- Выпито: {log_water} мл из {goal_water} мл.")
    await message.answer(f"     --Осталось: {max(goal_water-log_water, 0)} мл.")
    # калории
    log_cal = int(DATA.get("logged_calories1", 0))
    goal_cal = int(DATA.get("calorie_goal", 0))
    burned_calories = int(DATA.get("burned_calories", 0))
    await message.answer("Калории:")
    await message.answer(f"     -- Потреблено: {log_cal} ккал из {goal_cal} ккал.")
    await message.answer(f"     -- Сожжено: {burned_calories} ккал")
    await message.answer(f"     -- Баланс: {max(goal_cal-log_cal-burned_calories, 0)} ккал.")







# @router_prof.message(Profile.water_goal)
# async def profile_water_goal(message: types.Message, state=FSMContext):
#     logging.info(f"В блоке city water_goal")
#     profile = await state.get_data()
#     await message.answer(f"{profile}")
#     water_cal = await get_water_cal(profile)
#     await state.update_data(water_goal=water_cal)
#     # await state.update_data(water_goal=message.text)
#     await message.answer(f"цель по воде Успешно ")
    

    
    
# @router_prof.message(Profile.activity)
# async def profile_activity(message: types.Message, state=FSMContext):
#     await state.update_data(activity=message.text)
#     await state.set_state(Profile.city)
#     await message.answer("В каком городе вы находитесь?")




# @router_log.message(Command("log_water"))
# async def log_water(message: types.Message, state=FSMContext):
#     await state.set_state(Profile.logged_water)
#     await message.answer("Введите кол-во выпитой воды")
    

    # Хэндлер на команду /test2
# @router_prof.message(Command(f"log_water {n_water}"))
# async def cmd_test2(message: types.Message):
#     await message.reply(f"log water, {n_water}")