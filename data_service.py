import asyncio
import pprint

from model import Base, Session, SwapiPeople, engine


async def make_db_table():
    """Функция делает миграцию в БД и создает таблицы"""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def drop_db_table():
    """Функция делает миграцию в БД и удаляет таблицы"""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


async def get_people(client, people_id: int):
    """Функция получает данные по персонажу от swapi"""

    async with client.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json()
        return json_data


async def get_info(client, url: str):
    """Функция получает данные по url"""

    async with client.get(f'{url}') as response:
        json_data = await response.json()
        return json_data


async def paste_to_db(people_jsons: dict):
    """Функция записывает данные в БД"""

    async with Session() as session:
        insert_list = []
        for people in people_jsons:
            people_object = SwapiPeople(birth_year=people.get('birth_year'),
                                        eye_color=people.get('eye_color'),
                                        films=people.get('films'),
                                        gender=people.get('gender'),
                                        hair_color=people.get('hair_color'),
                                        height=people.get('height'),
                                        homeworld=people.get('homeworld'),
                                        mass=people.get('mass'),
                                        name=people.get('name'),
                                        skin_color=people.get('skin_color'),
                                        species=people.get('species'),
                                        starships=people.get('starships'),
                                        vehicles=people.get('vehicles'))
            insert_list.append(people_object)
        session.add_all(insert_list)
        await session.commit()


async def load_attribute(client, url_list: list):
    """Функция получает дополнительные данные по персонажу"""
    attribute_list_cor = [get_info(client, url) for url in url_list]
    get_attribute = await asyncio.gather(*attribute_list_cor)
    return get_attribute


async def additional_load_info(client, people_list: list):
    """Функция заменяет ссылки на дополнительные данные по персонажу"""
    new_dict = {}
    del_list = []
    for people in people_list:
        if len(people) == 1:
            print(people_list.index(people))
            del_list.append(people_list.index(people))
        for id, value in people.items():
            if id == 'films':
                films_value = await load_attribute(client, value)
                new_dict[id] = [row['title'] for row in films_value]
            elif id == 'homeworld':
                homeworl = await get_info(client, value)
                new_dict[id] = homeworl['name']
            elif type(value) == list:
                attr_value = await load_attribute(client, value)
                new_dict[id] = [row['name'] for row in attr_value]
        people['films'] = new_dict['films']
        people['homeworld'] = new_dict['homeworld']
        people['species'] = new_dict['species']
        people['starships'] = new_dict['starships']
        people['vehicles'] = new_dict['vehicles']
    [people_list.pop(id) for id in del_list]
    pprint.pprint(people_list)
    return people_list