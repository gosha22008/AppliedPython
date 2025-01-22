from aiogram.fsm.state import State, StatesGroup


class Profile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    current_temp = State()
    water_goal = State()
    calorie_goal = State()
    # logged_water = State()
    # logged_calories = State()
    # burned_calories = State()

class LogData(StatesGroup):
    logged_water = State()
    logged_calories1 = State()
    logged_calories2 = State()
    burned_calories = State()
    activ_time = State()
    workout = State()
    # eat_product = State()