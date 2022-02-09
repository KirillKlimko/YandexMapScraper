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

driver.get("https://yandex.by/maps/")

date_dict = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}


def get_data(file_path: str):
    with open(file_path, encoding="utf-8") as museum:
        file_reader = csv.reader(museum, delimiter="5")
        get_object_info(file_reader)


def save_data(folder_name: str, data: dict):
    try:
        os.mkdir(folder_name)
    except:
        shutil.rmtree(folder_name)
        os.mkdir(folder_name)
    with open(f"{folder_name}/data.json", "w") as write_file:
        json.dump(data, write_file, indent=4, ensure_ascii=False)


def save_images(folder_name: str):
    time.sleep(2)
    try:
        try:
            images_button = driver.find_element(
                By.CLASS_NAME, "tabs-select-view__title._name_gallery"
            )
            images_button.click()
        except:
            driver.find_element(By.CLASS_NAME, "carousel__arrow._size_m").click()
            time.sleep(2)
            images_button = driver.find_element(
                By.CLASS_NAME, "tabs-select-view__title._name_gallery"
            )
            images_button.click()
        checker = int(images_button.text.split("\n")[1]) // 20
        for _ in range(0, (checker + 2)):
            time.sleep(0.5)
            driver.find_element(By.CLASS_NAME, "scroll__container").send_keys(Keys.END)
        time.sleep(1)
        img = driver.find_elements(By.CLASS_NAME, "photo-wrapper__photo")
        try:
            os.mkdir(f"{folder_name}/pictures")
        except:
            shutil.rmtree(f"{folder_name}/pictures")
            os.mkdir(f"{folder_name}/pictures")
        for i in img:
            try:
                src = i.get_attribute("src")
                img_data = requests.get(src).content
                with open(
                    f'{folder_name}/pictures/{src.split("/")[4]}.jpg', "wb"
                ) as handler:
                    handler.write(img_data)
            except:
                pass
    except:
        pass


def get_reviews(data: list):
    reviews = []
    for info in data:
        try:
            review = {}
            comment = info.find_element(
                By.CLASS_NAME, "business-review-view__body-text"
            ).text
            author_profession = info.find_element(
                By.CLASS_NAME, "business-review-view__author-profession"
            ).text
            author_level = author_profession.split(" ")
            date = info.find_element(By.CLASS_NAME, "business-review-view__date").text
            split_date = date.split(" ")
            if len(split_date) == 2:
                split_date.append("2022")
            mount = date_dict[split_date[1]]
            if len(split_date[0]) == 1:
                new_date = '0' + split_date[0]
            else:
                new_date = split_date[0]
            current_date = split_date[2] + "-" + mount + "-" + new_date
            name = info.find_element(
                By.CLASS_NAME, "business-review-view__author"
            ).text.split("\n")
            user_url = info.find_element(
                By.CLASS_NAME, "business-review-view__user-icon"
            ).get_attribute("href")
            star = info.find_elements(
                By.CLASS_NAME,
                "inline-image._loaded.business-rating-badge-view__star._size_m",
            )
            empty_star = info.find_elements(
                By.CLASS_NAME,
                "inline-image._loaded.business-rating-badge-view__star._empty._size_m",
            )
            rating = len(star) - len(empty_star)
            review["author_name"] = name[0]
            review["author_profession"] = int(author_level[2])
            review["date"] = current_date
            review["comment"] = comment
            review["author_url"] = user_url
            review["rating"] = rating
            reviews.append(review)
        except:
            pass
    return reviews


def get_object_info(objects_data: csv):
    time.sleep(3)
    counter = 0
    for object in objects_data:
        data = {}
        object_name = object[0].replace("\t", "")
        data["object_name"] = object_name
        time.sleep(3)
        try:
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/div/div/div/div/form/div[2]/div/span/span/input",
            ).clear()
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/div/div/div/div/form/div[2]/div/span/span/input",
            ).send_keys(object_name)
        except:
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/div/div/div/div/form/div[1]/div/span/span/input",
            ).clear()
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/div/div/div/div/form/div[1]/div/span/span/input",
            ).send_keys(object[0])
        time.sleep(1)
        driver.find_element(
            By.CLASS_NAME, "small-search-form-view__icon._type_search"
        ).click()
        time.sleep(3)
        try:
            item_names = driver.find_elements(
                By.CLASS_NAME, "search-snippet-view__body._type_business"
            )
            for item in item_names:
                item_names_list = item.text.split("\n")
                for sub_item in item_names_list:
                    if fuzz.ratio(sub_item, object[0]) > 75:
                        item.click()
                        break
        except:
            pass
        try:
            driver.find_element(
                By.XPATH,
                "/html/body/div[1]/div[2]/div[9]/div[2]/div[1]/div[1]/div[1]/div/div[1]/div/div/ul/div[1]/li/div/div/a",
            ).click()
        except:
            pass
        time.sleep(2)
        try:
            coordinate_list = []
            time.sleep(2)
            driver.find_element(By.CLASS_NAME, 'action-button-view._type_share').click()
            time.sleep(2)
            coordinate = driver.find_element(By.CLASS_NAME,
                                'card-feature-view._view_normal._size_large._interactive.card-share-view__coordinates').text
            coordinate_split_list = coordinate.split(',')
            for coor in coordinate_split_list:
                coordinate_list.append(float(coor))
            data['object_coordinate'] = coordinate_list
        except:
            data['object_coordinate'] = None
        try:
            driver.find_element(
                By.CLASS_NAME, "tabs-select-view__title._name_overview"
            ).click()
        except:
            continue
        try:
            driver.find_element(By.CLASS_NAME, "card-phones-view__more").click()
        except:
            pass
        time.sleep(1)
        buttons = driver.find_elements(By.CLASS_NAME, "card-feature-view__value")
        for button in buttons:
            if button.text != "Добавить":
                button.click()
        try:
            link = driver.current_url
            data["object_id"] = int(link.split("/")[6])
        except:
            pass
        try:
            contact = driver.find_elements(
                By.CLASS_NAME, "card-phones-view__phone-number"
            )
            phones_list = []
            for phone in contact:
                phone_str = phone.text.split("\n")[0]
                phones_list.append(re.sub("[ |-]", "", phone_str))
            if phones_list == []:
                raise ValueError
            elif len(phones_list) == 1:
                data["contact"] = phones_list
            else:
                data["contact"] = phones_list
        except:
            data["contact"] = []
        try:
            business_url = driver.find_element(
                By.CLASS_NAME, "business-urls-view__text"
            )
            data["business_url"] = business_url.text
        except:
            data["business_url"] = None

        try:
            work_time = {}
            days_list = driver.find_elements(
                By.CLASS_NAME, "business-working-intervals-view__item"
            )
            for day in days_list:
                work_time_by_day = day.text.split("\n")
                work_time[work_time_by_day[0]] = work_time_by_day[1]
        except:
            work_time = None
        try:
            links = driver.find_elements(
                By.CLASS_NAME, "button._view_secondary-gray._ui._size_medium._link"
            )
            object_links = []
            for link in links:
                object_links.append(link.get_attribute("href"))
        except:
            object_links = None
        counter += 1
        try:
            object_category = driver.find_element(
                By.CLASS_NAME, "business-card-title-view__category"
            ).text
        except:
            object_category = None
        try:
            address = driver.find_element(
                By.CLASS_NAME, "business-contacts-view__address-link"
            ).text
        except:
            address = None
        data["object_category"] = object_category
        data["object_links"] = object_links
        data["address"] = address
        data["work_time"] = work_time
        try:
            features = driver.find_element(
                By.CLASS_NAME, "business-features-view__valued-content"
            )
            data["features"] = features.text
        except:
            data["features"] = None
        try:
            rating = driver.find_element(
                By.CLASS_NAME, "business-rating-badge-view__rating-text._size_m"
            ).text
            data["rating"] = float(rating.replace(",", "."))
        except:
            data["rating"] = None

        try:
            attendance = {}

            for _ in range(0, 1):
                time.sleep(0.5)
                driver.find_element(By.CLASS_NAME, "scroll__container").send_keys(
                    Keys.END
                )
            time.sleep(1)
            other_days = driver.find_elements(
                By.CLASS_NAME, "business-attendance-view__day"
            )

            for value in other_days:
                value.click()
                time.sleep(1)
                active_day = driver.find_element(
                    By.CLASS_NAME, "business-attendance-view__day._active"
                )
                loading_time = {}
                time.sleep(1)
                date_percent = driver.find_elements(
                    By.CLASS_NAME, "business-attendance-view__bar"
                )
                for value in date_percent:
                    percent = value.get_attribute("style")
                    percent_list = percent.split(" ")
                    percent_int = int(percent_list[1].replace("%", "").replace(";", ""))
                    date_time = value.get_attribute("data-time")
                    loading_time[date_time] = percent_int
                attendance[active_day.text] = loading_time
        except:
            attendance = None
        data["attendance"] = attendance
        try:
            time.sleep(1)
            number_of_votes = driver.find_element(
                By.CLASS_NAME, "business-summary-rating-badge-view__rating-count"
            ).text
            number_of_votes_list = number_of_votes.split(" ")
            data["number_of_votes"] = int(number_of_votes_list[0])
        except:
            data["number_of_votes"] = None
        try:
            all_info = driver.find_element(By.CLASS_NAME, "card-similar-carousel")
            similar_objects = []
            links_list = []
            id_list = []
            objects_names_list = []
            links = all_info.find_elements(By.CLASS_NAME, "link-wrapper")
            object_names = all_info.find_elements(
                By.CLASS_NAME, "card-similar-carousel__title"
            )
            for object_link in links:
                id_list.append(int(object_link.get_attribute("href").split("/")[6]))
                links_list.append(object_link.get_attribute("href"))
            for obj_name in object_names:
                objects_names_list.append(obj_name.text)
            for similar_obj in list(zip(links_list, objects_names_list, id_list)):
                similar_objects_info = {}
                similar_objects_info["object_id"] = similar_obj[2]
                similar_objects_info["object_name"] = similar_obj[1]
                similar_objects_info["object_link"] = similar_obj[0]
                similar_objects.append(similar_objects_info)
        except:
            similar_objects = []
        time.sleep(2)
        reviews_info = {}
        type_reviews = {}
        try:
            driver.find_element(
                By.CLASS_NAME, "tabs-select-view__title._name_reviews"
            ).click()
            time.sleep(2)
            types_reviews_list = driver.find_elements(
                By.CLASS_NAME, "button._view_secondary-gray._ui._size_small"
            )
            for types in types_reviews_list:
                types_list = types.text.split("•")
                if types_list == [""]:
                    continue
                type_reviews[types_list[0]] = int(types_list[1])
            reviews_info["type_reviews"] = type_reviews
        except:
            reviews_info["type_reviews"] = type_reviews
        time.sleep(1)
        try:
            data_list = []
            reviews = []
            count_reviews = driver.find_element(
                By.CLASS_NAME, "tabs-select-view__title._name_reviews._selected"
            ).text

            checker = int(count_reviews.split("\n")[1]) // 50

            try:
                types_reviews_list = driver.find_elements(
                    By.CLASS_NAME, "button._view_secondary-gray._ui._size_small"
                )
            except:
                types_reviews_list = []
            if checker >= 11:
                if types_reviews_list:
                    for types in types_reviews_list:
                        if types.text:
                            time.sleep(2)
                            data_list = []
                            try:
                                time.sleep(1)
                                review_text = types.text
                                into_checker = int(review_text.split("•")[1]) // 50
                                types.click()
                            except:
                                driver.find_element(
                                    By.CLASS_NAME,
                                    "carousel__arrow-wrapper._next._size_m",
                                ).click()
                                time.sleep(1)
                                review_text = types.text
                                into_checker = int(review_text.split("•")[1]) // 50
                                types.click()
                            for _ in range(0, (into_checker + 2)):
                                time.sleep(1)
                                driver.find_element(
                                    By.CLASS_NAME, "scroll__container"
                                ).send_keys(Keys.END)
                                time.sleep(2)
                                driver.find_element(
                                    By.CLASS_NAME, "scroll__container"
                                ).send_keys(Keys.PAGE_UP)
                            review_block = driver.find_elements(
                                By.CLASS_NAME, "business-review-view__info"
                            )
                            time.sleep(1)
                            for review in review_block:
                                data_list.append(review)
                            reviews_list = get_reviews(data_list)
                            for rev in reviews_list:
                                reviews.append(rev)
            else:

                for _ in range(0, (checker + 2)):
                    time.sleep(0.5)
                    driver.find_element(By.CLASS_NAME, "scroll__container").send_keys(
                        Keys.END
                    )
                review_block = driver.find_elements(
                    By.CLASS_NAME, "business-review-view__info"
                )
                for review in review_block:
                    data_list.append(review)
                time.sleep(1)
                reviews_list = get_reviews(data_list)
                for rev in reviews_list:
                    reviews.append(rev)
            time.sleep(1)
        except:
            pass
        time.sleep(1)
        try:
            data["number_of_review"] = len(reviews)
        except:
            data["number_of_review"] = None
        data["similar_objects"] = similar_objects
        data["reviews_info"] = reviews_info
        try:
            reviews_info["reviews"] = reviews
        except:
            reviews_info["reviews"] = None
        save_data(object_name, data)
        save_images(object_name)
        print(object_name, "Done", counter)


get_data("museums-by.csv")
