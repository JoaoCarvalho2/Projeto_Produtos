document.addEventListener('DOMContentLoaded', async () => {
    const API_URL = ''; // Vazio pois é servido pelo mesmo host
    let allData = [];
    let JIRA_BASE_URL = '';

    // Seleção de elementos do DOM
    const filterForm = document.getElementById('filterForm');
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    const resultsDiv = document.getElementById('results');
    const fornecedorSelect = document.getElementById('fornecedor');
    const tableBody = document.getElementById('resultsTableBody');
    const loadingSpinner = document.getElementById('loading');
    const countersSpan = document.getElementById('counters');
    const selectAllHeaderCheckbox = document.getElementById('selectAllHeader');
    const selectAllBtn = document.getElementById('selectAll');
    const deselectAllBtn = document.getElementById('deselectAll');
    const sendToJiraBtn = document.getElementById('sendToJira');
    const exportCsvBtn = document.getElementById('exportCsv');
    const modal = document.getElementById('confirmationModal');
    const modalItemCount = document.getElementById('modalItemCount');
    const confirmSendBtn = document.getElementById('confirmSend');
    const cancelSendBtn = document.getElementById('cancelSend');
    const closeModalBtn = document.querySelector('.close-button');
    const searchClientInput = document.getElementById('searchClient');
    const minValueInput = document.getElementById('minValue');
    const maxValueInput = document.getElementById('maxValue');
    const btnSelectValid = document.getElementById('btnSelectValid');


    async function fetchConfig() {
        try {
            const response = await fetch(`${API_URL}/api/config`);
            if (!response.ok) return;
            const config = await response.json();
            JIRA_BASE_URL = config.jira_base_url;
        } catch (error) { console.error('Erro config:', error); }
    }
    await fetchConfig();


    function toggleLoading(show) {
        loadingSpinner.style.display = show ? 'block' : 'none';
    }

    function showMessage(message, type = 'info') {
        const messageArea = document.getElementById('messageArea');
        messageArea.textContent = message;
        messageArea.className = `message-area ${type}`;
        setTimeout(() => messageArea.textContent = '', 5000);
    }
    
    function formatToBrazilianDate(dateString) {
        if (!dateString || typeof dateString !== 'string') return 'N/A';
        // Se já vier no formato YYYY-MM-DD
        if (dateString.includes('-')) {
            const [year, month, day] = dateString.split('-');
            return `${day}/${month}/${year}`;
        }
        // Se vier no formato MM/DD/YYYY (comum no FileMaker)
        const parts = dateString.split('/');
        if (parts.length === 3) {
            const [month, day, year] = parts;
            return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`;
        }
        return dateString;
    }

    /**
     * Função auxiliar para encontrar valor em objeto ignorando prefixos (ex: lead::nome ou nome)
     */
    function findValue(obj, partialKey) {
        if (!obj) return null;
        
        // 1. Tenta a chave exata
        if (obj[partialKey] !== undefined) return obj[partialKey];
        
        // 2. Tenta encontrar chave que termine com o nome (ex: "lead::empresa" para busca "empresa")
        const keyFound = Object.keys(obj).find(k => k.endsWith(`::${partialKey}`) || k === partialKey);
        return keyFound ? obj[keyFound] : null;
    }

    function renderTable(data) {
        allData = data;
        // LOG DE DEBUG: Abra o F12 no navegador -> Console para ver o que chegou
        console.log("Dados recebidos do Backend:", data);

        tableBody.innerHTML = '';
        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="9" style="text-align:center;">Nenhum resultado encontrado.</td></tr>';
            resultsDiv.style.display = 'block';
            updateCounters();
            return;
        }

        data.forEach((item, index) => {
            const row = document.createElement('tr');
            row.dataset.index = index;
            
            // Usando a função inteligente para buscar os campos
            const empresa = findValue(item.lead_fields, 'empresa') || 'N/A';
            const nome = findValue(item.lead_fields, 'nome') || 'N/A';
            
            // Tenta 'data_criacao' ou 'lead::data_criacao'
            let rawDate = findValue(item.lead_fields, 'data_criacao');
            const dataCriacao = formatToBrazilianDate(rawDate);
            
            const fabricante = findValue(item.lead_fields, 'fabricante') || 'N/A';
            
            // Busca valor na proposta (pode ser valor_total_reais ou produto_proposta::valor_total_reais)
            const valorRaw = findValue(item.proposta_fields, 'valor_total_reais');
            const valor = valorRaw ? parseFloat(valorRaw).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'}) : 'R$ 0,00';
            
            const status = findValue(item.lead_fields, 'status') || 'Pendente';

            row.innerHTML = `
                <td><input type="checkbox" class="row-checkbox"></td>
                <td>${item.lead_id || 'N/A'}</td>
                <td>${item.proposta_id || 'N/A'}</td>
                <td>${empresa}</td>
                <td>${nome}</td>
                <td>${dataCriacao}</td>
                <td>${fabricante}</td>
                <td>${valor}</td>
                <td class="status-cell">
                    <span class="status-message">${status}</span>
                </td>
            `;
            tableBody.appendChild(row);
        });
        resultsDiv.style.display = 'block';
        updateCounters();
    }

    // ... (O restante das funções permanece igual: updateCounters, handleSelection, exportToCsv, etc.)
    
    function updateCounters() {
        const total = allData.length;
        const selected = document.querySelectorAll('.row-checkbox:checked').length;
        countersSpan.textContent = `Encontrados: ${total} | Selecionados: ${selected}`;
        sendToJiraBtn.disabled = selected === 0;
    }
    
    function handleSelection() {
        const checkboxes = document.querySelectorAll('.row-checkbox');
        const allChecked = checkboxes.length > 0 && Array.from(checkboxes).every(cb => cb.checked);
        selectAllHeaderCheckbox.checked = allChecked;
        updateCounters();
    }

    function exportToCsv() {
        const selectedRows = getSelectedItems();
        if (selectedRows.length === 0) {
            showMessage('Selecione ao menos um item para exportar.', 'info');
            return;
        }
        const headers = ['Lead ID', 'Proposta ID', 'Empresa', 'Contato', 'Data Criacao', 'Fabricante', 'Valor Total'];
        const csvContent = [
            headers.join(','),
            ...selectedRows.map(item => [
                item.lead_id || '',
                item.proposta_id || '',
                `"${(findValue(item.lead_fields, 'empresa') || '').replace(/"/g, '""')}"`,
                `"${(findValue(item.lead_fields, 'nome') || '').replace(/"/g, '""')}"`,
                formatToBrazilianDate(findValue(item.lead_fields, 'data_criacao')),
                findValue(item.lead_fields, 'fabricante') || '',
                findValue(item.proposta_fields, 'valor_total_reais') || ''
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'export_leads_atlassian.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    function getSelectedItems() {
        const selectedItems = [];
        document.querySelectorAll('.row-checkbox:checked').forEach(checkbox => {
            const rowIndex = checkbox.closest('tr').dataset.index;
            if (rowIndex !== undefined) {
                selectedItems.push(allData[parseInt(rowIndex)]);
            }
        });
        return selectedItems;
    }

    filterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const date_from = dateFromInput.value;
        const date_to = dateToInput.value;
        const fornecedor = fornecedorSelect.value;

        if (!date_from || !date_to) {
            showMessage('Por favor, preencha as datas.', 'error');
            return;
        }

        toggleLoading(true);
        resultsDiv.style.display = 'none';

        try {
            const params = new URLSearchParams({ date_from, date_to, fornecedor });
            const response = await fetch(`${API_URL}/api/leads?${params.toString()}`);
            if (!response.ok) {
                 const errorData = await response.json().catch(() => ({}));
                 throw new Error(errorData.detail || 'Erro ao buscar dados.');
            }
            const data = await response.json();
            renderTable(data);
        } catch (error) {
            console.error(error);
            showMessage(error.message, 'error');
            renderTable([]);
        } finally {
            toggleLoading(false);
        }
    });

    tableBody.addEventListener('change', (e) => {
        if (e.target.classList.contains('row-checkbox')) { handleSelection(); }
    });
    selectAllHeaderCheckbox.addEventListener('change', () => {
        const isChecked = selectAllHeaderCheckbox.checked;
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = isChecked);
        handleSelection();
    });
    selectAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = true);
        handleSelection();
    });
    deselectAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = false);
        handleSelection();
    });
    exportCsvBtn.addEventListener('click', exportToCsv);

    sendToJiraBtn.addEventListener('click', () => {
        const selectedCount = getSelectedItems().length;
        if (selectedCount > 0) {
            modalItemCount.textContent = selectedCount;
            modal.style.display = 'flex';
        }
    });
    closeModalBtn.addEventListener('click', () => modal.style.display = 'none');
    cancelSendBtn.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (e) => { if (e.target === modal) { modal.style.display = 'none'; } });

    confirmSendBtn.addEventListener('click', async () => {
        modal.style.display = 'none';
        const itemsToSend = getSelectedItems();
        if (itemsToSend.length === 0) return;

        const fornecedor = fornecedorSelect.value;

        toggleLoading(true);
        sendToJiraBtn.disabled = true;
        try {
            const response = await fetch(`${API_URL}/api/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    items: itemsToSend,
                    fornecedor: fornecedor
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({})); 
                throw new Error(errorData.detail || `Erro HTTP: ${response.status}`);
            }

            const resultData = await response.json();
            
            resultData.results.forEach(res => {
                const row = Array.from(tableBody.querySelectorAll('tr')).find(r => {
                    const index = r.dataset.index;
                    return allData[index] && allData[index].lead_id === res.lead_id;
                });
                if (row) {
                    const statusCell = row.querySelector('.status-cell');
                    if (res.status === 'ok') {
                        row.classList.add('status-ok');
                        const issueLink = JIRA_BASE_URL ? `<a href="${JIRA_BASE_URL}/browse/${res.issue_key}" target="_blank"><b>${res.issue_key}</b></a>` : `<b>${res.issue_key}</b>`;
                        statusCell.innerHTML = `<span class="status-message success">Sucesso! (${res.action})<br>${issueLink}</span>`;
                    } else {
                        row.classList.add('status-error');
                        statusCell.innerHTML = `<span class="status-message error" title="${res.message || 'Falha no envio.'}">Erro</span>`;
                    }
                }
            });
            showMessage('Envio concluído.', 'success');
        } catch (error) {
            console.error('Erro envio Jira:', error);
            showMessage(error.message, 'error');
        } finally {
            toggleLoading(false);
            sendToJiraBtn.disabled = false;
        }
    });
});
function parseMoney(valueStr) {
        if (!valueStr || typeof valueStr !== 'string') return 0;
        // Remove R$, espaços e pontos de milhar, troca vírgula por ponto
        const cleanStr = valueStr.replace(/[R$\s.]/g, '').replace(',', '.');
        return parseFloat(cleanStr) || 0;
    }

    // --- LÓGICA DE FILTRAGEM ---
    function applyLocalFilters() {
        const searchTerm = searchClientInput.value.toLowerCase();
        const minVal = parseFloat(minValueInput.value) || 0;
        const maxVal = parseFloat(maxValueInput.value) || Infinity;

        const rows = tableBody.querySelectorAll('tr');

        rows.forEach(row => {
            // Pega os dados das colunas (Cliente é índice 3, Valor é índice 7)
            // Ajuste os índices conforme sua tabela: 
            // 0:Chk, 1:ID Lead, 2:ID Prop, 3:Empresa, 4:Contato, 5:Data, 6:Fabricante, 7:Valor
            
            const clientName = row.children[3].textContent.toLowerCase();
            const contactName = row.children[4].textContent.toLowerCase();
            const leadId = row.children[1].textContent.toLowerCase();
            const valStr = row.children[7].textContent;
            const valNum = parseMoney(valStr);

            // Verifica condições
            const matchesSearch = clientName.includes(searchTerm) || 
                                  contactName.includes(searchTerm) || 
                                  leadId.includes(searchTerm);
            
            const matchesValue = valNum >= minVal && valNum <= maxVal;

            if (matchesSearch && matchesValue) {
                row.classList.remove('hidden-row');
            } else {
                row.classList.add('hidden-row');
                // Opcional: Desmarcar itens que foram escondidos
                // row.querySelector('.row-checkbox').checked = false; 
            }
        });
        
        // Atualiza contadores com base apenas nos visíveis
        updateCounters(); 
    }

    // --- SELECIONAR APENAS COM VALOR ---
    btnSelectValid.addEventListener('click', () => {
        const rows = tableBody.querySelectorAll('tr:not(.hidden-row)'); // Só atua nos visíveis
        let count = 0;
        
        rows.forEach(row => {
            const valStr = row.children[7].textContent;
            const valNum = parseMoney(valStr);
            const checkbox = row.querySelector('.row-checkbox');

            if (valNum > 0) {
                checkbox.checked = true;
                count++;
            } else {
                checkbox.checked = false;
            }
        });
        handleSelection();
        showMessage(`${count} itens com valor selecionados.`, 'success');
    });

    // --- EVENT LISTENERS DOS FILTROS ---
    searchClientInput.addEventListener('keyup', applyLocalFilters);
    minValueInput.addEventListener('input', applyLocalFilters); // 'input' pega setas do number
    maxValueInput.addEventListener('input', applyLocalFilters);