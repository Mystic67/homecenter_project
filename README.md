# Project 13 : HomeCenter (Domotique)

## **I. Présentation**
L' application HomeCenter est une application web domotique, écrite en Python 3, 
permettant de piloter les volets roulants ainsi que les luminaire de votre domicile 
depuis un ordinateur, une tablette ou un smartphone.  
Elle utilise des périphériques réseau sans fil au protocole Z-wave (868 MHz).  
Elle dispose d'un système de login ainsi qu'un système de gestion des utilisateurs  
ainsi qu'une interface de configuration des modules "Z-wave" simplifiée. 

## **II. Prérequis**
L'application nécessite l'installation électrique de modules et l'inclusion de ces 
modules au stick USB, afin de créer le réseau "Z-wave".  
Vous trouverez toutes les informations nécessaires, sur la compatibilité des 
modules domotique ainsi que sur leurs installations dans le 
[dossier de conception technique](https://github.com/Mystic67/homecenter_project/tree/master/doc/Dossier%20de%20conception%20technique%20-%20Projet%20HomeCenter.pdf)
associée à ce projet.
L'application nécessite également d'être hébergé sur un petit serveur local à votre 
domicile pour communiquer avec le réseau Z-wave par le biais d'un stick Z-wave USB.  
Un Raspberry Pi 3b ou supérieur, avec une distribution Linux Raspbian (Linux Debian pour Raspberry) 
est un choix pertinent pour son coût réduit et son faible encombrement, néanmoins, vous pouvez
également recycler un ancien pc ou pc barbone sous linux, ayant au minimum une de puissance équivalente
au Raspberry Pi 3b.  
Pour la configuration de l'application en production et des serveurs logiciels (NGINX, Supervisor), 
vous trouverez des modèles de fichier de configuration dans le 
[dossier de conception technique](https://github.com/Mystic67/homecenter_project/tree/master/doc/Dossier%20de%20conception%20technique%20-%20Projet%20HomeCenter.pdf)
ainsi qu'au bas de ce document.
   
**Fonctionnalités générales:**
L'utilisation de l'application est instinctive, néanmoins vous trouverez des explications 
sur son fonctionnement dans la rubrique " 3.1 Le principe de fonctionnement " du 
[dossier de conception fonctionnelle](https://github.com/Mystic67/homecenter_project/tree/master/doc/Dossier%20de%20conception%20fonctionnelle%20-%20Projet%20HomeCenter.pdf).
  
**NB:** 
1. Après la procédure d'installation de l'application "HomeCenter", décrite plus bas, 
vous aurez créé un utiisateur disposant des droits "super-utilisateur". 
Cet utilisateur fera partie du "Staff" et ne pourra pas être supprimé depuis 
l'interface d'administration des utilisateurs, contrairement aux autres utilisateurs 
créés depuis l'interface.  
  
2. Lors du premier démarrage, aucun module volet ou lumière ne sera disponibles sur 
les pages de l'interface utilisateur, tant que le super-utilisateur n'aura pas démarrer 
une première fois le réseau "Z-wave".   
  
## **II. Installation**

**Prérequis:**
1. Télécharger et installer Python3:  
    Voir le page: <https://www.python.org/downloads/>
2. installer pip dans votre terminal. (mode console):   
   Voir la page: <https://pip.pypa.io/en/stable/installing/>

**Installation du repository et de l'environement:**
1. Ouvrir votre therminal préféré et créer un répertoire pour le projet.  
   ex: `mkdir Ma_maison`
2. Aller dans le repertoire que vous venez de créer.  
   ex: `cd Ma_maison`
3. Installer un outils de création d'environement vituel (pipenv dans notre exemple)
   `pip install pipenv`     
4. Cloner ou télécharger le repository Git du projet dans le répertoire que vous venez de créer.
   ex: `git clone https://github.com/Mystic67/homecenter_project.git`
5. Aller dans le repertoire racine du projet.
    `cd /homecenter_project`  (/Ma_maison/homecenter_project)
6. Créer votre environement virtuel pipenv et installer les dépendances:
    `pipenv --three sync`

**Créer la base de données:**
Depuis votre environnement vituel (pipenv shell)
1. créer la base de données.
   ex: `python manage.py migrate`

**Créer l'utilisateur principal de l'application avec les droits "super-utilisateur" et "staff":**
Depuis votre environnement vituel (pipenv shell)
1. Créer l'utilisateur
   `python manage.py createsuperuser`
2. Répondre aux questions (nom, e-mail, mot de passe)

**Collecter les fichiers static nécessaires à l'appication:**
    `python manage.py collectstatic`

#### **Créer le fichier de configuration de production**
1. Allez dans le dossier settings de l'aapplication (/Ma_maison/homecenter_project/homecenter_project/settings)
     `cd ./homecenter_project/settings`
2. Créer et Editer le fichier "production.py" avec votre éditeur favori (vim, nano etc...)
     ex: `nano production.py`
      
3. Copier/coller dans ce fichier, le modèle de fichier "prodution.py" situé dans la section III au bas de ce document.
  
4. Modifier le contenu du fichier avec vos données tel que décrit dans les commentaires du fichier  
(Clé d'aapplication, adresse ip et données d'accès à votre serveur mail)  
  
5. Enregister les données.
       
#### **Installer et démarrer l'application serveur NGINX sur votre serveur physique sous Raspbian ou Debian :**  
1. Installer le serveur   
   `sudo apt install nginx`  
   
2. Créer et Editer le fichier de configuration "homecenter.conf" pour le serveur NGINX, dans le répertoire (/etc/nginx/sites-available/)  
   `sudo nano /etc/nginx/sites-available/homecenter.conf` 
    
3. Copier/coller dans ce fichier, le modèle de fichier "homecenter.cong" pour NGINX, situé dans la section III au bas de ce document.  
   ##### *Attention*: de ne pas confondre avec le fichier pour Supervisor qui porte le même nom. 
    
4. Modifier le contenu du fichier avec vos données tel que décrit dans les commentaires du fichier  
(Clé d'aapplication, adresse ip et données d'accès à votre serveur mail)  
    
5. Enregister les données.

6. Céer un lien symbolique dans le répertoire /etc/nginx/sites-enabled/ pour activer la configuration
   `sudo ln -s /etc/nginx/sites-enabled/homecenter.conf /etc/nginx/sites-enabled/homecenter.conf`

7. Démarrer le serveur NGINX  
   `sudo service nginx start`

#### **Pour démarrer le serveur "gunicorn" automatiquement via l'application "supervisor":**  
1. Installer l'application "supervisor"   
   `sudo apt install supervisor`  
   
2. Créer et Editer le fichier de configuration "homecenter.conf" pour "supervisor", dans le répertoire (/etc/supervisor/conf.d/)  
   `sudo nano /etc/supervisor/conf.d/homecenter.conf` 
    
3. Copier/coller dans ce fichier, le modèle de fichier "homecenter.cong" pour NGINX, situé dans la section III au bas de ce document.  
   ##### *Attention*: de ne pas confondre avec le fichier pour NGINX qui porte le même nom. 
    
4. Modifier le contenu du fichier avec vos données tel que décrit dans les commentaires du fichier    
(Chemin vers l'application gunicorn de votre environement virtuel, nom de session utilisateur, chemin du projet )  
    
5. Enregister les données.  

6. Mettre à jour et démarrer l'application supervisor. 
    `sudo supervisorctl reread`  
    `sudo supervisorctl update`  #L'aplication se met à jour et démarre.
    
**NB:** 
pour démarrer ou arrête l'application utiliser respectivement les commandes suivante:  
`sudo supervisorctl start homecenter` ou `sudo supervisorctl stop homecenter`

A ce stade, l'application est démarré en production et vous pouvez accéder à l'application depuis votre réseau local (intranet)         
Rendre à l'adresse local indiquée dans le terminal avec votre navigateur web préféré.  
Ex: http://127.0.0.1:5000 ou http://localhost:5000


## **III. Modèles de fichiers de configuration**
Fichier modèle de configuration pour les "settings" de l'application. 
#### **production.py**
    from . import *
    SECRET_KEY = "Votre clé d’application" # Remplacer par votre clé d’application 
    DEBUG = False
    ALLOWED_HOSTS = ['votre adresse ip', 'votre non de domaine'] # Entrer ici vos adresses ip d’accès et/ou vos nom de domaine, séparé par des virgules.
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'homecenter_db.sqlite3'),
        }
    }
    
    # Configurer ici votre serveur de mail SMTP pour la réinitialisation du mot de #passe 
    # utilisateur
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'mail.gandi.net'# Remplacer par le nom d’hôte de votre serveur mail d'envoi
    EMAIL_PORT = 587  # Remplacer par le port de votre serveur mail
    EMAIL_USE_TLS = True  # Activation du Protocol TLS
    EMAIL_HOST_USER = 'mon_d’utilisateur_du_serveur_SMTP'  # Remplacer par le nom d’utilisateur de votre serveur SMTP
    EMAIL_HOST_PASSWORD = 'mot_de_passe_du_serveur_SMTP'  # Remplacer par le Mot de passe de votre serveur SMTP
    DEFAULT_FROM_EMAIL = 'email@nom_de_domaine.com'  # Remplacer par votre adresse mail d'envoi par défaut
    SERVER_EMAIL = 'serveur_mail_envoi'  # Remplacer par le votre serveur mail d’envoi

Fichier modèle de configuration pour le serveur NGINX
#### **homecenter.conf (NGINX)**
    server {
           listen 80;
           listen [::]:80;
        # Commenter les lignes ci-dessus et décommander les lignes ci-dessous en mode SSL
           #listen 443;
           #listen [::]:443;
    
            # Logs
            access_log  /var/log/nginx/permit_access.log;
            error_log   /var/log/nginx/permit_error.log;
    
            # Entrer l’adresse ip de votre serveur et/ou votre nom de domaine
        server_name localhost mon_adresse_ip mon_nom_de_domaine; 
        
            # SSL
         # Décommenter les lignes ci-dessous si vous utiliser un certificat SSL 
            # ssl on;
            # ssl_certificate /chemin/mon_certificat.crt;  # Remplacer par votre fichier certificat crt
            # ssl_certificate_key /chemin/mon_certificat.key;  # Remplacer par votre clé de certificat
    
            # Root directory
            root /chemin_vers_projet/homecenter_project/; # Remplacer par votre chemin d’installation
    
            # Staticfiles location
            location /static {
            alias /chemin_vers_projet/homecenter_project/static/;# Remplacer par votre chemin d’install.
            }
    
            location / {
                    proxy_set_header Host $http_host;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_redirect off;
                    if (!-f $request_filename) {
                        proxy_pass http://127.0.0.1:5000; # Remplacer le port si vous le modifier
                        break;
                    }
                    proxy_set_header X-Real-IP $remote_addr;
            }
    
            location /socket.io {
                    proxy_pass         http://0.0.0.0:5000/socket.io; # Remplacer le port si vous le 										# modifier
                    proxy_redirect     off;
                    proxy_buffering    off;
    
                    proxy_set_header   Host             $host;
                    proxy_set_header   X-Real-IP        $remote_addr;
                    proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
    
                    # Websockets support
                    proxy_http_version 1.1;
                    proxy_set_header   Upgrade          $http_upgrade;
                    proxy_set_header   Connection       "upgrade";
            }
    }   

Fichier modèle de configuration pour l'application Supervisor
#### **homecenter.conf (NGINX)**
    [program:homecenter]
    # Remplacer par le chemin vers le serveur d’application gunicorn de votre environnement virtuel
    command=/home/chemin_vers_serveur_app/bin/gunicorn -k gevent -w 1 -b 127.0.0.1:5000 homecenter_project.wsgi:application
    
    # Remplacer par le nom d’utilisateur de votre session linux
    user = votre_nom_utilisateur_de_session
    directory = /home/chemin_de_votre_projet/homecenter_project
    autostart = true
    autorestart = true
    environment = DJANGO_SETTINGS_MODULE='homecenter_project.settings.production'
   
   
    
    
       
       
     
    


