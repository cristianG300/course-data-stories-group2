# Telling Data Stories with Semantic Technologies and Generative AI

This project combines semantic technologies with generative AI to create interactive "Data Stories." It visualizes data on baroque ceiling paintings in Germany on an interactive map and brings the artists behind the works to life through AI-generated narratives.

The project was developed as part of a course in collaboration with FIZ Karlsruhe, the AIFB at the Karlsruhe Institute of Technology, and the Academy of Sciences and Literature, Mainz.



---

## ✨ Features

* **Interactive Map Visualization**: Displays the geographical locations of artworks from the knowledge graph. Locations with multiple works are clustered for a clearer overview.
* **Detail Popups**: Clicking on a map point reveals detailed information about the artworks at that location, including title, artist, location, and a thumbnail image.
* **AI-Powered Storyteller**:
    * Dynamically loads a list of artists from the SPARQL endpoint.
    * Generates a unique, first-person story about the life and work of a selected artist at the click of a button.
    * [cite_start]Utilizes a Python backend service to retrieve data from the knowledge graph and send a request to the Groq API (using the Llama 4 model). [cite: 1]
* [cite_start]**SPARQL Integration**: Includes a read-only SPARQL query editor to explore the knowledge graph directly. [cite: 1]

---

## 🛠️ Architecture

The system uses a multi-container architecture managed with `docker-compose`, consisting of two main services:

1.  **Frontend (`shmarql`)**: A Docker container running an [MkDocs](https://www.mkdocs.org/) server. It renders the main website, which is written in Markdown (`index.md`) and includes extensive JavaScript for the interactive features (map, AI storyteller).
2.  **Backend (`llm_backend`)**: A Python [Flask](https://flask.palletsprojects.com/) application that serves two critical functions:
    * **SPARQL Proxy**: Forwards all SPARQL requests from the frontend to the actual endpoint (`https://datastoriesnfdi4c.ise.fiz-karlsruhe.de/sparql`). This bypasses browser Cross-Origin (CORS) restrictions.
    * **/generate-story API**: An endpoint that receives artist data, formats it into a prompt for a Large Language Model (LLM), and securely sends it to the Groq API without exposing the API key in the frontend.



---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

You need Git and a container runtime that provides the `docker` and `docker-compose` commands.

* **For Windows**: We recommend installing **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**.
    1.  Download the installer from the official website.
    2.  Run the installer and follow the on-screen instructions. It will automatically install Docker, the Docker CLI, and Docker Compose.
    3.  After installation, start Docker Desktop. Make sure the Docker whale icon in the system tray is stable (not animating), which indicates the service is running.

* **For macOS**: We recommend **[OrbStack](https://orbstack.dev/)** as a faster, more lightweight alternative to Docker Desktop.
    1.  Download OrbStack from the official website.
    2.  Open the downloaded `.dmg` file and drag the OrbStack icon into your Applications folder.
    3.  Start OrbStack. It will automatically provide the `docker` and `docker-compose` commands in your terminal. You can verify this by running `docker --version`.

* **Git**: Ensure you have [Git](https://git-scm.com/) installed.

### Installation Guide

1.  **Clone the Repository**: Clone this repository to your local machine.
    ```bash
    git clone git@github.com:YOUR_USERNAME/course-data-stories-group2.git
    cd course-data-stories-group2
    ```

2.  **Configure API Key**: The AI storyteller feature requires a Groq API key.
    * Create a new file named `.env` in the root directory of the project.
    * Add your Groq API key to the `.env` file. You can get a free key from the [Groq website](https://console.groq.com/keys).
    ```env
    # .env
    GROQ_API_KEY=your_groq_api_key_here
    ```
    > **Important**: The `.env` file is used by `docker-compose` to securely pass the API key to the backend container[cite: 1]. It should never be committed to your Git repository.

3.  **Start the Application**: Launch both containers in detached mode using `docker compose`.
    ```bash
    docker compose up -d
    ```

4.  **View the Application**: The application should now be running.
    * Open the main page in your browser: **[http://localhost:7015/course/](http://localhost:7015/course/)**
    * The backend service is accessible at `http://localhost:5001`, though it is typically only used by the frontend application. [cite: 1]

---

## ⚙️ How It Works

### Interactive Map Data Flow

1.  When the page loads, the JavaScript in the browser sends a SPARQL query to get the artwork locations.
2.  The request goes to the local backend service (`http://localhost:5001/sparql`). [cite: 1]
3.  The Flask backend proxy forwards this request to the real public SPARQL endpoint. [cite: 1]
4.  The results are sent back to the browser.
5.  The JavaScript processes the geo-data and uses Leaflet.js to render the markers on the map.

### AI Storyteller Data Flow

1.  **Load Artists**: On page load, a SPARQL query is sent via the backend proxy to get a list of all artists, which populates the dropdown menu.
2.  **Generate Story**:
    * When you select an artist and click "Generate Story," a second SPARQL query is sent to gather detailed data about that specific artist (works, funders, art forms, etc.).
    * This data is sent to the `/generate-story` endpoint of the Flask backend (`http://localhost:5001/generate-story`). [cite: 1]
    * The backend creates a detailed prompt instructing the AI to act as the artist and use only the provided facts.
    * The prompt is sent to the Groq API.
    * The story generated by the AI is returned to the browser and displayed on the page.

---

## 📁 File Structure:
├── backend/
│   ├── app.py             # Flask-Anwendung (SPARQL-Proxy & KI-Endpunkt)
│   ├── Dockerfile         # Docker-Anweisungen für das Backend
│   └── requirements.txt   # Python-Abhängigkeiten 
├── stories/
│   └── index.md           # Haupt-Markdown-Datei mit HTML, CSS und JS
├── .env                   # (Von dir erstellt) Speichert den GROQ_API_KEY
├── docker-compose.yml     # Definiert und konfiguriert die Frontend- und Backend-Dienste
├── navigation.yml         # Konfiguration der Seitennavigation für MkDocs
├── README.md              # Diese Readme-Datei
└── sparql-01.rq           # Beispiel für eine SPARQL-Abfrage