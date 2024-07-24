document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('openLitterLog').addEventListener('click', function() {
        chrome.tabs.create({ url: 'https://openlittermaplitterlog.streamlit.app/' });
    });
});