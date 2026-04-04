<?php
session_start();
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header("Location: index.php");
    exit;
}

// Ler mapas já existentes
$maps = [];
$saida_dir = __DIR__ . '/saida';
if (file_exists($saida_dir)) {
    $files = scandir($saida_dir);
    foreach ($files as $file) {
        if (pathinfo($file, PATHINFO_EXTENSION) === 'html') {
            $base = pathinfo($file, PATHINFO_FILENAME);
            $maps[] = [
                'nome' => $base,
                'html' => 'saida/' . $file,
                'pdf' => 'saida/' . $base . '.pdf',
                'png' => 'saida/' . $base . '.png'
            ];
        }
    }
}
// Ordenar o array (opcional, pelos mais recentes... scandir não os ordena por padrão)
$maps = array_reverse($maps);
?>
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel - Mapeador Geo</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <nav class="navbar glass-panel" style="margin: 2rem auto; width: calc(100% - 4rem); max-width: 1200px; border-radius: 12px;">
        <a href="dashboard.php" class="logo">Mapeador Geo</a>
        <a href="logout.php" class="logout">Sair do Sistema</a>
    </nav>

    <div class="container" style="padding-top: 0;">
        <div id="alertBox" class="alert d-none"></div>

        <!-- Área de Upload -->
        <div class="glass-panel upload-area" id="uploadArea">
            <div class="upload-icon">📄</div>
            <div class="upload-text">
                <h3>Arraste e solte seu arquivo .xlsx ou .xls aqui</h3>
                <p>ou clique para selecionar na sua máquina</p>
                <input type="file" id="fileInput" accept=".xlsx, .xls" class="d-none">
            </div>
        </div>

        <!-- Resultados -->
        <div class="glass-panel results-grid">
            <!-- Sidebar: Lista -->
            <div class="file-list-container">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--border-color);">
                    <h3 style="padding: 0; border: none; font-size: 1rem;">Meus Mapas</h3>
                    <button class="btn btn-secondary btn-sm" id="btnSyncFolder" title="Processar arquivos que já estão na pasta de entrada">🔄 Ler Pasta</button>
                </div>
                <div class="file-list" id="fileList">
                    <?php if (empty($maps)): ?>
                        <div style="text-align: center; color: var(--text-secondary); margin-top: 2rem; font-size: 0.9rem;">
                            Nenhum mapa plotado ainda.
                        </div>
                    <?php else: ?>
                        <?php foreach ($maps as $idx => $m): ?>
                            <div class="file-item <?= $idx === 0 ? 'active' : '' ?>" onclick="document.querySelectorAll('.file-item').forEach(el=>el.classList.remove('active')); this.classList.add('active'); loadMapInIframe('<?= $m['html'] ?>', '<?= $m['pdf'] ?>', '<?= $m['png'] ?>', '<?= addslashes($m['nome']) ?>')">
                                <div class="file-item-title"><?= htmlspecialchars($m['nome']) ?></div>
                                <div class="file-item-date">Salvo em disco</div>
                            </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </div>
            </div>

            <!-- Main: Visualizador -->
            <div class="map-viewer">
                <div class="map-header">
                    <h3 id="mapTitle"><?= !empty($maps) ? htmlspecialchars($maps[0]['nome']) : 'Nenhum item selecionado' ?></h3>
                    <div class="map-actions <?= empty($maps) ? 'd-none' : '' ?>" id="mapActions">
                        <button class="btn btn-secondary btn-sm" id="btnDownloadPng" <?= !empty($maps) ? "onclick=\"window.open('{$maps[0]['png']}', '_blank')\"" : "" ?>>⬇ PNG (Alta Res.)</button>
                        <button class="btn btn-sm" id="btnDownloadPdf" <?= !empty($maps) ? "onclick=\"window.open('{$maps[0]['pdf']}', '_blank')\"" : "" ?>>⬇ Download PDF</button>
                    </div>
                </div>
                
                <div class="iframe-container <?= empty($maps) ? 'd-none' : '' ?>" id="mapIframeWrapper">
                    <iframe id="mapIframe" src="<?= !empty($maps) ? $maps[0]['html'] : '' ?>"></iframe>
                </div>
                
                <div class="empty-state <?= !empty($maps) ? 'd-none' : '' ?>" id="emptyState">
                    Nenhum mapa importado para ser visualizado.
                </div>
            </div>
        </div>
    </div>

    <!-- Loader Assíncrono -->
    <div class="loader-overlay" id="loader">
        <div class="spinner"></div>
        <p id="loaderText" style="font-weight: 500; font-size: 1.1rem;">Processando...</p>
    </div>

    <script src="assets/script.js"></script>
    <script>
        // Função auxiliar exposta para o click inline dos items pre-renderizados via PHP
        function loadMapInIframe(html, pdf, png, name) {
            document.getElementById('emptyState').classList.add('d-none');
            document.getElementById('mapIframeWrapper').classList.remove('d-none');
            document.getElementById('mapActions').classList.remove('d-none');
            
            document.getElementById('mapIframe').src = html;
            document.getElementById('mapTitle').textContent = name;
            
            document.getElementById('btnDownloadPdf').onclick = () => window.open(pdf, '_blank');
            document.getElementById('btnDownloadPng').onclick = () => window.open(png, '_blank');
        }
    </script>
</body>
</html>
