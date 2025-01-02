# Amazon Product Tracker (Versión Local)

**Amazon Product Tracker** es una herramienta diseñada para monitorear precios de productos en Amazon. El sistema permite registrar productos, recibir notificaciones cuando los precios cambian, y consultar un historial de precios mediante gráficas generadas automáticamente. Esta versión local utiliza SQLite como base de datos y está optimizada para un uso personal.

---

## 🚀 Características

- **Registro de productos**: Añade productos de Amazon a través de su URL.
- **Notificaciones de cambios de precio**: Recibe alertas locales cuando se detectan cambios de precio.
- **Historial de precios**: Consulta gráficas con la evolución de los precios de tus productos monitoreados.
- **Interacción mediante Telegram**: Gestiona tus productos y consulta información de precios mediante comandos simples.
- **Ejecución sencilla**: Funciona perfectamente en un entorno local, sin problemas de conectividad ni dependencias externas.

---

## 📋 Requisitos

- Python 3.8 o superior.
- Cuenta en Telegram para interactuar con el bot.
- Dependencias incluidas en `requirements.txt`.

---

## 📦 Instalación y Configuración

### 1. Clona el Repositorio
```bash
git clone https://github.com/LManuXx/Amazon-Product-Tracker.git
cd Amazon-Product-Tracker
```

### 2. Instala las Dependencias
Asegúrate de que Python 3.8 o superior esté instalado en tu sistema. Luego, instala las dependencias necesarias ejecutando el siguiente comando en la terminal desde la raíz del proyecto:
```bash
pip install -r requirements.txt
```

### 3. Configura las Variables de Entorno
El bot necesita un token de API de Telegram para funcionar. Sigue estos pasos:

1. **Obtén un Token de Telegram**:
   - Abre Telegram y busca el bot **BotFather**.
   - Usa el comando `/newbot` para crear un nuevo bot.
   - Asigna un nombre y un alias al bot (por ejemplo, `PriceTrackerBot`).
   - Copia el token que BotFather te proporcionará.

2. **Crea un Archivo `.env`**:
   - En la raíz del proyecto, crea un archivo llamado `.env`.
   - Añade el token en el archivo de la siguiente manera:
     ```
     TOKEN=tu-token-de-telegram
     ```

### 4. Inicia el Bot
Ejecuta el bot utilizando el siguiente comando desde la terminal:
```bash
python tracker.py
```

El bot estará en funcionamiento y listo para interactuar. Puedes buscar tu bot en la aplicación de Telegram e iniciar una conversación enviando el comando /start.

## 🛠️ Uso

### Comandos Principales

- **/start**  
  Inicia el bot y recibe un mensaje de bienvenida con instrucciones básicas para comenzar a usarlo.

- **/add <URL>**  
  Añade un producto para monitorear utilizando su URL de Amazon.  
  **Ejemplo:**  
/add https://www.amazon.es/dp/B08HM5L35D

**Respuesta esperada:**  
Producto añadido: Nombre del Producto - Precio Inicial


- **/list**  
Muestra la lista de productos registrados con enlaces directos a Amazon y el precio actual registrado.  
**Ejemplo de respuesta:**  

Productos en seguimiento:

1.Reloj Lotus Millennial - 89,99 €


- **/checkprice <URL>**  
Consulta el precio actual de un producto registrado utilizando su URL de Amazon.  
**Ejemplo:**  
/checkprice https://www.amazon.es/dp/B08HM5L35D

**Respuesta esperada:**  
El precio del producto es: 89,99 €


- **/remove <número>**  
Elimina un producto registrado utilizando el número correspondiente mostrado en `/list`.  
**Ejemplo:**  
/remove 1

**Respuesta esperada:**  
El producto 'Reloj Lotus Millennial' ha sido eliminado del seguimiento.


- **/history <URL>**  
Genera una gráfica que muestra la evolución del precio de un producto registrado.  
**Ejemplo:**  
/history https://www.amazon.es/dp/B08HM5L35D

**Respuesta esperada:**  
El bot envía una imagen con el historial de precios.

---

## 📜 Detalles Técnicos

- **Base de Datos**  
SQLite se utiliza para almacenar usuarios, productos registrados y el historial de precios.

- **Scraping de Precios**  
Los precios se extraen de las páginas de Amazon utilizando la librería BeautifulSoup. El sistema identifica elementos específicos en el HTML de la página para obtener los datos de precio.

- **Notificaciones**  
El sistema genera notificaciones locales cada vez que se detecta un cambio en el precio de un producto. Estas notificaciones son enviadas directamente a través del bot de Telegram.

---

¿Hay algo más que te gustaría añadir o ajustar? 😊
