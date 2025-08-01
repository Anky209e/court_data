# Delhi High Court Case Scraper & Dashboard

This project is a Flask web application that allows you to search for Delhi High Court case details, view all associated order/judgment PDFs, and maintain a searchable dashboard of your queries.  
It uses Selenium to interact with the court's website and BeautifulSoup for HTML parsing.

---

## Features

- **Search by Case Type, Number, and Year**  
- **View all available order/judgment PDFs for a case**
- **Dashboard of all your queries**
- **No raw HTML stored, only structured data**
- **Dockerized for easy deployment**
- **No secret keys exposed in code**

---

## Requirements

- Docker (recommended)  
  or  
- Python 3.11+
- Google Chrome/Chromium and ChromeDriver (if running locally)
- The following Python packages:
    - Flask
    - selenium
    - beautifulsoup4

---

## Quick Start (Docker)

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/court_data.git
    cd court_data
    ```

2. **Build the Docker image:**
    ```sh
    docker build -t court-data-app .
    ```

3. **Run the container:**
    ```sh
    docker run -p 5000:5000 -e FLASK_SECRET_KEY='your-very-secret-key' court-data-app
    ```

4. **Visit [http://localhost:5000](http://localhost:5000) in your browser.**

---

## Local Development

1. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

2. **Ensure Chrome/Chromium and ChromeDriver are installed and in your PATH.**

3. **Set your secret key (optional but recommended):**
    ```sh
    export FLASK_SECRET_KEY='your-very-secret-key'
    ```

4. **Run the app:**
    ```sh
    python app.py
    ```

---

## Project Structure

```
court_data/
├── app.py                # Flask app (main entry point)
├── bs_hc_scrap.py        # Selenium & BeautifulSoup scraper
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker build instructions
├── .dockerignore         # Docker ignore file
├── db.sqlite3            # SQLite database (auto-created)
└── templates/
    ├── index.html
    ├── dashboard.html
    └── query_detail.html
```

---

## Security

- **Secret keys are never hardcoded.**  
  Set `FLASK_SECRET_KEY` as an environment variable.
- **Database and cache files are excluded from Docker images.**

---

## Notes

- The app fetches available case types and years from the Delhi High Court site at startup.
- Selenium runs in headless mode and is configured for Docker compatibility.
- Only valid, found cases are stored in the database. If no data is found, a message is shown and nothing is stored.

---

## Troubleshooting

- If you see errors about Chrome/Chromedriver, ensure they are installed and compatible.
- If you get `no such element` errors, the court website may have changed its layout.
- For Docker, all dependencies are handled in the Dockerfile.

---

## License

MIT License

---

## Disclaimer

This project is for educational and research purposes only.  
It is not affiliated with the Delhi High Court.  
Use responsibly and respect the court's website terms of service.