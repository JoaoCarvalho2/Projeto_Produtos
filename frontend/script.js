document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:8000';
    let allData = [];

    const filterForm = document.getElementById('filterForm');
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    const resultsDiv = document.getElementById('results');
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

    function toggleLoading(show) {
        loadingSpinner.style.display = show ? 'block' : 'none';
    }

    function showMessage(message, type = 'info') {
        const messageArea = document.getElementById('messageArea');
        messageArea.textContent = message;
        messageArea.className = `message-area ${type}`;
        setTimeout(() => messageArea.textContent = '', 5000);
    }

    function renderTable(data) {
        allData = data;
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
            
            row.innerHTML = `
                <td><input type="checkbox" class="row-checkbox"></td>
                <td>${item.lead_id || 'N/A'}</td>
                <td>${item.proposta_id || 'Sem Proposta'}</td>
                <td>${item.lead_fields.empresa || 'N/A'}</td>
                <td>${item.lead_fields.nome || 'N/A'}</td>
                <td>${item.lead_fields.data_criacao || 'N/A'}</td>
                <td>${item.lead_fields.fabricante || 'N/A'}</td>
                <td>${item.proposta_fields['produto_proposta::valor_total_sum'] || 'N/A'}</td>
                <td class="status-cell">
                    <span class="status-message">Pendente</span>
                </td>
            `;
            tableBody.appendChild(row);
        });
        resultsDiv.style.display = 'block';
        updateCounters();
    }
    
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
                `"${(item.lead_fields.empresa || '').replace(/"/g, '""')}"`,
                `"${(item.lead_fields.nome || '').replace(/"/g, '""')}"`,
                item.lead_fields.data_criacao || '',
                // ========================================================
                // CORREÇÃO: Usar 'fabricante' em vez de 'lead::fabricante'
                // ========================================================
                item.lead_fields.fabricante || '',
                item.proposta_fields['produto_proposta::valor_total_sum'] || ''
            ].join(','))
        ].join('\n');
        
        const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'export_leads.csv');
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

        if (!date_from || !date_to) {
            showMessage('Por favor, preencha as datas de início e fim.', 'error');
            return;
        }

        toggleLoading(true);
        resultsDiv.style.display = 'none';

        try {
            const params = new URLSearchParams({ date_from, date_to });
            const response = await fetch(`${API_URL}/api/leads?${params.toString()}`);
            if (!response.ok) {
                 const errorData = await response.json();
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

        toggleLoading(true);
        sendToJiraBtn.disabled = true;
        try {
            const response = await fetch(`${API_URL}/api/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: itemsToSend }),
            });
            const resultData = await response.json();
            
            resultData.results.forEach(res => {
                const row = Array.from(tableBody.querySelectorAll('tr')).find(r => {
                    const index = r.dataset.index;
                    return allData[index] && allData[index].lead_id === res.lead_id && allData[index].proposta_id === res.proposta_id;
                });
                if (row) {
                    const statusCell = row.querySelector('.status-cell');
                    if (res.status === 'ok') {
                        row.classList.add('status-ok');
                        statusCell.innerHTML = `<span class="status-message success">Sucesso! (${res.action})<br><b>${res.issue_key}</b></span>`;
                    } else {
                        row.classList.add('status-error');
                        statusCell.innerHTML = `<span class="status-message error">Erro: ${res.message || 'Falha no envio.'}</span>`;
                    }
                }
            });
            showMessage('Processo de envio concluído. Verifique o status na tabela.', 'success');
        } catch (error) {
            console.error('Erro ao enviar para o Jira:', error);
            showMessage('Ocorreu um erro de comunicação com o servidor.', 'error');
        } finally {
            toggleLoading(false);
            sendToJiraBtn.disabled = false;
        }
    });
});