const { getWorkflowStatus, readStatusToken } = require('./_workflow-status');

module.exports = async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const requestUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const token = requestUrl.searchParams.get('token');
    const { formWaitingUrl } = readStatusToken(token);
    const status = await getWorkflowStatus(formWaitingUrl);

    if (status.pending) {
      return res.status(202).json({
        ok: true,
        pending: true,
        message: 'Bug creation is still processing.',
        workflowStatus: status.workflowStatus,
      });
    }

    if (status.workflowStatus !== 'success' && status.workflowStatus !== 'form-waiting') {
      return res.status(502).json({
        error: 'The workflow failed before creating a Jira ticket.',
        workflowStatus: status.workflowStatus,
      });
    }

    if (!status.ticketKey) {
      return res.status(502).json({
        error: 'The workflow finished, but no Jira ticket key was returned.',
        workflowStatus: status.workflowStatus,
      });
    }

    return res.status(200).json({
      ok: true,
      pending: false,
      message: `Bug ${status.ticketKey} created successfully.`,
      ticketKey: status.ticketKey,
      ticketUrl: status.ticketUrl,
    });
  } catch (error) {
    console.error('Bug report status error', error);
    return res.status(400).json({
      error: error.message || 'Could not check bug report status.',
    });
  }
};
