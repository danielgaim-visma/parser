export function processFiles(form, loadingDiv, resultDiv) {
    const formData = new FormData(form);

    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Nettverksrespons var ikke ok');
            });
        }
        return response.json();
    })
    .then(data => {
        loadingDiv.style.display = 'none';
        let resultHTML = '<h2>Behandling fullført</h2>';
        resultHTML += `<p>Batch ID: ${data.batch_id}</p>`;

        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                if (result.file) {
                    resultHTML += `<p>Behandlet fil: ${result.file}</p>`;
                }
                if (result.output_folder) {
                    resultHTML += `<p>Dokumentmappe: ${result.output_folder}</p>`;
                }
                if (result.summary_file) {
                    resultHTML += `<p>Ordtellingssammendrag: ${result.summary_file}</p>`;
                }
                if (result.summary_message) {
                    resultHTML += `<p>Sammendragsmelding: ${result.summary_message}</p>`;
                }
                if (result.error) {
                    resultHTML += `<p>Feil: ${result.error}</p>`;
                }
            });
        } else {
            resultHTML += '<p>Ingen resultater generert. Vennligst sjekk innstillingene dine og prøv igjen.</p>';
        }

        resultHTML += `<a href="/download/${data.batch_id}" download>Last ned resultater</a>`;
        resultDiv.innerHTML = resultHTML;
    })
    .catch(error => {
        loadingDiv.style.display = 'none';
        console.error('Error:', error);
        resultDiv.innerHTML = `<p>En feil oppstod: ${error.message}</p>`;
    });
}