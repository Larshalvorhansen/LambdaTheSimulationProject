import re
from bs4 import BeautifulSoup

file_path = "data/360239172.html"

def extract_property_details(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    details = {}

    # Extracting Finkode from the URL in the 'meta' tag with property 'og:url'
    og_url_meta = soup.find('meta', attrs={'property': 'og:url'})
    if og_url_meta:
        details['Finnkode'] = og_url_meta['content'].split('finnkode=')[-1]

    # Extracting the link from the 'link' tag with rel 'canonical'
    canonical_link = soup.find('link', attrs={'rel': 'canonical'})
    if canonical_link:
        details['Lenke'] = canonical_link['href']

    # Extracting the title from the 'meta' tag with property 'og:title'
    og_title_meta = soup.find('meta', attrs={'property': 'og:title'})
    if og_title_meta:
        details['Tittel'] = og_title_meta['content']

    # Extracting description from the 'meta' tag with name 'description'
    description_meta = soup.find('meta', attrs={'name': 'description'})
    if description_meta:
        details['Om boligen'] = description_meta['content']

    # Attempt to find the address in a div with class 'address'
    address_tag = soup.find('div', class_='address')
    if address_tag:
        details['Adresse'] = address_tag.get_text(strip=True)

    # Additional fields extraction based on known patterns in real estate listings
    field_patterns = {
        'Prisantydning': re.compile(r'Prisantydning\s*:\s*([\d\s]+kr)'),
        'Totalpris': re.compile(r'Totalpris\s*:\s*([\d\s]+kr)'),
        'Omkostninger': re.compile(r'Omkostninger\s*:\s*([\d\s]+kr)'),
        'Fellesgjeld': re.compile(r'Fellesgjeld\s*:\s*([\d\s]+kr)'),
        'Felleskost/mnd.': re.compile(r'Felleskostnader/mnd.\s*:\s*([\d\s]+kr)'),
        'Fellesformue': re.compile(r'Fellesformue\s*:\s*([\d\s]+kr)'),
        'Formuesverdi': re.compile(r'Formuesverdi\s*:\s*([\d\s]+kr)'),
        'Pris på lån': re.compile(r'Pris på lån\s*:\s*([\d\s]+kr/mnd)'),
        'Boligtype': re.compile(r'Boligtype\s*:\s*(\w+)'),
        'Eieform': re.compile(r'Eieform\s*:\s*(\w+)'),
        'Soverom': re.compile(r'Soverom\s*:\s*(\d+)'),
        'Internt bruksareal': re.compile(r'Internt bruksareal\s*:\s*([\d\s]+m²)'),
        'Bruksareal': re.compile(r'Bruksareal\s*:\s*([\d\s]+m²)'),
        'Eksternt bruksareal': re.compile(r'Eksternt bruksareal\s*:\s*([\d\s]+m²)'),
        'Etasje': re.compile(r'Etasje\s*:\s*(\d+)'),
        'Byggeår': re.compile(r'Byggeår\s*:\s*(\d+)'),
        'Energimerking': re.compile(r'Energimerking\s*:\s*([A-G]\s*-\s*[A-Z]+)'),
        'Rom': re.compile(r'Rom\s*:\s*(\d+)'),
        'Renovert år': re.compile(r'Renovert år\s*:\s*(\d+)'),
        'Tomteareal': re.compile(r'Tomteareal\s*:\s*([\d\s]+m²)'),
        'Fasiliteter': re.compile(r'Fasiliteter\s*:\s*([^\n]+)')
    }

    # Text content of the HTML to apply regex patterns
    html_text = soup.get_text()

    for field, pattern in field_patterns.items():
        match = pattern.search(html_text)
        if match:
            details[field] = match.group(1).strip()

    return details

# Path to your HTML file
property_details = extract_property_details(file_path)
print(property_details)



{'Finnkode': '360239172',
 'Lenke': 'https://www.finn.no/realestate/homes/ad.html?finnkode=360239172',
 'Tittel': 'Lekker og lys 2-roms med vestvendt balkong på ca 11,5kvm. Fantastisk utsikt og gode solforhold. Heis. Oppvarming/VV inkl',
 'Om boligen': 'Velkommen til Malerhaugveien 34C! En lys og lekker 2-roms leilighet i 4. etg med stor og vestvendt balkong på hele 11,5kvm som byr på en fantastisk ut'}
