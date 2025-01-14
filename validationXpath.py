from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración del WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://loteria.org.gt/site/award")
    wait = WebDriverWait(driver, 10)
    
    # Validar el XPath
    element = wait.until(EC.presence_of_element_located((By.XPATH, "//body/div[3]/div[1]/div/div[2]/div[1]/div/div/div/a")))
    print(f"XPath correcto: {element.get_attribute('href')}")
except Exception as e:
    print(f"Error al validar el XPath: {e}")
finally:
    driver.quit()
