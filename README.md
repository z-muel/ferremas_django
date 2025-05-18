# Proyecto FERREMAS - Django

## Requisitos
- Python 3.8+
- Django 4.2+

## Instalación
1. Crear entorno virtual:
```bash
python -m venv venv
```
2. Activar entorno:
```bash
# Windows:
.\venv\Scripts\activate
```
3. Instalar dependencias:
```bash
pip install -r requirements.txt
```
4. Migraciones:
```bash
python manage.py migrate
```
5. Usuario admin:
```bash
python manage.py createsuperuser
```
6. Ejecutar:
```bash
python manage.py runserver
```

## Estructura
`/tienda` - Aplicación principal con modelos, vistas y templates