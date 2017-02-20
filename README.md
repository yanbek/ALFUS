# ALFUS

Ved endring av modell prøv først:

python manage.py makemigrations
python manage.py migrate

Hvis ikke dette fungerer så slett db.sqlite3 og kjør
makemigrations og migrate pånytt.

Skriv manage.py createsuperuser for å lage adminbruker. 
