class Config:
    def __init__(self):
        self.URL = 'https://cgit.labour.gov.in/awards-and-judgements-orders'
        self.START_DATE = '01/01/1910'  # Format: MM/DD/YYYY
        self.END_DATE = '09/13/2024'
        self.MONTH_INPUT_ID = 'edit-ordermonth'
        self.YEAR_INPUT_ID = 'edit-orderyear'
        self.SEARCH_BUTTON_ID = 'edit-searchbutton'
        self.PDF_DIR = r'C:\Users\admin\Desktop\pdf\industrial_tribunal'