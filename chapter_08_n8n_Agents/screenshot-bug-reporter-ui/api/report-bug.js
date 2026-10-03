const { createStatusToken, extractTicketDetails } = require('./_workflow-status');

const MAX_UPLOAD_BYTES = 4.25 * 1024 * 1024;

async function readBody(req) {
  const chunks = [];
  let size = 0;

  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_UPLOAD_BYTES) {
      const error = new Error(
        'The optimized upload is still too large. Crop the screenshot to the affected area and try again.',
      );
      error.statusCode = 413;
      throw error;
    }
    chunks.push(Buffer.from(chunk));
  }

  return Buffer.concat(chunks);
}

function parseInitialResponse(responseText) {
  try {
    const parsed = JSON.parse(responseText);
    if (parsed.formWaitingUrl) {
      return {
        pending: true,
        statusToken: createStatusToken(parsed.formWaitingUrl),
      };
    }
  } catch {
    // Some completion responses are HTML, so fall through to ticket extraction.
  }

  return {
    pending: false,
    ...extractTicketDetails(responseText),
  };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const targetUrl = process.env.N8N_BUG_REPORTER_URL;
  if (!targetUrl) {
    return res.status(500).json({ error: 'Submission endpoint is not configured.' });
  }

  const contentType = req.headers['content-type'];
  if (!contentType || !contentType.includes('multipart/form-data')) {
    return res.status(400).json({ error: 'Expected a multipart form submission.' });
  }

  try {
    const body = await readBody(req);
    const upstreamResponse = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'content-type': contentType,
        'user-agent': 'screenshot-bug-reporter-ui/1.0',
      },
      body,
      redirect: 'follow',
    });
    const responseText = await upstreamResponse.text();

    if (!upstreamResponse.ok) {
      console.error('Bug report submission failed', {
        status: upstreamResponse.status,
        response: responseText.slice(0, 500),
      });
      return res.status(502).json({
        error: 'The report could not be submitted. Please try again.',
      });
    }

    const parsed = parseInitialResponse(responseText);
    if (parsed.pending) {
      return res.status(202).json({
        ok: true,
        pending: true,
        statusToken: parsed.statusToken,
        message: 'Bug creation is processing.',
      });
    }

    if (!parsed.ticketKey) {
      return res.status(502).json({
        error: 'The workflow finished, but no Jira ticket key was returned.',
      });
    }

    return res.status(200).json({
      ok: true,
      pending: false,
      message: `Bug ${parsed.ticketKey} created successfully.`,
      ticketKey: parsed.ticketKey,
      ticketUrl: parsed.ticketUrl,
    });
  } catch (error) {
    const statusCode = error.statusCode || 500;
    console.error('Bug report proxy error', error);
    return res.status(statusCode).json({
      error: error.message || 'Something went wrong while submitting the report.',
    });
  }
};

module.exports.config = {
  api: {
    bodyParser: false,
  },
};
