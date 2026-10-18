from playwright.sync_api import sync_playwright
import psycopg2
from dependencies import password

with sync_playwright() as p:
    con = psycopg2.connect(database='movies_500', user='postgres', password=password, host='localhost', port='5432')

    cur = con.cursor()

    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.film.ru/compilation/500-luchshih-filmov")

    scroll_count = 0
    max_count = 100

    height = -1
    while scroll_count < max_count:
        page.mouse.wheel(0, 15000)
        page.wait_for_timeout(4000)
        new_height = page.evaluate('document.body.scrollHeight')
        if new_height == height:
            break
        height = new_height
        scroll_count += 1

    c = 0
    u = page.locator("//div[@class='redesign_afisha_movie_main_title']//a")
    for item in u.all_text_contents():
        c += 1
        cur.execute('''INSERT INTO movies(title) VALUES(%s)''', (item.strip(),))

    print(c)
    con.commit()
    cur.close()
    con.close()
    browser.close()
