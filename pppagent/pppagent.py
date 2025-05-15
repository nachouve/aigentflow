# AI Agent that can visit Pepephone website and download invoices

"""
Steps:
1- Open playwright browser
2- Go to Pepephone website
3- Login (if not logged in)
4- Go to invoices page
5- Download the invoice (choosing YYYY and MM)
6- Close browser
"""

import os
import sys
import time
import getpass
from typing import Optional

from playwright.sync_api import sync_playwright

PEPEPHPONE_URL = "https://www.pepephone.com/"
PEPEPHPONE_INVOICES_URL = "https://www.pepephone.com/mi-pepephone/facturas"

months_in_spanish = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


class PepephoneInvoiceDownloader:
    def __init__(self, playwright):
        self.name = "PepephoneInvoiceDownloader"
        self.browser = playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.download_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_path, exist_ok=True)

    def open_browser(self):
        """Navigate to the Pepephone website."""
        self.page.goto(PEPEPHPONE_URL)
        self.page.set_default_timeout(600)

    def login(self, username: str, password: str):
        """Login to Pepephone account."""
        self.page.goto(f"{PEPEPHPONE_URL}login")  # Navigate to the login page
        self.page.fill("input[type='email']", username)  # Fill in the username
        self.page.fill("input[type='password']", password)  # Fill in the password
        # Find a div with text "ENTRAR"
        btn = self.page.wait_for_selector("button:has-text('ENTRAR')", timeout=10000)  # Wait for the login button to be visible
        btn.click()  # Click the button
        self.page.wait_for_load_state("networkidle")  # Wait for the page to load after login
        print("Login successful!")

    def goto_invoices(self):
        """Navigate to the invoices page."""
        self.page.goto(PEPEPHPONE_INVOICES_URL, timeout=30000)
        # Wait for the page to load
        self.page.wait_for_load_state("networkidle")
        # get all text from the page, not tags 
        text = self.page.inner_text("body")

        current_month = int(time.strftime("%m")) 
        current_month_name = time.strftime("%B")
        # Translate month name to Spanish
        last_month_name_es = months_in_spanish[(current_month-1)%12]
        print(f"Current month: {current_month_name} ({current_month}) {last_month_name_es})")
        for line in text.split("\n"):
            if last_month_name_es in line.lower():
                print(line)

    import re

    def extract_invoices(text):
        """Extract invoice data from the text and return a dictionary.
        
        Example of Format of text:
        'Inicio\nPepeTV\nEnergía\nFacturas\nCuenta\nAtención al cliente\nNuestro horario de atención es de lunes a domingo de 8:00h a 23:45h.\nCONTÁCTANOS\nFacturas\nTODAS\nTELÉFONO\nENERGÍA\nMarzo\n2025\nVer menos\nTeléfono\n38,44 €\nLínea 647772590\nFibra  Ultreia 17\nTOTAL\n(impuestos incluidos)\n38,44 € \nFebrero\n2025\n36,99 €\nEnero\n2025\n39,35 €\nDiciembre\n2024\n45,77 €\nNoviembre\n2024\n40,44 €\nOctubre\n2024\n38,44 €\nVER MÁS FACTURAS\n¿Te han quedado dudas?\nEstas son algunas preguntas frecuentes\n¿Cúal es el ciclo de facturación de Pepephone?\n¿Cómo será la primera factura que reciba de Pepephone?\nNo tengo claro que el importe de mi última factura sea correcto, ¿dónde puedo  revisarlo?\n¿Cuándo se renuevan los datos de facturación en Pepephone?\nInformación legal\nPolítica de cookies'
        """
        invoices = {}
        # Regular expression to match month-year and amount with a comma as the decimal separator
        pattern = r"(?i)(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\n(\d{4})\n([\d]+\,[\d]{2}) €"

        # Updated regex to allow for optional lines between the year and the amount
        pattern = r"(?i)(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\n(\d{4})(?:\n.*?)*?\n([\d]+\,[\d]{2}) €"
        matches = re.findall(pattern, text)

        for match in matches:
            month_year = f"{match[0].lower()} {match[1]}"  # Combine month and year
            amount = float(match[2].replace(",", "."))  # Convert amount to float, replacing ',' with '.'
            invoices[month_year] = amount

        return invoices


def download_invoice(self, year: int, month: int):
    """Download the invoice for the specified year and month."""
    #It has to be done with a OCR tool, because the invoice link is not a direct link

        
if __name__ == "__main__OLD":
    with sync_playwright() as playwright:
        try:
            downloader = PepephoneInvoiceDownloader(playwright)
            downloader.open_browser()
            #username = input("Enter your Pepephone username: ")
            password = getpass.getpass("Enter your Pepephone password: ")
            username = "nachouve@gmail.com"
            #password = "7xxxxx Xxxxxxxx"
            downloader.login(username, password)

            downloader.goto_invoices()
            # Extract invoices from the text
            invoices_text = downloader.page.inner_text("body")
            invoices = downloader.extract_invoices(invoices_text)
            print("Invoices found:")
            for month_year, amount in invoices.items():
                print(f"{month_year}: {amount} €")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            import ipdb; ipdb.set_trace()

    OCRBrowser = ScreenOCR()
    # Localize a Chrome window
    OCRBrowser.localize_chrome_window()
    # Focus 
    OCRBrowser.focus_chrome_window()
    # Goto pepephone website
    # Login
    # facturas
    # for each invoice
    #     download invoice