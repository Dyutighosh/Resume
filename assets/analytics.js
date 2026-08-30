(() => {
  /* Replace the empty value with the site code selected in GoatCounter. */
  const siteCode = 'dyutighosh';
  const localHosts = new Set(['localhost', '127.0.0.1', '::1']);

  if (
    !/^[a-z0-9-]+$/i.test(siteCode)
    || window.location.protocol === 'file:'
    || localHosts.has(window.location.hostname)
    || navigator.doNotTrack === '1'
  ) {
    return;
  }

  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://gc.zgo.at/count.js';
  script.dataset.goatcounter = `https://${siteCode}.goatcounter.com/count`;
  document.head.appendChild(script);
})();
