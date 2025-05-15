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
from dotenv import load_dotenv

from smolagents import vision_web_browser as vwb
## from vwb ##
import argparse
from io import BytesIO
from time import sleep

import helium
import PIL.Image
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from smolagents import CodeAgent, DuckDuckGoSearchTool, tool
from smolagents.agents import ActionStep
from smolagents.cli import load_model
##############

from dialog import show_dialog

PEPEPHPONE_URL = "https://www.pepephone.com/mi-pepephone"
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

vwb.search_request = f"""
Please, Visit Pepephone website and download the 3 more recent invoices in PDF.

Today is: {time.strftime("%Y-%m-%d")}
PEPHPONE_URL: {PEPEPHPONE_URL}
PEPEPHONE_INVOICES_URL: {PEPEPHPONE_INVOICES_URL}

The user will login in the Pepephone website prevously, so you have only search for the invoices.

You have to go to the invoices page and download the 3 more recent invoices in PDF format.

You need to click in every invoice amount (but can be the same amount in more than one month!!) that will open *in a new tab* with the invoice in PDF.

Be aware of the new tab, to continue to the next invoice.

To download the invoice, you need to click in the download button ("Descargar") that is in the top right corner of the page with an icon of a down arrow and a line under it.

The html code for that download button is:
<cr-icon-button id="download" iron-icon="cr:file-download" aria-label="Descargar" title="Descargar" aria-haspopup="false" role="button" tabindex="0" aria-disabled="false"></cr-icon-button>

"""

def go_to_pdf_invoice(amount_text="39,35 €"):
    click(S(f"//*[contains(text(), '{amount_text}')]"))
    time.sleep(1)
    # Locate the download button by its id and click it
    # page has this code:
    # '<html><head></head><body style="height: 100%; width: 100%; overflow: hidden; margin:0px; background-color: rgb(82, 86, 89);"><embed name="F75C4AAB2F366C98EB15293E0FB79CB2" style="position:absolute; left: 0; top: 0;" width="100%" height="100%" src="about:blank" type="application/pdf" internalid="F75C4AAB2F366C98EB15293E0FB79CB2"></body></html>'
    # so... we need to access the embed element and click the download button in the new tab
    # Switch to the new tab (the last one opened)
    driver.switch_to.window(driver.window_handles[-1])
    # Wait for the page to load
    time.sleep(2)
    # Click the download button
    driver.execute_script("window.print();")
    time.sleep(2)
    pyautogui.press('enter')


        # time.sleep(1)
       
    download_button = driver.find_element(By.ID, "download")
    download_button.click()
    
    

def run_webagent(prompt: str, model_type: str, model_id: str) -> None:
    # Load environment variables
    load_dotenv()

    # Initialize the model based on the provided arguments
    model = load_model(model_type, model_id)    

    global driver
    driver = vwb.initialize_driver()
    agent = vwb.initialize_agent(model)
    
    go_to(PEPEPHPONE_URL)
    
    email = find_all(S("*[type=email]"))
    if len(email) > 0:
        email_element = email[0].web_element
        print(email_element)
        email_element.click()
        email_element.clear()
        print(email_element)
        # Select all text in the email input field and delete it
        email_element.send_keys(Keys.CONTROL + "a")
        email_element.send_keys(Keys.DELETE)
        
        write("nachouve@gmail.com", into=email[0])
    show_dialog("User Action Required", "Please, login in Pepephone website")

    # Run the agent with the provided prompt
    agent.python_executor("from helium import *")
    agent.run(prompt + vwb.helium_instructions)


def main() -> None:
    # Parse command line arguments
    args = vwb.parse_arguments()
    run_webagent(args.prompt, args.model_type, args.model_id)

    