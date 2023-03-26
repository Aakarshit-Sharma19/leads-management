$("#uploadDocumentForm").bind('submit', function () {
    $('body').css('pointer-events', 'none');
    $(`
        <div class="alert alert-info">
            Please wait while the file is uploaded. The <strong>page has been disabled</strong> for safety during upload. <br>
            Please make sure your internet supports speeds of at least of 2mbps.
        </div>
    `).insertAfter("#space-files > div.alert:first-child").hide().show('slow');
});
