class Config:
    def __init__(self):
        self.URL = 'https://hcs.gov.in/hcs/hcourt/hg_judgement_date_search'
        self.START_DATE = '01/01/1910'  # Format: MM/DD/YYYY
        self.END_DATE = '09/13/2024'
        self.MONTH_INPUT_ID = 'edit-ordermonth'
        self.YEAR_INPUT_ID = 'edit-orderyear'
        self.SEARCH_BUTTON_ID = 'edit-searchbutton'
        self.PDF_DIR = r'C:\Users\admin\Desktop\pdf\sikkim_high_court'