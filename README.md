Web application that has 5 different flaws from the OWASP top ten list as well as their fixes.

## Setup instructions
1. Clone repository

2. Create virtual enviroment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup database
```bash
python3 manage.py migrate
```

5. Start server
```bash
python3 manage.py runserver
```

6. Access application
URL: http://127.0.0.1:8000/