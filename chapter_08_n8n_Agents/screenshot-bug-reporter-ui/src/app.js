const form = document.querySelector('#bug-report-form');
const fileInput = document.querySelector('#screenshot');
const dropZone = document.querySelector('#drop-zone');
const preview = document.querySelector('#preview');
const previewImage = document.querySelector('#preview-image');
const statusMessage = document.querySelector('#status');
const submitButton = document.querySelector('#submit-button');
const resultPanel = document.querySelector('#result-panel');
const ticketKey = document.querySelector('#ticket-key');
const ticketUrl = document.querySelector('#ticket-url');
const openTicketLink = document.querySelector('#open-ticket-link');
const copyUrlButton = document.querySelector('#copy-url-button');
const logAnotherButton = document.querySelector('#log-another-button');

const MAX_SOURCE_BYTES = 18 * 1024 * 1024;
const MAX_FORWARD_BYTES = 3.8 * 1024 * 1024;
const MAX_IMAGE_SIDE = 2400;
const STATUS_POLL_MS = 4000;
const STATUS_TIMEOUT_MS = 20 * 60 * 1000;
const ACCEPTED_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp']);

function setStatus(message, type = 'neutral') {
  statusMessage.textContent = message;
  statusMessage.classList.toggle('is-success', type === 'success');
  statusMessage.classList.toggle('is-error', type === 'error');
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.classList.toggle('is-loading', isLoading);
  submitButton.querySelector('.button-label').textContent = isLoading
    ? 'Creating'
    : 'Create Bug';
}

function validateFile(file) {
  if (!file) return 'Please choose a screenshot before submitting.';
  if (!ACCEPTED_TYPES.has(file.type)) return 'Use a PNG, JPG or WebP screenshot.';
  if (file.size > MAX_SOURCE_BYTES) return 'Keep the screenshot under 18 MB.';
  return '';
}

function canvasToBlob(canvas, type, quality) {
  return new Promise((resolve) => {
    canvas.toBlob(resolve, type, quality);
  });
}

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    const objectUrl = URL.createObjectURL(file);
    image.onload = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      reject(new Error('Could not read the screenshot. Please try another image.'));
    };
    image.src = objectUrl;
  });
}

async function optimizeScreenshot(file) {
  if (file.size <= MAX_FORWARD_BYTES) return file;

  const image = await loadImage(file);
  const width = image.naturalWidth;
  const height = image.naturalHeight;
  let scale = Math.min(1, MAX_IMAGE_SIDE / Math.max(width, height));
  let quality = 0.9;

  for (let attempt = 0; attempt < 8; attempt += 1) {
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(width * scale));
    canvas.height = Math.max(1, Math.round(height * scale));

    const context = canvas.getContext('2d', { alpha: false });
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, canvas.width, canvas.height);

    const blob = await canvasToBlob(canvas, 'image/jpeg', quality);
    if (blob && blob.size <= MAX_FORWARD_BYTES) {
      const originalName = file.name.replace(/\.[^.]+$/, '');
      return new File([blob], `${originalName || 'screenshot'}-optimized.jpg`, {
        type: 'image/jpeg',
      });
    }

    if (quality > 0.68) {
      quality -= 0.08;
    } else {
      scale *= 0.82;
    }
  }

  throw new Error('This screenshot is too large to submit. Crop it to the affected area and try again.');
}

function showPreview(file) {
  const validationError = validateFile(file);
  if (validationError) {
    preview.classList.add('is-empty');
    previewImage.removeAttribute('src');
    setStatus(validationError, 'error');
    return;
  }

  const reader = new FileReader();
  reader.addEventListener('load', () => {
    previewImage.src = reader.result;
    preview.classList.remove('is-empty');
  });
  reader.readAsDataURL(file);
  setStatus(`${file.name} selected.`, 'neutral');
}

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

async function pollTicketStatus(statusToken) {
  const deadline = Date.now() + STATUS_TIMEOUT_MS;
  let pollCount = 0;

  while (Date.now() < deadline) {
    await wait(STATUS_POLL_MS);
    pollCount += 1;
    setStatus(`Still working. Waiting for the ticket... (${pollCount})`, 'neutral');

    const response = await fetch(`/api/report-status?token=${encodeURIComponent(statusToken)}`);
    const payload = await response.json().catch(() => ({}));

    if (response.status === 202 || payload.pending) continue;
    if (!response.ok) {
      throw new Error(payload.error || 'The workflow failed before creating a Jira ticket.');
    }
    return payload;
  }

  throw new Error('The workflow is still running. Please check the automation execution.');
}

function showResult(payload) {
  ticketKey.textContent = payload.ticketKey;
  ticketUrl.value = payload.ticketUrl || '';
  openTicketLink.href = payload.ticketUrl || '#';
  openTicketLink.toggleAttribute('aria-disabled', !payload.ticketUrl);
  form.hidden = true;
  resultPanel.hidden = false;
}

function resetForm() {
  form.reset();
  preview.classList.add('is-empty');
  previewImage.removeAttribute('src');
  resultPanel.hidden = true;
  form.hidden = false;
  setStatus('Ready for evidence.', 'neutral');
}

fileInput.addEventListener('change', () => {
  showPreview(fileInput.files[0]);
});

for (const eventName of ['dragenter', 'dragover']) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add('is-dragging');
  });
}

for (const eventName of ['dragleave', 'drop']) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove('is-dragging');
  });
}

dropZone.addEventListener('drop', (event) => {
  const file = event.dataTransfer.files[0];
  if (!file) return;

  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  fileInput.files = dataTransfer.files;
  showPreview(file);
});

copyUrlButton.addEventListener('click', async () => {
  if (!ticketUrl.value) return;
  await navigator.clipboard.writeText(ticketUrl.value);
  copyUrlButton.textContent = 'Copied';
  setTimeout(() => {
    copyUrlButton.textContent = 'Copy URL';
  }, 1800);
});

logAnotherButton.addEventListener('click', resetForm);

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const file = fileInput.files[0];
  const validationError = validateFile(file);
  if (validationError) {
    setStatus(validationError, 'error');
    return;
  }

  setLoading(true);

  try {
    setStatus('Optimizing screenshot...', 'neutral');
    const formData = new FormData(form);
    const optimizedFile = await optimizeScreenshot(file);
    formData.set('field-0', optimizedFile, optimizedFile.name);

    setStatus('Submitting evidence...', 'neutral');
    const response = await fetch('/api/report-bug', {
      method: 'POST',
      body: formData,
    });
    const payload = await response.json().catch(() => ({}));

    if (!response.ok && response.status !== 202) {
      throw new Error(payload.error || 'The report could not be submitted.');
    }

    const finalPayload = payload.pending ? await pollTicketStatus(payload.statusToken) : payload;
    if (!finalPayload.ticketKey) {
      throw new Error('The workflow finished, but no ticket number was returned.');
    }

    setStatus(`Bug ${finalPayload.ticketKey} created.`, 'success');
    showResult(finalPayload);
  } catch (error) {
    setStatus(error.message || 'Something went wrong. Please try again.', 'error');
  } finally {
    setLoading(false);
  }
});
