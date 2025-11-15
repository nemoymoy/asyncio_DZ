import asyncio
import datetime

import aiohttp
from more_itertools import chunked

from model import Session, SwapiPeople, drop_db_table, init_orm

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
                                            # films=people.get('films'),
                                            gender=people.get('gender'),
                                            hair_color=people.get('hair_color'),
                                            # height=people.get('height'),
                                            homeworld=people.get('homeworld'),
                                            mass=people.get('mass'),
                                            name=people.get('name'),
                                            skin_color=people.get('skin_color'),
                                            # species=people.get('species'),
                                            # starships=people.get('starships'),
                                            # vehicles=people.get('vehicles')
                                            )
                insert_list.append(people_object)
            # session.add(swapi_person)
        # orm_people = [SwapiPeople(json=person) for person in people_data]
        # session.add_all(orm_people)
        session.add_all(insert_list)
        await session.commit()

async def main():
    await drop_db_table()
    await init_orm()

    async with aiohttp.ClientSession() as http_session:
        people_ids = range(1, 101)
        for people_ids_chunk in chunked(people_ids, MAX_REQUESTS):
            coros = [get_people(i, http_session) for i in people_ids_chunk]
            results = await asyncio.gather(*coros)
            coro = insert_people(results)
            task = asyncio.create_task(coro)

    tasks = asyncio.all_tasks()
    main_task = asyncio.current_task()
    tasks.remove(main_task)
    await asyncio.gather(*tasks)
    # for task in tasks:
    #     await task


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.run(main())
    print(datetime.datetime.now() - start)
