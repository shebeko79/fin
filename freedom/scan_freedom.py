from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
from requests.structures import CaseInsensitiveDict
import time
import datetime
import os.path


adviсe = []
#if os.path.exists('adviсe.dat'):
#    f = open('adviсe.dat', 'rb')
#    adviсe = pickle.load(f)

service = Service(executable_path="./chromedriver_win32/chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://tradernet.com/authentication/login/")

input("Step wait for login")

driver.get("https://tradernet.com/what-to-buy?tab=ideas")

for x in range(50):
    next_button = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(by=By.XPATH, value="//*[@id='what-to-buy-page']/div/div/section[2]/div/div[2]/button"))
    print(x, ": button text=",next_button.text)
    time.sleep(3)
    next_button.click()

time.sleep(3)
all_links = driver.find_elements(By.TAG_NAME, "a")
links=[]

for l in all_links:
    href = l.get_attribute("href")
    if isinstance(href, str) and href.find("/what-to-buy/idea/") != -1:
        links.append(l)

for l in links:
    href = l.get_attribute("href")
    num_str = href.replace("https://tradernet.com/what-to-buy/idea/","");
    l.click()
    time.sleep(3)

    el_enter_price =  driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[2]/ul/li[2]/span[2]')
    el_target_price = driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[2]/ul/li[3]/span[2]')
    el_pos_size =     driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[2]/ul/li[4]/span[2]')
    el_pos_risk =     driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[2]/ul/li[5]/span[2]')
    el_pos_duration = driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[2]/ul/li[6]/span[2]')
    el_pos_gain =     driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[2]/ul/li[7]/div/span')
    el_pos_ticket =   driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[2]/div/div/div[2]/div[1]/div[1]/a')
    el_pos_date =     driver.find_element(by=By.XPATH, value='//*[@id="invest-ideas-'+num_str+'"]/div/section[1]/div/div[1]/div[2]/div[1]')
                                                              
    enter_price =  el_enter_price.text
    target_price = el_target_price.text
    pos_size =     el_pos_size.text
    pos_risk =     el_pos_risk.text
    pos_duration = el_pos_duration.text
    pos_gain =     el_pos_gain.text
    pos_ticket =   el_pos_ticket.get_attribute('href').replace("https://tradernet.com/charts/","")
    pos_date = el_pos_date.text
            
    dt = datetime.datetime.now()
    if pos_date == 'today':
        dt = dt
    elif pos_date.find(" days ago") != -1:
        d = int(pos_date.replace(" days ago",""))
        dt = dt - datetime.timedelta(days=d)
    else:
        dt = datetime.datetime.strptime(pos_date,"%d %B %Y at %H:%M")#25 April 2023 at 10:00
        
    pos_date = dt.strftime('%Y-%m-%d %H:%M')
    
    print(f'{pos_ticket}: date={pos_date} enter={enter_price} target={target_price} size={pos_size} risk={pos_risk} duration={pos_duration} gain={pos_gain}')
    
    rec = [pos_ticket,pos_date,enter_price,target_price,pos_size,pos_risk,pos_duration,pos_gain]
    adviсe.append(rec)

    driver.back()
    time.sleep(1)
    
    
input("Step to save")
f = open('adviсe.dat', 'wb')
pickle.dump(adviсe, f)
f.close()

driver.quit()
