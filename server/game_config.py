from os import getenv

from attrdict import AttrDict


class BaseConfig(object):
    TICK_TIME = 10
    MAP_NAME = 'theMap'
    CURRENT_MAP_VERSION = 'map03'
    DEFAULT_TRAINS_COUNT = 2

    HIJACKERS_ASSAULT_PROBABILITY = 0
    HIJACKERS_POWER_RANGE = (1, 3)
    HIJACKERS_COOLDOWN_COEF = 2

    PARASITES_ASSAULT_PROBABILITY = 0
    PARASITES_POWER_RANGE = (1, 3)
    PARASITES_COOLDOWN_COEF = 2

    REFUGEES_ARRIVAL_PROBABILITY = 0
    REFUGEES_NUMBER_RANGE = (1, 3)
    REFUGEES_COOLDOWN_COEF = 2

    TOWN_LEVELS = AttrDict({
        1: {
            'population_capacity': 10,
            'product_capacity': 200,
            'armor_capacity': 100,
            'train_cooldown_on_collision': 8,
            'next_level_price': 100,
        },
        2: {
            'population_capacity': 20,
            'product_capacity': 400,
            'armor_capacity': 200,
            'train_cooldown_on_collision': 6,
            'next_level_price': 200,
        },
        3: {
            'population_capacity': 40,
            'product_capacity': 800,
            'armor_capacity': 400,
            'train_cooldown_on_collision': 4,
            'next_level_price': None,
        },
    })

    TRAIN_LEVELS = AttrDict({
        1: {
            'goods_capacity': 40,
            # 'fuel_capacity': 400,
            # 'fuel_consumption': 1,
            'next_level_price': 40,
        },
        2: {
            'goods_capacity': 80,
            # 'fuel_capacity': 800,
            # 'fuel_consumption': 1,
            'next_level_price': 80,
        },
        3: {
            'goods_capacity': 160,
            # 'fuel_capacity': 1600,
            # 'fuel_consumption': 1,
            'next_level_price': None,
        },
    })


class TestingConfig(BaseConfig):
    DEFAULT_TRAINS_COUNT = 3


class TestingConfigWithEvents(TestingConfig):
    HIJACKERS_ASSAULT_PROBABILITY = 100
    HIJACKERS_POWER_RANGE = (1, 1)
    PARASITES_ASSAULT_PROBABILITY = 100
    PARASITES_POWER_RANGE = (1, 1)
    REFUGEES_ARRIVAL_PROBABILITY = 100
    REFUGEES_NUMBER_RANGE = (1, 1)


class ProductionConfig(BaseConfig):
    pass


server_configs = {
    'testing': TestingConfig,
    'testing_with_events': TestingConfigWithEvents,
    'production': ProductionConfig,
}

config = server_configs[getenv('WG_FORGE_SERVER_CONFIG', 'production')]
