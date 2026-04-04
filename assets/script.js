document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const loader = document.getElementById('loader');
    const loaderText = document.getElementById('loaderText');
    const alertBox = document.getElementById('alertBox');
    
    const iframeContainer = document.getElementById('mapIframe');
    const emptyState = document.getElementById('emptyState');
    const mapTitle = document.getElementById('mapTitle');
    const btnDownloadPdf = document.getElementById('btnDownloadPdf');
    const btnDownloadPng = document.getElementById('btnDownloadPng');
    const mapActions = document.getElementById('mapActions');
    
    const btnSyncFolder = document.getElementById('btnSyncFolder');
    
    if (btnSyncFolder) {
        btnSyncFolder.addEventListener('click', () => {
            loader.classList.add('active');
            loaderText.textContent = `Varrendo a pasta de entrada... Aguarde o processamento em massa.`;
            alertBox.classList.add('d-none');

            fetch('sync.php')
            .then(response => response.json())
            .then(data => {
                loader.classList.remove('active');
                if (data.success) {
                    showAlert(data.message, 'success');
                    // Recarregar lista
                    const fileList = document.getElementById('fileList');
                    // Limpar provisoriamente pra atualizar com novos
                    if (data.mapas.length > 0) {
                        data.mapas.forEach(m => addToList(m));
                    }
                } else {
                    showAlert(data.message || 'Erro ao sincronizar.', 'error');
                }
            })
            .catch(error => {
                loader.classList.remove('active');
                showAlert('Falha na comunicação com o servidor.', 'error');
            });
        });
    }

    // Drag & Drop
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
        });

        uploadArea.addEventListener('drop', handleDrop, false);
        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFiles(this.files);
            }
        });
    }

    function handleDrop(e) {
        let dt = e.dataTransfer;
        let files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length === 0) return;
        const file = files[0];
        
        const fileName = file.name.toLowerCase();
        if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
            showAlert('Por favor, envie apenas arquivos nos formatos .xlsx ou .xls', 'error');
            return;
        }

        uploadFile(file);
    }

    function showAlert(message, type) {
        alertBox.textContent = message;
        alertBox.className = `alert alert-${type}`;
        alertBox.classList.remove('d-none');
        setTimeout(() => alertBox.classList.add('d-none'), 5000);
    }

    function loadMapInIframe(htmlPath, pdfPath, pngPath, name) {
        emptyState.classList.add('d-none');
        iframeContainer.classList.remove('d-none');
        mapActions.classList.remove('d-none');
        
        // Anti-cache pra sempre carregar a versao nova
        iframeContainer.src = htmlPath + '?_t=' + new Date().getTime();
        mapTitle.textContent = name;
        
        btnDownloadPdf.onclick = () => window.open(pdfPath, '_blank');
        btnDownloadPng.onclick = () => window.open(pngPath, '_blank');
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('arquivo_xlsx', file);

        loader.classList.add('active');
        loaderText.textContent = `Enviando e processando ${file.name}... Isso pode levar alguns segundos.`;
        alertBox.classList.add('d-none');

        fetch('upload.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loader.classList.remove('active');
            if (data.success) {
                showAlert('Mapa processado com sucesso!', 'success');
                // Adicionar a lista visualmente
                addToList(data.mapaInfo);
                // Carregar no iframe
                loadMapInIframe(data.mapaInfo.html, data.mapaInfo.pdf, data.mapaInfo.png, data.mapaInfo.nome);
            } else {
                showAlert(data.message || 'Ocorreu um erro no servidor.', 'error');
            }
        })
        .catch(error => {
            loader.classList.remove('active');
            showAlert('Falha na comunicação com o servidor. O processador backend pode estar offline.', 'error');
            console.error(error);
        });
    }

    function addToList(info) {
        const fileList = document.getElementById('fileList');
        if (!fileList) return;
        
        // Remove active de todos
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
        
        const div = document.createElement('div');
        div.className = 'file-item active';
        div.innerHTML = `
            <div class="file-item-title">${info.nome}</div>
            <div class="file-item-date">Gerado agora</div>
        `;
        div.onclick = () => {
             document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
             div.classList.add('active');
             loadMapInIframe(info.html, info.pdf, info.png, info.nome);
        };
        
        fileList.prepend(div);
    }
});
