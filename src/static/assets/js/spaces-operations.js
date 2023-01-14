async function addManager(formEvent) {
    // url, managerEmail, csrfToken
    formEvent.preventDefault();
    const form = $(formEvent.target);
    const managerEmail = $('#inputManagerEmail').val();
    try {
        const response = await fetch(form.attr('action'), {
            method: 'POST', body: JSON.stringify({
                email: managerEmail
            }), mode: 'same-origin', headers: {
                'Content-Type': 'application/json', 'X-CSRFToken': csrfToken
            }
        });
        if (response.status === 200) {
            const data = await response.json();
            if (data?.changed) {
                const tbody = document.querySelector('#managers-table tbody');
                const lastRow = tbody.querySelector('tr:last-child');
                const lastIndex = parseInt(lastRow?.querySelector('th[scope=row]')?.innerText ?? '0');
                const newIndex = lastIndex + 1;
                const newRow = document.createElement('tr');
                newRow.setAttribute('id', 'managers-entry-' + newIndex);
                newRow.innerHTML = `
                <tr id="managers-entry-${newIndex}">
                    <th scope="row">${newIndex}</th>
                    <td>${data.user?.name}</td>
                    <td>${data.user?.email}</td>
                    <td>
                        <button class="btn btn-danger"
                                table-row-id="#managers-entry-${newIndex}"
                                email="${data.user?.email}"
                                onclick="removeManager(this)"
                        >Delete
                        </button>
                    </td>
                </tr>
                `;
                tbody.appendChild(newRow);
                alert(data?.message ?? 'Success');
            } else {
                alert('The user has already been added in this space as a manager.');
            }
            form.trigger('reset');
        } else {
            const data = await response.json();
            alert(`Error while adding manager, reason: ${data?.message ?? 'Unknown'}`);
        }
    } catch (e) {
        alert('Error while adding manager; Please reload the page.');
        console.error(e);
    }
}

async function addWriter(formEvent) {
    formEvent.preventDefault();
    const form = $(formEvent.target);
    const writerEmail = $('#inputWriterEmail').val();
    try {
        const response = await fetch(form.attr('action'), {
            method: 'POST', body: JSON.stringify({
                email: writerEmail
            }), mode: 'same-origin', headers: {
                'Content-Type': 'application/json', 'X-CSRFToken': csrfToken
            }
        });
        if (response.status === 200) {
            const data = await response.json();
            if (data?.changed) {
                const tbody = document.querySelector('#writers-table tbody');
                const lastRow = tbody.querySelector('tr:last-child');
                const lastIndex = parseInt(lastRow?.querySelector('th[scope=row]')?.innerText ?? '0');
                const newIndex = lastIndex + 1;
                const newRow = document.createElement('tr');
                newRow.setAttribute('id', 'writers-entry-' + newIndex);
                newRow.innerHTML = `
                <tr id="writers-entry-${newIndex}">
                    <th scope="row">${newIndex}</th>
                    <td>${data.user?.name}</td>
                    <td>${data.user?.email}</td>
                    <td>
                        <button class="btn btn-danger"
                                table-row-id="#writers-entry-${newIndex}"
                                email="${data.user?.email}"
                                onclick="removeWriter(this)"
                        >Delete
                        </button>
                    </td>
                </tr>
                `;
                tbody.appendChild(newRow);
                alert(data?.message ?? 'Success');
            } else {
                alert('The user has already been added in this space as a writer.');
            }
            form.trigger('reset');
        } else {
            const data = await response.json();
            alert(`Error while adding writer, reason: ${data?.message ?? 'Unknown'}; Please reload the page.`);
        }

    } catch (e) {
        alert('Error while adding writer; Please reload the page.');
        console.error(e);
    }
}

async function removeManager(entryButtonElement) {
    const managerEmail = $(entryButtonElement).attr('email');
    const tbody = document.querySelector('#managers-table tbody');
    const url = $(tbody).attr('action-url');
    const tableRowId = $(entryButtonElement).attr('table-row-id');

    const consent = window.confirm(`Do you want to remove this user ${managerEmail} from this space`);
    if (consent) {
        try {
            const response = await fetch(url, {
                method: 'DELETE', body: JSON.stringify({
                    email: managerEmail
                }), mode: 'same-origin', headers: {
                    'Content-Type': 'application/json', 'X-CSRFToken': csrfToken
                }
            });
            const data = await response.json();
            if (response.status === 200) {
                const node = $(tableRowId);
                node.remove();
                alert(data?.message ?? 'Success');
            } else {
                alert(`Removing manager failed, Please try again or reload. Reason: ${data?.message ?? 'Unknown'}; Please reload the page.`)
            }
        } catch (e) {
            alert(`Removing manager failed, Please try again or reload.`);
            console.error(e);
        }
    }
}

async function removeWriter(entryButtonElement) {
    const writerEmail = $(entryButtonElement).attr('email');
    const tbody = document.querySelector('#writers-table tbody');
    const url = $(tbody).attr('action-url');
    const tableRowId = $(entryButtonElement).attr('table-row-id');

    const consent = window.confirm(`Do you want to remove this user ${writerEmail} from this space`);
    if (consent) {
        try {
            const response = await fetch(url, {
                method: 'DELETE', body: JSON.stringify({
                    email: writerEmail
                }), mode: 'same-origin', headers: {
                    'Content-Type': 'application/json', 'X-CSRFToken': csrfToken
                }
            });
            const data = await response.json();
            if (response.status === 200) {
                const node = $(tableRowId);
                node.remove();
                alert(data?.message ?? 'Success');
            } else {
                alert(`Removing writer failed, Please try again or reload. Reason: ${data?.message ?? 'Unknown'}; Please reload the page.`)
            }
        } catch (e) {
            alert(`Removing writer failed, Please try again or reload.`);
            console.error(e);
        }
    }
}

$('input[type=file]').bind('change', function () {
    const supportedTypes = [
        'text/tab-separated-values',
        'application/vnd.ms-excel.sheet.macroenabled.12',
        'application/vnd.ms-excel',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/x-vnd.oasis.opendocument.spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        'application/vnd.ms-excel.template.macroenabled.12',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
    ];
    const messages = [];
    if (this.files[0].size > 24 * 1024 * 1024) {
        messages.push('The max file size is 24 MiB');
    }
    if (!supportedTypes.includes(this.files[0].type)) {
        messages.push('File type is not supported');
    }
    if (messages.length > 0) {
        alert(messages.join('\n'));
        $(this).val('');
    }
});

$("#uploadDocumentForm").bind('submit', function () {
    $('body').css('pointer-events', 'none');
    $(`
        <div class="alert alert-info">
            Please wait while the file is uploaded. The <strong>page has been disabled</strong> for safety during upload. <br>
            Please make sure your internet supports speeds of at least of 2mbps.
        </div>
    `).insertAfter("#space-files > div.alert:first-child").hide().show('slow');
});