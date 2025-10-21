# String Analyzer API (Django REST Framework)

### Description
REST API that analyzes strings and stores their computed properties:
- Length
- Palindrome status
- Unique characters
- Word count
- SHA-256 hash
- Character frequency map

### Stack
- Python 3.x
- Django
- Django REST Framework

### How to Run Locally
```bash
git clone https://github.com/dettah/string_analyzer_api.git
cd string_analyzer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
