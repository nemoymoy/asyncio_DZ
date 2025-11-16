import asyncio
import datetime

import aiohttp
from more_itertools import chunked

from model import Session, SwapiPeople, drop_db_table, init_orm
from pprint import pprint

MAX_REQUESTS = 5

async def get_people(person_id, http_session):
    response = await http_session.get(f"https://swapi.py4e.com/api/people/{person_id}/")
    json_data = await response.json()
    return json_data


async def insert_people(people_data: list[dict]):
    async with Session() as session:
        insert_list = []
        for people in people_data:
            # swapi_person = SwapiPeople(json=person)
            # print(people)
            if 'detail' not in people:
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
                                            vehicles=people.get('vehicles')
                                            )
                insert_list.append(people_object)
            # session.add(swapi_person)
        # orm_people = [SwapiPeople(json=person) for person in people_data]
        # session.add_all(orm_people)
        session.add_all(insert_list)
        await session.commit()

async def get_info(client, url: str):
    """Функция получает данные по url"""

    async with client.get(f'{url}') as response:
        json_data = await response.json()
        return json_data

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
        if 'detail' not in people:
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
    for id in del_list:
        if id < len(people_list):
            people_list.pop(id)
    pprint(people_list)
    return people_list

async def main():
    await drop_db_table()
    await init_orm()

    tasks = []
    async with aiohttp.ClientSession() as client:
        people_ids = range(1, 101)
        for people_ids_chunk in chunked(people_ids, MAX_REQUESTS):
            coros = [get_people(i, client) for i in people_ids_chunk]
            results = await asyncio.gather(*coros)

            add_attribute = await additional_load_info(client, results)

            coro = insert_people(add_attribute)
            task = asyncio.create_task(coro)
            tasks.append(task)

    tasks = asyncio.all_tasks()
    main_task = asyncio.current_task()
    tasks.remove(main_task)
    # await asyncio.gather(*tasks)
    for task in tasks:
        await task


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.run(main())
    print(datetime.datetime.now() - start)
