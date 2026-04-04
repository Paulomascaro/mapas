<?php
session_start();
require_once 'config_path.php';
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'message' => 'Não autorizado.']);
    exit;
}

header('Content-Type: application/json');

$entrada_dir = __DIR__ . '/dados_entrada';
$saida_dir = __DIR__ . '/saida';

if (!file_exists($entrada_dir)) {
    mkdir($entrada_dir, 0777, true);
}
if (!file_exists($saida_dir)) {
    mkdir($saida_dir, 0777, true);
}

$arquivos = scandir($entrada_dir);
$resultados = [];
$processados = 0;
$erros = 0;

foreach ($arquivos as $arquivo) {
    $ext = strtolower(pathinfo($arquivo, PATHINFO_EXTENSION));
    if (($ext === 'xlsx' || $ext === 'xls') && strpos($arquivo, '~') !== 0) {
        $caminho_completo = $entrada_dir . '/' . $arquivo;
        
        $comando = PYTHON_PATH . " main.py " . escapeshellarg($caminho_completo) . " 2>&1";
        $output = shell_exec($comando);
        
        $json_res = null;
        if ($output) {
            $linhas = explode("\n", trim($output));
            foreach ($linhas as $linha) {
                $parsed = json_decode($linha, true);
                if ($parsed !== null && isset($parsed['status'])) {
                    $json_res = $parsed;
                    break;
                }
            }
        }

        if ($json_res && $json_res['status'] === 'success') {
            $processados++;
            $resultados[] = [
                'nome' => $json_res['nome_base'],
                'html' => 'saida/' . basename($json_res['html']),
                'pdf' => 'saida/' . basename($json_res['pdf']),
                'png' => 'saida/' . basename($json_res['png'])
            ];
        } else {
            $erros++;
        }
    }
}

echo json_encode([
    'success' => true,
    'message' => "Processamento concluído: $processados arquivos mapeados, $erros falhas.",
    'mapas' => $resultados
]);
