
from selenium import webdriver
import requests
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import zipfile

options=webdriver.ChromeOptions()
options.headless=True

driver=webdriver.Chrome()


# Lien de la page web à scraper
url = "https://www.syride.com/fr/explorer/3764768529"
driver.get(url)


# Attendre que la page se charge complètement
driver.implicitly_wait(5)  # Attendre jusqu'à 10 secondes pour que les éléments se chargent
i=2
vols=[]
while i<30:
    
    # Récupérer toutes les classes lineDiv
    lineDivs = driver.find_elements(By.CLASS_NAME, "lineDiv")
    
    # Pour chaque classe lineDiv, cliquer sur le bouton loupe et extraire le lien
    for lineDiv in lineDivs:
        loupe_button = lineDiv.find_element(By.CSS_SELECTOR, "td[onclick^='showFlight'] img")
        driver.implicitly_wait(1)
        driver.execute_script("arguments[0].click();", loupe_button)
    
        vol_url = driver.current_url
        print(vol_url)
        vols.append(vol_url)



    # Construire le sélecteur CSS avec la valeur de i
    css_selector = f'img.numeroPagesResultats[data-page="{i}"]'

    # Tenter de trouver l'élément avec le sélecteur CSS
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
    )

    # Exécuter un script JavaScript pour cliquer sur l'élément
    driver.execute_script("arguments[0].click();", element)
    
    print(f"Page {i-1} traitée")
    i += 1
    driver.implicitly_wait(5)

for vol in vols:
    print(vol)
    driver.get(vol)
    driver.implicitly_wait(1) 
    # Si l'élément est dans un iframe, passez-y
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    if iframe:
        driver.switch_to.frame(iframe)

    # Trouver l'élément de flèche sur la page actuelle
    arrow_button = driver.find_element(By.ID, "bandeauDroiteDivArrow")


# Cliquer sur le bouton
    arrow_button.click()
    # Extract the HTML content of the page
    page_source = driver.page_source
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find the <a> tag containing the ZIP link
    zip_link = soup.find('a', href=lambda href: href and 'downloadZIP.php' in href)
    
    # Extract the href attribute value if the ZIP link is found
    if zip_link:
        zip_url = zip_link['href']
        #print("ZIP link:", zip_url)
    else:
        print("ZIP link not found on this page")
    


    
    filename = "Data_St-Hilaire>20km_100p/"+zip_url.split('=')[-1]  # Utilisation de la partie après le dernier '=' comme nom de fichier
    # Divise l'URL en segments en utilisant '/' comme séparateur
    segments = vol.split('/')

    # Récupère les deux derniers segments
    deux_derniers_mots = segments[-2:]

    # Rejoindre les deux derniers segments en une seule chaîne de caractères
    name_data = '+'.join(deux_derniers_mots)
        # Télécharger le fichier ZIP
    zip_url="https://www.syride.com/"+zip_url
    zip_response = requests.get(zip_url)

        # Vérifier si la requête a réussi (statut 200)
    if zip_response.status_code == 200:
            # Écrire le contenu de la réponse dans un fichier
        with open(filename+ ".zip" , 'wb') as f:
            f.write(zip_response.content)
        
        with zipfile.ZipFile(filename+ ".zip" , 'r') as zip_ref:
            zip_ref.extractall("Data_St-Hilaire>20km_100p/"+name_data)
        os.remove(filename+".zip")

        print(f"Le fichier ZIP a été téléchargé avec succès sous le nom '{filename}'.")
    else:
        print(f"La requête de téléchargement du fichier ZIP à partir du lien '{zip_url}' a échoué.")
    
# Fermer le navigateur
driver.quit()