document.addEventListener('DOMContentLoaded', async () => {
  const bylineInfo = document.querySelector('#bylineInfo');
  console.log('BylineInfo:', bylineInfo);  // Debug output

  if (bylineInfo) {
    let href = bylineInfo.textContent.split(' ');

    if (href[0] === 'Visit') {
      href = href.slice(2, -1);
    } else {
      href = href.slice(1);
    }

    href = href.join('_').toLowerCase();
    console.log('Request URL:', `https://en.wikipedia.org/api/rest_v1/page/summary/${href}`);  // Debug output

    try {
      const response = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${href}`);
      const data = await response.json();
      const extract = data.extract || "No extract available.";

      let wikiBox = document.getElementById('wikiBox');
      if (!wikiBox) {
        wikiBox = document.createElement('div');
        wikiBox.id = 'wikiBox';
        wikiBox.style.cssText = 'width: 300px; background-color: white; border: 1px solid black; padding: 10px; overflow-y: auto;';

        const targetContainer = document.querySelector('#bylineInfo'); // Adjust this selector to your target container
        if (targetContainer) {
          targetContainer.appendChild(wikiBox);
        } else {
          // If the target container is not found, append to the body or handle as needed
          document.body.appendChild(wikiBox);
        }
      }
      wikiBox.innerHTML = extract;
    } catch (error) {
      console.error('Fetch error:', error);
    }
  } else {
    console.log('Byline info not found');
  }
});
