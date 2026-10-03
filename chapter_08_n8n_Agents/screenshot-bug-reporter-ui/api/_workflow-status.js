const crypto = require('node:crypto');

const TICKET_KEY_PATTERN = /\bKAN-\d+\b/i;
const ANY_JIRA_KEY_PATTERN = /\b[A-Z][A-Z0-9]+-\d+\b/;
const TOKEN_MAX_AGE_MS = 25 * 60 * 1000;

function getTokenSecret() {
  return process.env.STATUS_TOKEN_SECRET || process.env.N8N_BUG_REPORTER_URL || 'local-dev-secret';
}

function getKey() {
  return crypto.createHash('sha256').update(getTokenSecret()).digest();
}

function encode(buffer) {
  return buffer.toString('base64url');
}

function decode(value) {
  return Buffer.from(value, 'base64url');
}

function createStatusToken(formWaitingUrl) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', getKey(), iv);
  const payload = Buffer.from(
    JSON.stringify({
      formWaitingUrl,
      createdAt: Date.now(),
    }),
  );
  const encrypted = Buffer.concat([cipher.update(payload), cipher.final()]);

  return [encode(iv), encode(cipher.getAuthTag()), encode(encrypted)].join('.');
}

function readStatusToken(token) {
  const [ivValue, tagValue, encryptedValue] = String(token || '').split('.');
  if (!ivValue || !tagValue || !encryptedValue) {
    throw new Error('Invalid status token.');
  }

  const decipher = crypto.createDecipheriv('aes-256-gcm', getKey(), decode(ivValue));
  decipher.setAuthTag(decode(tagValue));
  const decrypted = Buffer.concat([decipher.update(decode(encryptedValue)), decipher.final()]);
  const payload = JSON.parse(decrypted.toString('utf8'));

  if (!payload.formWaitingUrl || Date.now() - payload.createdAt > TOKEN_MAX_AGE_MS) {
    throw new Error('Status token expired. Please submit the bug again.');
  }

  return payload;
}

function decodeHtmlEntities(value) {
  return String(value || '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function extractTicketDetails(responseText) {
  const text = decodeHtmlEntities(responseText);
  const ticketKey = text.match(TICKET_KEY_PATTERN)?.[0]?.toUpperCase()
    || text.match(ANY_JIRA_KEY_PATTERN)?.[0]
    || '';
  const ticketUrl = ticketKey
    ? text.match(new RegExp(`https?://[^\\s"'<>]+/browse/${ticketKey}`, 'i'))?.[0] || ''
    : '';

  return {
    ticketKey,
    ticketUrl,
  };
}

function getStatusUrl(formWaitingUrl) {
  const url = new URL(formWaitingUrl);
  url.pathname = `${url.pathname}/n8n-execution-status`;
  return url.toString();
}

async function getWorkflowStatus(formWaitingUrl) {
  const statusResponse = await fetch(getStatusUrl(formWaitingUrl), {
    headers: {
      accept: 'text/plain',
      'user-agent': 'screenshot-bug-reporter-ui/1.0',
    },
  });
  const workflowStatus = (await statusResponse.text()).trim();

  if (workflowStatus !== 'success' && workflowStatus !== 'form-waiting') {
    return {
      pending: workflowStatus === 'running' || workflowStatus === 'waiting',
      workflowStatus,
      ticketKey: '',
      ticketUrl: '',
    };
  }

  const completionResponse = await fetch(formWaitingUrl, {
    headers: {
      accept: 'text/html,application/json,text/plain',
      'user-agent': 'screenshot-bug-reporter-ui/1.0',
    },
    redirect: 'follow',
  });
  const completionText = await completionResponse.text();

  return {
    pending: false,
    workflowStatus,
    ...extractTicketDetails(completionText),
  };
}

module.exports = {
  createStatusToken,
  extractTicketDetails,
  getWorkflowStatus,
  readStatusToken,
};
