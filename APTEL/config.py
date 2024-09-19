class Config:
    def __init__(self):
        self.URL = 'https://aptel.gov.in/en/judgementorder/tab4'
        self.START_DATE = '01-01-1910'  # Format: DD/MM/YYYY
        self.END_DATE = '18-09-2024'
        self.MONTH_INPUT_ID = 'edit-from-date'
        self.YEAR_INPUT_ID = 'edit-to-date'
        self.SEARCH_BUTTON_ID = 'edit-actions'
        self.PDF_DIR = r'C:\Users\admin\Desktop\pdf\aptel'