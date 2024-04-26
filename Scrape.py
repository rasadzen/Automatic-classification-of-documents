import requests
import sqlite3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


# Nustatome puslapį, iš kurio vykdome duomenų gavimą
target = "https://publikuojamidokumentai.svencionys.lt/legal-acts"

# Sukūriamą sujungimą su DB
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()

# Sukuriame lentelę, nuskaitytiems duomenims
cursor.execute('''CREATE TABLE IF NOT EXISTS documents
                (label TEXT,
                 document BLOB)''')

# Funkcija duomenų įkelimui į DB
def insert_data(label, document):
    cursor.execute("INSERT INTO documents (label, document) VALUES (?, ?)", (label, document))
    conn.commit()


# Funkcija duomenų gavimui iš puslapio naudojant Selenium
def scrape_dok_data(target):
    # Inicializuojame driver'į
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service)
    driver.get(target)
    try:
        # bandome spausti mygtuką ieškoti, kad duomenis būtų parodyti ekrane
        press_search = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary")))
        press_search.click()
        time.sleep(2)
        print('Mygtukas ieskoti paspaustas')

        try:
            # Surandame visas eilutes
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.grid-row")
            for row in rows:
                try:
                    # Slenkame lentele žemyn, kad įkeltume daugiau eilučių
                    table = driver.find_element(By.CSS_SELECTOR, "table.table")
                    driver.execute_script("arguments[0].scrollIntoView();", table)
                    time.sleep(2)
                except (NoSuchElementException, TimeoutException) as e:
                    print(f'Error while finding or scrolling the table: {e}')
                # Spaudžiame at dokumento pavadinimo
                link = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) > a:nth-child(1)")
                link.click()
                time.sleep(2)
                print('Pavadinimas paspaustas')

                # BeautifulSuop pagalba pasiimame dokumento rūšį
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                label = soup.find('div', class_='col-sm-6').text.strip()
                print('Label:', label)

                # Išskleidžiame atidaromą menių dokumento atidarymui naujame lange
                open_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.fa-file-word')))
                open_dropdown.click()
                print('Isskleidziamas meniu paspaustas')

                # Pasirenkame vieną iš opcijų išskleidžiamame meniu
                first_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#dropdown-basic > li:nth-child(1) > a:nth-child(1)')))
                first_option.click()
                time.sleep(2)
                print('Pasirinktas 1 meniu elementas')

                # Bandome nuskaityti duomenis
                pdf_url = driver.current_url
                response = requests.get(pdf_url)
                pdf_content = response.content
                response.raise_for_status()

                # Įkeliame nuskaitytus duomenis
                insert_data(label, pdf_content)

                # Grįžtame į pradinį skirtuką
                driver.switch_to.window(driver.window_handles[0])
                try:
                    # Išeiname iš atidaryto papildomo lango duokumento atsiutimui
                    press_exit = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".fa-times > path:nth-child(1)")))
                    press_exit.click()
                    time.sleep(2)
                    print('Mygtukas ieskoti paspaustas')
                except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
                    print(f'Error while clicking "Search": {e}')

        except (NoSuchElementException, TimeoutException) as e:
            print(f'Error while finding rows: {e}')


    except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
        print(f'Error while clicking "Search": {e}')

# Paleidžiame funkciją
scrape_dok_data(target)

conn.close()