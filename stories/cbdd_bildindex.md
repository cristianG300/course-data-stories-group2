# Data Story: Analyse barocker Kunstwerke in Deutschland

Diese Data Story basiert auf den Daten des Corpus der barocken Deckenmalereien (CbDD) und des Bildindex. Wir untersuchen die Verteilung, die Netzwerke und die Themen dieser Kunstwerke.

<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.9/dist/vis-network.min.js"></script>

---

### 1. Verteilung nach Kunstform und -medium

Wir beginnen mit einer grundlegenden Frage: Welche Arten von Kunstwerken sind im Datensatz am häufigsten vertreten? Die Abfrage nutzt `cto:has_form`, um die Kunstform jedes `cto:Artwork` zu identifizieren.

<shmarql-query id="q1">
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?artformLabel (COUNT(?work) AS ?count)
WHERE {
  ?work a cto:Artwork ;
        cto:has_form ?artform .
  ?artform rdfs:label ?artformLabel .
  FILTER(LANG(?artformLabel) = "de")
}
GROUP BY ?artformLabel
ORDER BY DESC(?count)
LIMIT 10
</shmarql-query>

<div id="plot1"></div>
<script>
document.addEventListener('shmarql-success-q1', (event) => {
  const data = event.detail.results.bindings.map(row => ({
    label: row.artformLabel.value,
    value: parseInt(row.count.value)
  }));
  Plotly.newPlot('plot1', [{ x: data.map(d => d.label), y: data.map(d => d.value), type: 'bar' }], {title: 'Top 10 Kunstformen'});
});
</script>

---

### 2. Verbindungen zwischen Künstlern und Förderern

Kunst braucht Finanzierung. Das folgende Netzwerkdiagramm visualisiert die Beziehungen zwischen Künstlern (`cto:created_by`) und ihren Förderern (`cto:funded_by`).

<shmarql-query id="q2">
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?creatorLabel ?funderLabel
WHERE {
  ?work a cto:Artwork ;
        cto:created_by ?creator ;
        cto:funded_by ?funder .
  ?creator rdfs:label ?creatorLabel .
  ?funder rdfs:label ?funderLabel .
}
LIMIT 50
</shmarql-query>

<div id="plot2" style="height: 500px; border: 1px solid #ddd;"></div>
<script>
document.addEventListener('shmarql-success-q2', (event) => {
    const bindings = event.detail.results.bindings;
    const nodes = new vis.DataSet();
    const edges = [];
    const nodeLabels = new Set();
    bindings.forEach(row => {
        const creator = row.creatorLabel.value;
        const funder = row.funderLabel.value;
        if (!nodeLabels.has(creator)) { nodes.add({ id: creator, label: creator, group: 'creator' }); nodeLabels.add(creator); }
        if (!nodeLabels.has(funder)) { nodes.add({ id: funder, label: funder, group: 'funder' }); nodeLabels.add(funder); }
        edges.push({ from: creator, to: funder });
    });
    const data = { nodes: nodes, edges: edges };
    const options = {
        groups: {
          creator: { color: { background: 'rgba(0, 123, 255, 0.8)' } },
          funder: { color: { background: 'rgba(255, 193, 7, 0.8)' } }
        }
    };
    new vis.Network(document.getElementById('plot2'), data, options);
});
</script>

---

### 3. Ikonographische Themen

Welche Motive waren im Barock populär? Wir analysieren die `cto:has_iconography`-Relation, um die am häufigsten dargestellten Themen zu finden.

<shmarql-query id="q3">
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?iconclassLabel (COUNT(?work) AS ?count)
WHERE {
  ?work a cto:Artwork ;
        cto:has_iconography ?iconclass .
  ?iconclass rdfs:label ?iconclassLabel .
}
GROUP BY ?iconclassLabel
ORDER BY DESC(?count)
LIMIT 15
</shmarql-query>

<div id="plot3"></div>
<script>
document.addEventListener('shmarql-success-q3', (event) => {
  const data = event.detail.results.bindings.map(row => ({
    label: row.iconclassLabel.value,
    value: parseInt(row.count.value)
  })).reverse();
  Plotly.newPlot('plot3', [{ y: data.map(d => d.label), x: data.map(d => d.value), type: 'bar', orientation: 'h' }], {title: 'Top 15 Ikonographische Themen', margin: { l: 350 }});
});
</script>

---

### 4. Anzahl der Kunstwerke pro Künstler

Welche Künstler waren am produktivsten? Diese Abfrage zählt die Werke (`cto:Artwork`) pro Künstler (`cto:created_by`).

<shmarql-query id="q4">
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?artistLabel (COUNT(?work) AS ?count)
WHERE {
  ?work a cto:Artwork ;
        cto:created_by ?artist .
  ?artist rdfs:label ?artistLabel .
}
GROUP BY ?artistLabel
ORDER BY DESC(?count)
LIMIT 10
</shmarql-query>

<div id="plot4"></div>
<script>
document.addEventListener('shmarql-success-q4', (event) => {
  const data = event.detail.results.bindings.map(row => ({
    label: row.artistLabel.value,
    value: parseInt(row.count.value)
  }));
  Plotly.newPlot('plot4', [{ x: data.map(d => d.label), y: data.map(d => d.value), type: 'bar' }], {title: 'Top 10 Künstler nach Anzahl der Werke'});
});
</script>

---

### 5. Geografische Verteilung der Kunstwerke

Wo befinden sich die Kunstwerke? Diese Karte nutzt die `cto:located_in`-Relation und die Geo-Koordinaten (`schema:latitude` & `schema:longitude`), um die Standorte zu visualisieren.

<shmarql-query id="q5">
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
SELECT ?locLabel ?lat ?lon
WHERE {
  ?work a cto:Artwork ;
        cto:located_in ?loc .
  ?loc rdfs:label ?locLabel ;
       schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
}
LIMIT 200
</shmarql-query>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<div id="plot5" style="height: 500px;"></div>
<script>
document.addEventListener('shmarql-success-q5', (event) => {
  const locations = event.detail.results.bindings.map(row => ({
    label: row.locLabel.value,
    lat: parseFloat(row.lat.value),
    lon: parseFloat(row.lon.value)
  }));
  const map = L.map('plot5').setView([51.16, 10.45], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);
  locations.forEach(loc => { L.marker([loc.lat, loc.lon]).addTo(map).bindPopup(loc.label); });
});
</script>

---

### 6. KI-Künstler-Geschichtenerzähler

Als Abschluss erwecken wir die Daten zum Leben. Wählen Sie einen Künstler, und eine KI erzählt eine Geschichte aus dessen Perspektive, basierend auf den Daten aus dem Wissensgraphen.

<div class="llm-interactive-area">
    <p>Künstler auswählen:</p>
    <select id="artist-select" disabled><option>Lade Künstler...</option></select>
    <button id="generate-story-btn">Geschichte generieren</button>
    <hr>
    <h3>Die Geschichte von...</h3>
    <div id="story-output"><p>Die Geschichte wird hier erscheinen.</p></div>
</div>

<style>
    .llm-interactive-area{background-color:#f9f9f9;border:1px solid #ddd;padding:20px;border-radius:8px;}
    #artist-select{width:100%;padding:8px;margin-bottom:10px;}
    #generate-story-btn{padding:10px 15px;background-color:#007bff;color:white;border:none;border-radius:4px;cursor:pointer;}
    #story-output{margin-top:20px;white-space:pre-wrap;line-height:1.6;}
</style>

<script>
    (() => {
        const SPARQL_ENDPOINT = "https://datastoriesnfdi4c.ise.fiz-karlsruhe.de/sparql";
        const BACKEND_API_URL = "http://localhost:5001/generate-story";

        const artistSelect = document.getElementById('artist-select');
        const generateBtn = document.getElementById('generate-story-btn');
        const storyOutput = document.getElementById('story-output');

        async function querySparql(query) {
            const url = new URL(SPARQL_ENDPOINT);
            url.searchParams.append('query', query);
            url.searchParams.append('format', 'json');
            const response = await fetch(url, { headers: { 'Accept': 'application/sparql-results+json' } });
            if (!response.ok) throw new Error('SPARQL query failed');
            return (await response.json()).results.bindings;
        }

        async function populateArtists() {
            const query = `
                PREFIX cto: <https://nfdi4culture.de/ontology#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT DISTINCT ?artist ?artistLabel WHERE {
                    ?work a cto:Artwork ; cto:created_by ?artist .
                    ?artist rdfs:label ?artistLabel .
                } ORDER BY ?artistLabel`;
            try {
                const artists = await querySparql(query);
                artistSelect.innerHTML = '<option value="">-- Bitte wählen --</option>';
                artists.forEach(artist => {
                    const option = document.createElement('option');
                    option.value = artist.artist.value;
                    option.textContent = artist.artistLabel.value;
                    artistSelect.appendChild(option);
                });
                artistSelect.disabled = false;
            } catch (error) { console.error(error); }
        }

        generateBtn.addEventListener('click', async () => {
            const artistUri = artistSelect.value;
            const artistName = artistSelect.options[artistSelect.selectedIndex].text;
            if (!artistUri) { return; }

            storyOutput.innerHTML = '<p>Generiere Geschichte...</p>';

            try {
                const artistDataQuery = `
                    PREFIX cto: <https://nfdi4culture.de/ontology#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    SELECT DISTINCT ?workLabel ?dateLabel ?locationLabel ?patronLabel WHERE {
                        <${artistUri}> rdfs:label ?artistLabel .
                        ?work cto:created_by <${artistUri}> .
                        OPTIONAL { ?work rdfs:label ?workLabel . }
                        OPTIONAL { ?work cto:created_at ?date . ?date rdfs:label ?dateLabel . }
                        OPTIONAL { ?work cto:located_in ?loc . ?loc rdfs:label ?locationLabel . }
                        OPTIONAL { ?work cto:funded_by ?patron . ?patron rdfs:label ?patronLabel . }
                    } LIMIT 30`;
                
                const results = await querySparql(artistDataQuery);
                const formattedData = results.map(r => {
                    let parts = [];
                    if (r.workLabel?.value) parts.push(`Werk: ${r.workLabel.value}`);
                    if (r.dateLabel?.value) parts.push(`datiert auf ${r.dateLabel.value}`);
                    if (r.locationLabel?.value) parts.push(`in ${r.locationLabel.value}`);
                    if (r.patronLabel?.value) parts.push(`im Auftrag von ${r.patronLabel.value}`);
                    return `- ${parts.join(', ')}`;
                }).join('\\n');

                if (!formattedData) {
                    storyOutput.innerHTML = '<p>Keine ausreichenden Daten für eine Geschichte gefunden.</p>';
                    return;
                }

                const response = await fetch(BACKEND_API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ artistName, artistData: formattedData })
                });

                if (!response.ok) throw new Error('Backend API call failed');
                const data = await response.json();
                storyOutput.innerHTML = data.story;

            } catch (error) { console.error(error); }
        });

        populateArtists();
    })();
</script>