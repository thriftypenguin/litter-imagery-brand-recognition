chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getHref') {
    const bylineInfo = document.querySelector('#bylineInfo'); // Modify the selector as needed
    if (bylineInfo) {
      sendResponse({ href: bylineInfo.textContent});
    } else {
      sendResponse({ href: 'Not found' });
    }
  } else if (request.action === 'displayWiki') {
    let wikiBox = document.getElementById('wikiBox');
    if (!wikiBox) {
      wikiBox = document.createElement('div');
      wikiBox.id = 'wikiBox';
      wikiBox.style.cssText = 'width: 300px; background-color: white; border: 1px solid black; padding: 10px; overflow-y: auto;';
      // Choose a container where the box should be added, for example at the end of an article
      const targetContainer = document.querySelector('#bylineInfo'); // Adjust this selector to your target container
      if (targetContainer) {
        targetContainer.appendChild(wikiBox);
      } else {
        // If the target container is not found, append to the body or handle as needed
        document.body.appendChild(wikiBox);
      }
    }
    wikiBox.innerHTML = request.content;
  }
});
