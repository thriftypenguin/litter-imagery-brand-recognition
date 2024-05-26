document.addEventListener('DOMContentLoaded', () => {
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var activeTab = tabs[0];
    chrome.scripting.executeScript({
        target: {tabId: activeTab.id},
        files: ['content.js']
    }, () => {
        chrome.tabs.sendMessage(activeTab.id, {action: 'getHref'}, function(response) {
            console.log("Href received: ", response.href);
            document.getElementById('hrefData').setAttribute('data-href', response.href);
        });
    });
  });

  // Observe hrefOutput for changes
  const hrefOutputDiv = document.getElementById('hrefOutput');
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        chrome.tabs.query({active: true, currentWindow: true}, tabs => {
          chrome.tabs.sendMessage(tabs[0].id, {
            action: 'displayWiki',
            content: hrefOutputDiv.innerHTML
          });
        });
      }
    });
  });

  observer.observe(hrefOutputDiv, {childList: true, subtree: true});
});
