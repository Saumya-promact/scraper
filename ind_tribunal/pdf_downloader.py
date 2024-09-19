import os
import requests

class PDFDownloader:
    def __init__(self, pdf_dir=None):
        if pdf_dir is None:
            self.pdf_dir = r'C:\Users\admin\Desktop\pdf\sikkim_high_court'
        else:
            self.pdf_dir = pdf_dir

        os.makedirs(self.pdf_dir, exist_ok=True)

    def create_session(self, driver):
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        return session

    def download(self, session, url, filename):
        try:
            response = session.get(url, stream=True)
            response.raise_for_status()
            
            file_path = os.path.join(self.pdf_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return file_path
        except Exception as e:
            print(f"Error downloading PDF from {url}: {str(e)}")
            return None
