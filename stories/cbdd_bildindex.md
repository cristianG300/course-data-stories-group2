# AI Artist Storyteller

This interactive page brings the data from the knowledge graph to life. Select an artist from the list, and an AI will generate a unique story from their perspective, based on real data about their works, patrons, and places of activity.

<div class="llm-interactive-area">
    <p><b>1. Select an Artist:</b></p>
    <select id="artist-select" disabled>
        <option>Loading artists from the knowledge graph...</option>
    </select>

    <button id="generate-story-btn" disabled><b>2. Generate Story</b></button>
    <hr>
    <h3>The Story of...</h3>
    <div id="story-output">
        <p>Please select an artist and click "Generate Story".</p>
    </div>
</div>

<style>
    .llm-interactive-area {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 8px;
        font-family: sans-serif;
    }
    #artist-select {
        width: 100%;
        padding: 10px;
        margin-bottom: 15px;
        border-radius: 4px;
        border: 1px solid #ccc;
        background-color: white;
    }
    #generate-story-btn {
        padding: 12px 18px;
        font-size: 16px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    #generate-story-btn:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }
    #generate-story-btn:hover:not(:disabled) {
        background-color: #0056b3;
    }
    #story-output {
        margin-top: 20px;
        padding: 15px;
        background-color: white;
        border: 1px solid #eee;
        border-radius: 4px;
        white-space: pre-wrap;
        line-height: 1.6;
        min-height: 100px;
    }
</style>

<script>
    (() => {
        // --- CONFIGURATION ---
        const SPARQL_PROXY_ENDPOINT = "http://localhost:5001/sparql";
        const AI_BACKEND_ENDPOINT = "http://localhost:5001/generate-story";

        // --- DOM ELEMENTS ---
        const artistSelect = document.getElementById('artist-select');
        const generateBtn = document.getElementById('generate-story-btn');
        const storyOutput = document.getElementById('story-output');

        /**
         * A reusable function to safely send SPARQL queries via the backend proxy.
         * @param {string} query - The SPARQL query.
         * @returns {Promise<Array>} - A promise that resolves with the results (bindings).
         */
        async function querySparql(query) {
            const url = new URL(SPARQL_PROXY_ENDPOINT);
            url.searchParams.append('query', query);
            url.searchParams.append('format', 'json');
            
            const response = await fetch(url, { headers: { 'Accept': 'application/sparql-results+json' } });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`SPARQL query failed with status ${response.status}: ${errorText}`);
            }
            const json = await response.json();
            return json?.results?.bindings || [];
        }

        /**
         * Populates the dropdown menu with all artists from the dataset.
         */
        async function populateArtistsDropdown() {
            // *** CORRECTED QUERY ***
            // This query now uses schema:VisualArtwork and schema:creator as per your data model.
            const artistQuery = `
                PREFIX schema: <http://schema.org/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT DISTINCT ?artist ?artistLabel WHERE {
                    ?work a schema:VisualArtwork ;
                          schema:creator ?artist .
                    ?artist rdfs:label ?artistLabel .
                } ORDER BY ?artistLabel`;
            
            try {
                const artists = await querySparql(artistQuery);
                if (artists.length === 0) {
                    artistSelect.innerHTML = '<option>No artists found.</option>';
                    return;
                }
                artistSelect.innerHTML = '<option value="">-- Please select an artist --</option>';
                artists.forEach(artist => {
                    if (artist.artist?.value && artist.artistLabel?.value) {
                        const option = document.createElement('option');
                        option.value = artist.artist.value;
                        option.textContent = artist.artistLabel.value;
                        artistSelect.appendChild(option);
                    }
                });
                artistSelect.disabled = false;
                generateBtn.disabled = false;
            } catch (error) {
                console.error("Error populating the artist list:", error);
                artistSelect.innerHTML = '<option>Error loading artists</option>';
            }
        }
        
        async function generateStoryWorkflow() {
            const artistUri = artistSelect.value;
            const artistName = artistSelect.options[artistSelect.selectedIndex].text;
            if (!artistUri) {
                storyOutput.innerHTML = "<p>Please select an artist from the list first.</p>";
                return;
            }
            storyOutput.innerHTML = "<p>Gathering data and contacting the AI... please wait...</p>";
            generateBtn.disabled = true;

            try {
                // *** CORRECTED QUERY ***
                // This query now also uses schema:creator to find the works for the selected artist.
                const artworksQuery = `
                    PREFIX schema: <http://schema.org/>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX cto: <https://nfdi4culture.de/ontology#>
                    SELECT DISTINCT ?workLabel ?dateLabel ?locationLabel ?patronLabel WHERE {
                        <${artistUri}> rdfs:label ?artistLabel .
                        ?work schema:creator <${artistUri}> .
                        OPTIONAL { ?work rdfs:label ?workLabel . }
                        OPTIONAL { ?work cto:created_at ?date . ?date rdfs:label ?dateLabel . }
                        OPTIONAL { ?work cto:located_in ?loc . ?loc rdfs:label ?locationLabel . }
                        OPTIONAL { ?work cto:funded_by ?patron . ?patron rdfs:label ?patronLabel . }
                    } LIMIT 150`;
                const artworkResults = await querySparql(artworksQuery);
                if (artworkResults.length === 0) {
                    storyOutput.innerHTML = '<p>No detailed artwork data could be found for this artist to generate a story.</p>';
                    generateBtn.disabled = false;
                    return;
                }
                const formattedData = artworkResults.map(r => {
                    let parts = [];
                    if (r.workLabel?.value) parts.push(`my work "${r.workLabel.value}"`);
                    if (r.dateLabel?.value) parts.push(`dated ${r.dateLabel.value}`);
                    if (r.locationLabel?.value) parts.push(`at ${r.locationLabel.value}`);
                    if (r.patronLabel?.value) parts.push(`commissioned by ${r.patronLabel.value}`);
                    return `- ${parts.join(', ')}`;
                }).join('\\n');

                const aiResponse = await fetch(AI_BACKEND_ENDPOINT, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ artistName, artistData: formattedData })
                });
                if (!aiResponse.ok) throw new Error(`Backend API call failed with status ${aiResponse.status}`);
                const storyData = await aiResponse.json();
                storyOutput.innerHTML = storyData.story;
            } catch (error) {
                console.error("Error in story generation workflow:", error);
                storyOutput.innerHTML = `<p style="color: red;">An error occurred. Please check the browser console for details.</p>`;
            } finally {
                generateBtn.disabled = false;
            }
        }

        // --- INITIALIZATION ---
        generateBtn.addEventListener('click', generateStoryWorkflow);
        populateArtistsDropdown();
    })();
</script>