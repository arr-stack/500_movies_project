from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import execute_values
from dependencies import password

BASE_URL = "https://www.film.ru"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f"{BASE_URL}/compilation/500-luchshih-filmov")
    page.wait_for_selector("css=div.redesign_afisha_movie")

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

    movie_cards = page.locator("css=div.redesign_afisha_movie").all()

    targets = []

    for card in movie_cards:
        title_element = card.locator("css=.redesign_afisha_movie_main_title a")
        if title_element.count() == 0:
            continue
        ru_title = title_element.inner_text().strip()
        path = title_element.get_attribute("href")
        full_url = f"{BASE_URL}{path}"
        subtitle_element = card.locator("css=.redesign_afisha_movie_main_subtitle")

        full_text = subtitle_element.inner_text().strip()
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        original_title = lines[0]
        year = lines[1]

        targets.append({
            "title": ru_title,
            "original_title": original_title,
            "year": year,
            "url": full_url
        })
    scraped_results = []

    for item in targets:
        page.goto(item["url"])
        desc_node = page.locator("css=div.wrapper_movies_text p")
        description = desc_node.first.inner_text().strip()

        scraped_results.append({
            "title": item["title"],
            "original_title": item["original_title"],
            "year": item["year"],
            "description": description
        })

    browser.close()

    data_to_insert = [
        (
            movie["title"],
            movie["original_title"],
            movie["year"],
            movie["description"]
        )
        for movie in scraped_results
    ]
    browser.close()

    con = psycopg2.connect(database='movies_500', user='postgres', password=password, host='localhost', port='5432')
    cur = con.cursor()

    query = "INSERT INTO movies (title, original_title, year, description) VALUES %s"

    execute_values(cur, query, data_to_insert)
    con.commit()
    cur.close()
    con.close()
