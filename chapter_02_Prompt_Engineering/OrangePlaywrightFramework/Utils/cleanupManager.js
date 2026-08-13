/**
 * CleanupManager — automatically deletes old test runs, keeping only the last 5
 * across Logs/, ScreenshotAttachment/, and Reports/ folders.
 *
 * - Runs after every test suite completes (called from reportGenerator.js)
 * - Identifies test runs by timestamp: YYYYMMDD_HHMMSS
 * - Keeps 5 most recent, deletes everything older
 * - Prevents disk space bloat from repeated test runs
 */
const fs = require('fs');
const path = require('path');

const config = require('../config/config');

const MAX_RUNS_TO_KEEP = 5;

/**
 * Extract timestamp from file/folder name.
 * Format: anything_YYYYMMDD_HHMMSS.ext or anything_YYYYMMDD_HHMMSS/
 * Returns: YYYYMMDD_HHMMSS as string for sorting
 */
function extractTimestamp(filename) {
    // Match pattern: 8 digits + underscore + 6 digits
    const match = filename.match(/(\d{8})_(\d{6})/);
    if (match) {
        return `${match[1]}_${match[2]}`;
    }
    return null;
}

/**
 * Deletes a file or directory recursively.
 */
function deleteRecursive(itemPath) {
    try {
        if (fs.existsSync(itemPath)) {
            if (fs.lstatSync(itemPath).isDirectory()) {
                fs.readdirSync(itemPath).forEach((file) => {
                    deleteRecursive(path.join(itemPath, file));
                });
                fs.rmdirSync(itemPath);
            } else {
                fs.unlinkSync(itemPath);
            }
        }
    } catch (err) {
        // Silently ignore errors (e.g., permission issues)
    }
}

/**
 * Get all test runs in a folder, sorted by timestamp (newest first).
 */
function getTestRunsInFolder(folderPath) {
    if (!fs.existsSync(folderPath)) {
        return [];
    }

    const items = fs.readdirSync(folderPath);
    const runs = items
        .map((item) => {
            const timestamp = extractTimestamp(item);
            return { name: item, timestamp };
        })
        .filter((r) => r.timestamp !== null)
        .sort((a, b) => b.timestamp.localeCompare(a.timestamp)); // Newest first

    return runs;
}

/**
 * Cleanup: keep only the last MAX_RUNS_TO_KEEP test runs in each folder.
 */
function cleanup() {
    const frameworkRoot = path.resolve(__dirname, '..');

    // Define folders to clean
    const foldersToClean = [
        { path: path.join(frameworkRoot, config.logsDir), label: 'Logs' },
        {
            path: path.join(frameworkRoot, config.screenshotDir),
            label: 'ScreenshotAttachment',
        },
        { path: path.join(frameworkRoot, config.reportsDir), label: 'Reports' },
    ];

    let totalDeleted = 0;

    foldersToClean.forEach(({ path: folderPath, label }) => {
        const runs = getTestRunsInFolder(folderPath);

        if (runs.length > MAX_RUNS_TO_KEEP) {
            const toDelete = runs.slice(MAX_RUNS_TO_KEEP); // Everything after the 5th
            console.log(
                `[Cleanup] ${label}: keeping ${MAX_RUNS_TO_KEEP}, deleting ${toDelete.length} old run(s)`
            );

            toDelete.forEach(({ name }) => {
                const itemPath = path.join(folderPath, name);
                deleteRecursive(itemPath);
                totalDeleted++;
            });
        }
    });

    if (totalDeleted > 0) {
        console.log(`[Cleanup] Deleted ${totalDeleted} old test run artifact(s)`);
    }
}

module.exports = { cleanup };
