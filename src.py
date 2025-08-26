from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import re
import pandas as pd
import time 
from typing import *
from tqdm import tqdm
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class GSMARENAScraper:
    def __init__(self, RATE_LIMIT:int = 20, autosave: bool = False, save_interval:int =20):
        '''
        Initializes the GSMARENAScraper with the specified rate limit, autosave option, and save interval.

        PARAMS
        -----
        RATE_LIMIT: int
            The maximum number of requests to send per second.
        autosave: bool
            Whether to automatically save the dataset at regular intervals.
        save_interval: int
            The number of requests to process before saving the dataset.
        '''
        self.dataset = pd.DataFrame({"manufacturer": [], 
                                    "phonename": [], 
                                    "releasedate": [], 
                                    "os": [], 
                                    "batsize": [], 
                                    "battype": [], 
                                    "scrsize": [], 
                                    "scrtype": [], 
                                    "nettech": [], 
                                    "chipset": [], 
                                    "cpu": [], 
                                    "gpu": [], 
                                    "internal": [], 
                                    "maincammodule": [], 
                                    "maincamvid": [], 
                                    "selfcammodule": [], 
                                    "selfcamvid": [], 
                                    "price": []})
        self.rate_limit = RATE_LIMIT

        # autosaver
        if autosave and not save_interval:
            raise ValueError("If autosave is enabled, save_interval must be specified")
        if autosave and save_interval <= 0:
            raise ValueError("If autosave is enabled, save_interval must be greater than 0")
        self.autosave_check = autosave
        if autosave:
            self.save_interval = save_interval
            self.index = 0
            self.timestart = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")

        # initializes useragent
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        options = Options()
        options.add_argument(f'user-agent={userAgent}')
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.gsmarena.com/makers.php3")

        # get brand information and URLS
        brandList = self.driver.find_elements(By.XPATH, './/div[@class="st-text"]//tbody/tr//td')
        self.brandINFO = []
        for brand in brandList:
            brand_link = brand.find_element(By.XPATH, './/a').get_attribute('href')
            brandName, tot_devices = brand.find_element(By.XPATH, './/a').text.split("\n")
            tot_devices = int(re.sub(r'\D', '', tot_devices))
            self.brandINFO.append([brandName, tot_devices, brand_link])
        self.brandINFO = pd.DataFrame(self.brandINFO, columns=["manufacturer", "total_devices", "link"])
    
    def autosave(self):
        '''
        Saves the dataset to a CSV file at regular intervals.
        '''
        os.makedirs(f"TEMP/{self.timestart}", exist_ok=True)
        
        if self.index % self.save_interval == 0:
            self.dataset.to_csv(f"TEMP/{self.timestart}/{self.index}.csv", index=False)

    def scrape_content(self):
        '''
        Scrapes the URLs from whatever page you're showing.
        then scrapes the content from those URLs.
        '''
        content_URLs = []
        content_elements = self.driver.find_elements(By.XPATH, './/div[@id="review-body"]/div[@class="makers"]/ul/li')
        for element in content_elements:
            content_URLs.append(element.find_element(By.XPATH, './/a').get_attribute('href'))
        for url in tqdm(content_URLs, desc="Scraping phone"):
            time.sleep(self.rate_limit)
            self.driver.get(url)
            self.getphonespec()

            if self.autosave_check:
                self.index+=1
                self.autosave()

    def getphonespec(self):
        '''
        Scrapes the specifications of a phone from its detail page.
        '''
        phone_spec_box = self.driver.find_element(By.XPATH, './/div[@id="body"]/div[1]')  # Get phone specifications box

        try:
            phoneName = phone_spec_box.find_element(By.XPATH, './/h1[@class="specs-phone-name-title"]').text
        except:
            phoneName = "Na"

        try:
            releasedate = phone_spec_box.find_element(By.XPATH, './/span[@data-spec="released-hl"]').text.removeprefix("Released ")
        except:
            releasedate = "Na"

        try:
            os = phone_spec_box.find_element(By.XPATH, './/span[@data-spec="os-hl"]').text
        except:
            os = "Na"

        # battery
        try:
            batsize = phone_spec_box.find_element(By.XPATH, './/span[@data-spec="batsize-hl"]').text
        except:
            batsize = "Na"

        try:
            battype = phone_spec_box.find_element(By.XPATH, './/div[@data-spec="battype-hl"]').text
        except:
            battype = "Na"

        # screen
        try:
            scrsize = phone_spec_box.find_element(By.XPATH, './/div[@data-spec="displayres-hl"]').text.strip(" pixels")
        except:
            scrsize = "Na"

        try:
            scrtype = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="displaytype"]').text
        except:
            scrtype = "Na"

        try:
            nettech = phone_spec_box.find_element(By.XPATH, './/a[@data-spec="nettech"]').text
        except:
            nettech = "Na"

        # platform
        try:
            chipset = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="chipset"]').text
        except:
            chipset = "Na"

        try:
            cpu = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="cpu"]').text
        except:
            cpu = "Na"

        try:
            gpu = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="gpu"]').text
        except:
            gpu = "Na"

        try:
            internal = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="internalmemory"]').text
        except:
            internal = "Na"

        # main camera
        try:
            maincammodule = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="cam1modules"]').text
        except:
            maincammodule = "Na"

        try:
            maincamvid = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="cam1video"]').text
        except:
            maincamvid = "Na"

        # selfie camera
        try:
            selfcammodule = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="cam2modules"]').text
        except:
            selfcammodule = "Na"

        try:
            selfcamvid = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="cam2video"]').text
        except:
            selfcamvid = "Na"

        # price
        try:
            price = phone_spec_box.find_element(By.XPATH, './/td[@data-spec="price"]').text.strip("About ")
        except:
            price = "Na"

        self.dataset = pd.concat([self.dataset, pd.DataFrame({"manufacturer": [self.brandName],
                                                               "phonename": [phoneName],
                                                               "releasedate": [releasedate],
                                                               "os": [os],
                                                               "batsize": [batsize],
                                                               "battype": [battype],
                                                               "scrsize": [scrsize],
                                                               "scrtype": [scrtype],
                                                               "nettech": [nettech],
                                                               "chipset": [chipset],
                                                               "cpu": [cpu],
                                                               "gpu": [gpu],
                                                               "internal": [internal],
                                                               "maincammodule": [maincammodule],
                                                               "maincamvid": [maincamvid],
                                                               "selfcammodule": [selfcammodule],
                                                               "selfcamvid": [selfcamvid],
                                                               "price": [price]})], 
                                                               ignore_index=True)

    def brand_scrape(self, brandName):
        '''
        Scrapes all phone models for a given brand.
        '''
        URL = self.brandINFO[self.brandINFO["manufacturer"]== brandName]["link"].values[0]
        self.driver.get(URL)

        try:
            # This checks if the page navigation element is present. If there's one page on the brand.
            page_nav = self.driver.find_element(By.XPATH, './/div[@class="review-nav-v2"]//div[@class="nav-pages"]')
            temp = re.findall(r'\d+', page_nav.text)
            current_index, last_index = int(temp[0]), int(temp[-1])

            page_urlStructure = page_nav.find_elements(By.XPATH, './/a')[-1].get_attribute('href')
            PAGE_URLS = []
            for i in range(current_index+1, last_index + 1):
                PAGE_URLS.append(re.sub(r'p\d+', f'p{i}', page_urlStructure))
        except:
            # If single page!
            PAGE_URLS = []

        self.brandName = self.driver.find_element(By.XPATH, './/h1["@class = article-info-name"]').text.split(" ")[0]
        print(f"PAGE 1/{len(PAGE_URLS)+1} for brand {brandName}")
        self.scrape_content()
        for page_url in PAGE_URLS:
            print(f"PAGE {PAGE_URLS.index(page_url)+2}/{len(PAGE_URLS)+1} for brand {brandName}")
            self.driver.get(page_url)
            self.scrape_content()

        os.makedirs("OUTPUT", exist_ok=True)
        self.dataset.to_csv(f"OUTPUT/{brandName}.csv", index=False)

    def scrapeALL(self):
        '''
        Scrapes all phone models for all brands.
        '''
        for brand in tqdm(self.brandINFO["manufacturer"], desc="Scraping all brands"):
            self.brand_scrape(brand)
        self.dataset.to_csv(f"OUTPUT/!GSMARENA-DATASET.csv", index=False)

if __name__ == "__main__":
    def start_scraping():
        # Get values from UI
        rate_limit = int(rate_limit_entry.get())
        autosave = autosave_var.get()
        save_interval = int(save_interval_entry.get())
        
        try:
            # Disable button during scraping
            start_button.config(state="disabled")
            
            # Create scraper
            global scraper
            scraper = GSMARENAScraper(RATE_LIMIT=rate_limit, autosave=autosave, save_interval=save_interval)
            
            # Update brand listbox
            update_brand_list()
            
            # Lock settings after initialization
            rate_limit_entry.config(state="disabled")
            autosave_checkbox.config(state="disabled")
            save_interval_entry.config(state="disabled")
            
            # Enable brand selection after initialization
            search_entry.config(state="normal")
            scrape_brand_button.config(state="normal")
            scrape_all_button.config(state="normal")
            
            status_label.config(text="Scraper initialized. Select a brand or choose 'Scrape All'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize scraper: {str(e)}")
            start_button.config(state="normal")
            brand_listbox.config(state="normal")
    
    def update_brand_list(search_term=""):
        """Update the brand listbox based on search term"""
        if scraper is None:
            return
        
        brand_listbox.delete(0, tk.END)
        for brand in scraper.brandINFO["manufacturer"]:
            if search_term.lower() in brand.lower():
                brand_listbox.insert(tk.END, brand)
    
    def on_search(*args):
        """Handle search entry changes"""
        search_term = search_var.get()
        update_brand_list(search_term)
    
    def scrape_brand():
        if not brand_listbox.curselection():
            messagebox.showwarning("Warning", "Please select a brand")
            return
        
        brand = brand_listbox.get(brand_listbox.curselection()[0])
        status_label.config(text=f"Scraping brand: {brand}...")
        
        # Get total devices for this brand for progress tracking
        total_devices = scraper.brandINFO[scraper.brandINFO["manufacturer"] == brand]["total_devices"].values[0]
        
        # Show progress bar and set up for brand scraping
        progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        progress_bar.config(mode="determinate", maximum=total_devices)
        progress_bar["value"] = 0
        
        # Disable buttons during scraping
        scrape_brand_button.config(state="disabled")
        scrape_all_button.config(state="disabled")
        
        def update_progress(current, total, brand_name):
            root.after(0, lambda: progress_bar.config(value=current))
            root.after(0, lambda: status_label.config(text=f"Scraping {brand_name}: {current}/{total} devices"))
        
        def run_scrape():
            try:
                # Modify scraper to track progress
                original_getphonespec = scraper.getphonespec
                devices_scraped = [0]  # Use list for mutable counter
                
                def tracked_getphonespec():
                    original_getphonespec()
                    devices_scraped[0] += 1
                    update_progress(devices_scraped[0], total_devices, brand)
                
                scraper.getphonespec = tracked_getphonespec
                scraper.brand_scrape(brand)
                scraper.getphonespec = original_getphonespec  # Restore original method
                
                root.after(0, lambda: progress_bar.grid_remove())
                root.after(0, lambda: status_label.config(text=f"Finished scraping {brand} ({total_devices} devices)"))
                root.after(0, lambda: scrape_brand_button.config(state="normal"))
                root.after(0, lambda: scrape_all_button.config(state="normal"))
                root.after(0, lambda: messagebox.showinfo("Scraping Complete", f"Successfully scraped {brand} brand with {total_devices} devices!"))
            except Exception as e:
                root.after(0, lambda: progress_bar.grid_remove())
                root.after(0, lambda: messagebox.showerror("Error", f"Failed to scrape brand: {str(e)}"))
                root.after(0, lambda: status_label.config(text="Error occurred"))
                root.after(0, lambda: scrape_brand_button.config(state="normal"))
                root.after(0, lambda: scrape_all_button.config(state="normal"))
        
        # Run scraping in a separate thread to prevent UI freeze
        threading.Thread(target=run_scrape, daemon=True).start()
    
    def scrape_all():
        status_label.config(text="Scraping all brands...")
        
        # Calculate total devices across all brands
        total_all_devices = scraper.brandINFO["total_devices"].sum()
        
        # Show progress bar for all brands
        progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        progress_bar.config(mode="determinate", maximum=total_all_devices)
        progress_bar["value"] = 0
        
        # Disable buttons during scraping
        scrape_brand_button.config(state="disabled")
        scrape_all_button.config(state="disabled")
        
        def update_progress_all(current, total, current_brand, brand_index, total_brands):
            root.after(0, lambda: progress_bar.config(value=current))
            root.after(0, lambda: status_label.config(text=f"Scraping {current_brand} (Brand {brand_index+1}/{total_brands}): {current}/{total} total devices"))
        
        def run_scrape_all():
            try:
                total_scraped = [0] 
                original_getphonespec = scraper.getphonespec
                
                def tracked_getphonespec():
                    original_getphonespec()
                    total_scraped[0] += 1
                
                scraper.getphonespec = tracked_getphonespec
                
                for i, brand in enumerate(scraper.brandINFO["manufacturer"]):
                    brand_devices = scraper.brandINFO[scraper.brandINFO["manufacturer"] == brand]["total_devices"].values[0]
                    
                    # Update progress for each device in this brand
                    brand_start_count = total_scraped[0]
                    
                    def brand_tracked_getphonespec():
                        original_getphonespec()
                        total_scraped[0] += 1
                        update_progress_all(total_scraped[0], total_all_devices, brand, i, len(scraper.brandINFO))
                    
                    scraper.getphonespec = brand_tracked_getphonespec
                    scraper.brand_scrape(brand)
                
                scraper.getphonespec = original_getphonespec 
                
                root.after(0, lambda: progress_bar.grid_remove())
                root.after(0, lambda: status_label.config(text=f"Finished scraping all brands ({total_all_devices} total devices)"))
                root.after(0, lambda: scrape_brand_button.config(state="normal"))
                root.after(0, lambda: scrape_all_button.config(state="normal"))
                root.after(0, lambda: messagebox.showinfo("Scraping Complete", f"Successfully scraped all {len(scraper.brandINFO)} brands with {total_all_devices} total devices!"))
            except Exception as e:
                root.after(0, lambda: progress_bar.grid_remove())
                root.after(0, lambda: messagebox.showerror("Error", f"Failed to scrape all brands: {str(e)}"))
                root.after(0, lambda: status_label.config(text="Error occurred"))
                root.after(0, lambda: scrape_brand_button.config(state="normal"))
                root.after(0, lambda: scrape_all_button.config(state="normal"))
        
        # Run scraping in a separate thread to prevent UI freeze
        threading.Thread(target=run_scrape_all, daemon=True).start()
    
    # Create the main window
    root = tk.Tk()
    root.title("GSM Arena Scraper")
    root.geometry("600x550")
    
    # Create a frame for settings
    settings_frame = ttk.LabelFrame(root, text="Scraper Settings")
    settings_frame.pack(fill="x", padx=10, pady=10)
    
    # Rate limit
    ttk.Label(settings_frame, text="Rate Limit (seconds):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    rate_limit_entry = ttk.Entry(settings_frame, width=10)
    rate_limit_entry.insert(0, "20")
    rate_limit_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    # Autosave
    autosave_var = tk.BooleanVar(value=True)
    autosave_checkbox = ttk.Checkbutton(settings_frame, text="Enable Autosave", variable=autosave_var)
    autosave_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    
    # Save interval
    ttk.Label(settings_frame, text="Save Interval:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    save_interval_entry = ttk.Entry(settings_frame, width=10)
    save_interval_entry.insert(0, "20")
    save_interval_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    # Initialize button
    start_button = ttk.Button(settings_frame, text="Initialize Scraper", command=start_scraping)
    start_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)
    
    # Progress bar frame
    progress_frame = ttk.Frame(root)
    progress_frame.pack(fill="x", padx=10, pady=5)
    progress_frame.grid_columnconfigure(0, weight=1)
    
    # Progress bar (initially hidden)
    progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
    
    # Brand selection frame
    brand_frame = ttk.LabelFrame(root, text="Brand Selection")
    brand_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Search frame
    search_frame = ttk.Frame(brand_frame)
    search_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(search_frame, text="Search brands:").pack(side=tk.LEFT, padx=(0, 5))
    search_var = tk.StringVar()
    search_var.trace('w', on_search)
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, fill="x", expand=True)
    search_entry.config(state="disabled")
    
    # Brand listbox with scrollbar
    listbox_frame = ttk.Frame(brand_frame)
    listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    scrollbar = ttk.Scrollbar(listbox_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    brand_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, height=10)
    brand_listbox.pack(fill="both", expand=True)
    scrollbar.config(command=brand_listbox.yview)
    
    # Buttons frame
    button_frame = ttk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=10)
    
    scrape_brand_button = ttk.Button(button_frame, text="Scrape Selected Brand", command=scrape_brand)
    scrape_brand_button.pack(side=tk.LEFT, padx=5)
    scrape_brand_button.config(state="disabled")
    
    scrape_all_button = ttk.Button(button_frame, text="Scrape All Brands", command=scrape_all)
    scrape_all_button.pack(side=tk.RIGHT, padx=5)
    scrape_all_button.config(state="disabled")
    
    # Status label
    status_label = ttk.Label(root, text="Please initialize the scraper first")
    status_label.pack(pady=10)
    
    scraper = None
    
    root.mainloop()