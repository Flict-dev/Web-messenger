"""
This file should be deleted when the backend is ready
"""
class Reader:
  def __init__(self, filename: str):
    self.filename = filename
    self.abs_path = r'D:\PythonProjetcs\webMessenger\Web-messenger\backend\templates'
  
  def read_html(self):
    with open(f"{self.abs_path}\{self.filename}", 'r') as file:
      html = file.read()
    return html
    