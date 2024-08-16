document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const processBtn = document.getElementById('process-btn');
    const clearBtn = document.getElementById('clear-btn');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');

    fileInput.addEventListener('change', updateFileList);
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

    function processFiles() {
        const files = fileInput.files;
        if (files.length === 0) {
            alert('Vennligst velg minst én fil.');
            return;
        }

        const formData = new FormData();
        for (let file of files) {
            formData.append('files[]', file);
        }
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
            resultDiv.innerHTML = `
                <h2>Behandling fullført</h2>
                <p>Batch ID: ${data.batch_id}</p>
                <a href="/download/${data.batch_id}" download>Last ned resultater</a>
            `;
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
        resultDiv.innerHTML = '';

        fetch('/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});