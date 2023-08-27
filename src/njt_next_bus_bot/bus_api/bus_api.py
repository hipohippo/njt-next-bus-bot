"""
projecte parked due to anti-robot mechanism on njtransit.com
"""
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from hipo_telegram_bot_common.selenium_driver.launch import get_chrome_driver
from njt_next_bus_bot.bus_api.bus_and_stop import Stop, NextBus


def parse_mybusnow_webpage(stop: Stop, browser: WebDriver, browser_window_handle: int) -> List[NextBus]:
    browser.switch_to.window(browser.window_handles[browser_window_handle])
    browser.get(f"https://mybusnow.njtransit.com/bustime/wireless/html/eta.jsp?route=All&id={stop.id}&showAllBusses=on")
    scheduled_bus_and_arrivals = browser.find_elements(by=By.XPATH, value='//strong[@class="larger"]')
    capacity = browser.find_elements(by=By.XPATH, value='//span[@class="smaller"]')
    bus_and_prediction = [element.text for element in scheduled_bus_and_arrivals]
    vehicle_info = [cap.text for cap in capacity]

    num_arrival_info = len(bus_and_prediction) // 2
    return [
        NextBus(stop, bus_and_prediction[2 * i], bus_and_prediction[2 * i + 1], vehicle_info[i])
        for i in range(num_arrival_info)
    ]


async def next_bus_job(stop: Stop, browser: WebDriver, browser_window_handle: int) -> List[NextBus]:
    return parse_mybusnow_webpage(stop, browser, browser_window_handle)

def local_tst():
    browser = get_chrome_driver(config, 6001)