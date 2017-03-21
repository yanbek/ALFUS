# ALFUS

Ved endring av modell prøv først:

python manage.py makemigrations
python manage.py migrate

Hvis ikke dette fungerer så slett db.sqlite3 og kjør
makemigrations og migrate pånytt.

Skriv manage.py createsuperuser for å lage adminbruker. 

Crispy forms må installeres for å kjøre serveren.
pip install django-crispy-forms eller pip3 install django-crispy-forms

Skriv manage.py runcrons for å oppdatere vanskelighetsgraden på oppgavene.
pip install django-crons
