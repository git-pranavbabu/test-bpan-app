export const checkPrinter = async () => {
  try {
    const res = await fetch('http://127.0.0.1:9999/spool', { method: 'HEAD' });
    return res.ok || res.status === 405;
  } catch {
    return false;
  }
};

export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const input = document.createElement('input');
    input.value = text;
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    return true;
  }
};
