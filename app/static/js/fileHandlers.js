export function updateFileList(fileInput, fileList) {
    fileList.innerHTML = '';
    for (let file of fileInput.files) {
        const li = document.createElement('li');
        li.textContent = file.name;
        fileList.appendChild(li);
    }
}

export function updateReferenceFileName(referenceFileInput, referenceFileName) {
    if (referenceFileInput.files.length > 0) {
        referenceFileName.textContent = `Valgt referansefil: ${referenceFileInput.files[0].name}`;
    } else {
        referenceFileName.textContent = '';
    }
}

export function clearFiles(fileInput, fileList, referenceFileInput, referenceFileName, resultDiv) {
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