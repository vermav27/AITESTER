/**
 * Central configuration for the OrangePlaywrightFramework.
 * Single QA environment — no environment switching (RICE-POT I-8).
 *
 * Values are the RICE-POT spec defaults. They can be overridden through
 * a local `.env` file (see `.env.example`); `.env` is gitignored.
 */
const fs = require('fs');
const path = require('path');

// Minimal, zero-dependency .env loader (npm is not available in this
// environment). Reads KEY=VALUE lines into process.env without overriding
// already-set variables.
function loadEnvFile(envPath) {
  try {
    const content = fs.readFileSync(envPath, 'utf8');
    content.split(/\r?\n/).forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;
      const eqIndex = trimmed.indexOf('=');
      if (eqIndex <= 0) return;
      const key = trimmed.slice(0, eqIndex).trim();
      const value = trimmed.slice(eqIndex + 1).trim();
      if (key && process.env[key] === undefined) {
        process.env[key] = value;
      }
    });
  } catch (err) {
    // No .env file present — use spec defaults.
  }
}

loadEnvFile(path.join(__dirname, '..', '.env'));

const config = {
  baseURL: process.env.BASE_URL || 'https://opensource-demo.orangehrmlive.com/',
  validUsername: process.env.VALID_USERNAME || 'Admin',
  validPassword: process.env.VALID_PASSWORD || 'admin123',
  invalidUsername: process.env.INVALID_USERNAME || 'invalid',
  invalidPassword: process.env.INVALID_PASSWORD || 'incorrectpassword',
  // Gate: releases only go ahead at a 99% pass rate (RICE-POT I-7).
  passRateThreshold: Number(process.env.PASS_RATE_THRESHOLD || 99),
  // Artifact folder names (RICE-POT I-5, I-6, I-7).
  screenshotDir: 'ScreenshotAttachment',
  logsDir: 'Logs',
  reportsDir: 'Reports',
};

module.exports = config;
