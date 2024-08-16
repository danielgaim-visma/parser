document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const referenceFileInput = document.getElementById('reference-file-input');
    const referenceFileName = document.getElementById('reference-file-name');
    const processBtn = document.getElementById('process-btn');
    const clearBtn = document.getElementById('clear-btn');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');

    fileInput.addEventListener('change', updateFileList);
    referenceFileInput.addEventListener('change', updateReferenceFileName);
    processBtn.addEventListener('click', processFiles);
    clearBtn.addEventListener('click', clearFiles);

    function updateFileList() {
        fileList.innerHTML = '';
        for (let file of fileInput.files) {
            const li = document.createElement('li');
            li.textContent = file.name;
            fileList.appendChild(li);
        }
    }

    function updateReferenceFileName() {
        if (referenceFileInput.files.length > 0) {
            referenceFileName.textContent = `Valgt referansefil: ${referenceFileInput.files[0].name}`;
        } else {
            referenceFileName.textContent = '';
        }
    }

    function processFiles() {
        const files = fileInput.files;
        const referenceFile = referenceFileInput.files[0];
        if (files.length === 0) {
            alert('Vennligst velg minst én fil.');
            return;
        }
        if (!referenceFile) {
            alert('Vennligst velg en referansefil.');
            return;
        }

        const formData = new FormData();
        for (let file of files) {
            formData.append('files[]', file);
        }
        formData.append('reference_file', referenceFile);
        formData.append('parse_doc', document.getElementById('parse-doc').checked);
        formData.append('create_summary', document.getElementById('create-summary').checked);
        formData.append('min_count', document.getElementById('min-count').value);
        formData.append('max_count', document.getElementById('max-count').value);
        formData.append('parse_level', document.getElementById('parse-level').value);

        loadingDiv.style.display = 'block';
        resultDiv.innerHTML = '';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Nettverksrespons var ikke ok');
            }
            return response.json();
        })
        .then(data => {
            loadingDiv.style.display = 'none';
            let resultHTML = '<h2>Behandling fullført</h2>';
            resultHTML += `<p>Batch ID: ${data.batch_id}</p>`;

            if (data.results) {
                data.results.forEach(result => {
                    if (result.filename) {
                        resultHTML += `<p>Behandlet fil: ${result.filename}</p>`;
                    }
                    if (result.doc_folder) {
                        resultHTML += `<p>Dokumentmappe: ${result.doc_folder}</p>`;
                    }
                    if (result.summary_file) {
                        resultHTML += `<p>Ordtellingssammendrag: ${result.summary_file}</p>`;
                    }
                    if (result.summary_message) {
                        resultHTML += `<p>Sammendragsmelding: ${result.summary_message}</p>`;
                    }
                });
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

    function clearFiles() {
        fileInput.value = '';
        fileList.innerHTML = '';
        referenceFileInput.value = '';
        referenceFileName.textContent = '';
        resultDiv.innerHTML = '';

        fetch('/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            alert('Opplastede filer er slettet.');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('En feil oppstod under sletting av filer.');
        });
    }
});