import csv
import json
import os
import re
import shutil
import time

import requests
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# options = webdriver.FirefoxOptions()
# options.headless = True
driver = webdriver.Firefox()

driver.get("https://yandex.by/maps/org/muzey_istorii_velikoy_otechestvennoy_voyny/1082640705/?from=tabbar&ll=27.537664%2C53.916388&mode=search&sctx=ZAAAAAgBEAAaKAoSCUxTBDi9jztAEapiKv2E80pAEhIJdy6M9KL25T8RoWgewCK%2Fxj8iBgABAgMEBSgKOABAtZ4GSAFqAnVhnQHNzEw9oAEAqAEAvQE1uEFJwgERyvD78wPKlf6R7QKX%2F5e6yQTqAQDyAQD4AQCCAgZ5YW5kZXiKAgCSAgA%3D&sll=27.537664%2C53.916388&source=serp_navig&sspn=0.088173%2C0.031893&text=yandex&z=14.43")

time.sleep(3)

driver.find_element(By.CLASS_NAME, 'action-button-view._type_share').click()
time.sleep(1)
a = driver.find_element(By.CLASS_NAME, 'card-feature-view._view_normal._size_large._interactive.card-share-view__coordinates').text
time.sleep(1)
print(a)