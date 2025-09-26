# Telling Data Stories with Semantic Technologies and Generative AI

This project combines semantic technologies with generative AI to create interactive "Data Stories." It visualizes data on baroque ceiling paintings in Germany on an interactive map and brings the artists behind the works to life through AI-generated narratives.

The project was developed as part of a course in collaboration with FIZ Karlsruhe, the AIFB at the Karlsruhe Institute of Technology, and the Academy of Sciences and Literature, Mainz.

## 🛠️ Architecture

The system uses a multi-container architecture managed with `docker-compose`, consisting of two main services:

1.  **Frontend**: A Docker container running a [MkDocs](https://www.mkdocs.org/) server. It renders the main website, which is written in Markdown (`index.md`) and includes extensive JavaScript for the interactive features (map, AI storyteller).
2.  **Backend**: A Python [Flask](https://flask.palletsprojects.com/) application that serves two critical functions:
    * **SPARQL Proxy**: Forwards all SPARQL requests from the frontend to the actual endpoint (`https://datastoriesnfdi4c.ise.fiz-karlsruhe.de/sparql`). This bypasses browser Cross-Origin (CORS) restrictions.
    * **generate-story API**: An endpoint that receives artist data, formats it into a prompt for a Large Language Model (LLM), and securely sends it to the Groq API without exposing the API key in the frontend.

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
    > **Important**: The `.env` file is used by `docker-compose` to securely pass the API key to the backend container. It should never be committed to your Git repository.

3.  **Start the Application**: When starting the container for the first time, the static site has not yet been built.  
    Run the following command once to generate the HTML output into `/src/site`:
    ```bash
    docker exec -it shmarql sh -lc 'mkdocs build -f /src/mkdocs.yml -d /src/site' 
    ```
    Launch both containers in detached mode using `docker compose`.
    ```bash
    docker compose up --build -d
    ```

4.  **View the Application**: The application should now be running.
    * Open the main page in your browser: **[http://localhost:7015/course/](http://localhost:7015/course/)**
    * The backend service is accessible at `http://localhost:5001`, though it is typically only used by the frontend application.
---
### Disclaimer
Parts of the code and documentation in this project were generated with the assistance of AI models. All generated content has been reviewed and adapted by the project contributors before inclusion.