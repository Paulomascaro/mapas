<?php
session_start();
require_once 'config_path.php';
if (!isset($_SESSION['logged_in']) || $_SESSION['logged_in'] !== true) {
    echo json_encode(['success' => false, 'message' => 'Não autorizado.']);
    exit;
}

header('Content-Type: application/json');

if (!isset($_FILES['arquivo_xlsx']) || $_FILES['arquivo_xlsx']['error'] !== UPLOAD_ERR_OK) {
    echo json_encode(['success' => false, 'message' => 'Nenhum arquivo ou erro no envio.']);
    exit;
}

$file = $_FILES['arquivo_xlsx'];
$extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
if ($extension !== 'xlsx' && $extension !== 'xls') {
    echo json_encode(['success' => false, 'message' => 'Formato não permitido. Use .xlsx ou .xls.']);
    exit;
}

$entrada_dir = __DIR__ . '/dados_entrada';
if (!file_exists($entrada_dir)) {
    mkdir($entrada_dir, 0777, true);
}

// Limpar caracteres estranhos no nome
$nome_original = pathinfo($file['name'], PATHINFO_FILENAME);
$nome_seguro = preg_replace('/[^a-zA-Z0-9_\-]/', '_', $nome_original);
$novo_nome = $nome_seguro . '_' . time() . '.xlsx';
$caminho_final = $entrada_dir . '/' . $novo_nome;

if (move_uploaded_file($file['tmp_name'], $caminho_final)) {
    
    // Executa o Python e pede saída em JSON passando o arquivo individual
    // Como estamos no Windows do usuário, vamos tentar rodar com python. Se falhar, é erro de server config.
    $comando = PYTHON_PATH . " main.py " . escapeshellarg($caminho_final) . " 2>&1";
    $output = shell_exec($comando);
    
    // Decodifica JSON retornado pelo Python
    $resultado = null;
    if ($output) {
        $linhas = explode("\n", trim($output));
        foreach ($linhas as $linha) {
            $parsed = json_decode($linha, true);
            if ($parsed !== null && isset($parsed['status'])) {
                $resultado = $parsed;
                break;
            }
        }
    }

    if ($resultado && $resultado['status'] === 'success') {
        echo json_encode([
            'success' => true,
            'mapaInfo' => [
                'nome' => $resultado['nome_base'],
                'html' => 'saida/' . basename($resultado['html']),
                'pdf' => 'saida/' . basename($resultado['pdf']),
                'png' => 'saida/' . basename($resultado['png'])
            ]
        ]);
    } else {
        $erroStr = $resultado['message'] ?? 'O Python não gerou a saída esperada. Talvez não esteja no PATH ou ocorreu um erro de ambiente.';
        echo json_encode(['success' => false, 'message' => 'Erro interno na Plotagem: ' . $erroStr]);
    }

} else {
    echo json_encode(['success' => false, 'message' => 'Falha ao salvar o arquivo no servidor.']);
}
