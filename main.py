import aiohttp
import asyncio
import csv
import json
from lxml import html
from unidecode import unidecode

FREEMAIL_PROVIDERS = [
    'cbox.cz',
    'c-box.cz',
    'centrum.cz',
    'cmail.cz',
    'c-mail.cz',
    'email.cz',
    'gmail.com',
    'iol.cz',
    'o2active.cz',
    'post.cz',
    'quick.cz',
    'raz-dva.cz',
    'seznam.cz',
    'tiscali.cz',
    'volny.cz',
    'wo.cz',
    'worldonline.cz',
]

async def get(row, session):
    try:
        async with session.get(url=f"http://{row['url']}", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}) as response:
            tree = html.fromstring(await response.text())
            generator = tree.xpath('//meta[@name="generator"]/@content')
            author = tree.xpath('//meta[@name="author"]/@content')
            print(generator, author)
            row['generator'] = generator
            row['author'] = author
            row['status'] = response.status
    except Exception as e:
        print(e)
        row['status'] = '000'
    
    print(f"[{row['status']}] {row['name']} ")

    return row

async def main():
    with open('obce.json', encoding='utf-8') as file:
        data = json.load(file)
        csv_data = []

        for municipality in data['municipalities']:
            hezky_nazev = municipality['hezkyNazev']
            
            for domain in set([mail.split('@')[1] for mail in municipality['mail']]):

                if unidecode(hezky_nazev.lower().replace(' ', '')) in domain:
                    is_official = 1
                else:
                    is_official = 0
                    if domain in FREEMAIL_PROVIDERS:
                        domain = None

                csv_data.append({
                    'name': hezky_nazev,
                    'url': domain,
                    'is_official': is_official,
                    })
        
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(row, session) for row in csv_data if row['is_official'] == 1])

        with open('obce.csv', 'w+', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, ['name', 'url', 'is_official', 'status', 'generator', 'author'])
            writer.writeheader()
            writer.writerows(csv_data)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
