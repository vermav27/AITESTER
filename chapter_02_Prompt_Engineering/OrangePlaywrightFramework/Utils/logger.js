/**
 * Logger — writes a per-run log file into the Logs/ folder with the naming
 * convention `Logs_TestRun_<DateStamp>_<TimeStamp>.txt` (RICE-POT I-6) and
 * mirrors every line to the console (RICE-POT O-1).
 *
 * Usage:
 *   const logger = require('./Utils/logger');
 *   logger.init();                       // once per run, creates the log file
 *   logger.info('Some message');
 *   logger.error('Some error');
 */
const fs = require('fs');
const path = require('path');

const config = require('../config/config');

let logStream = null;
let logFilePath = null;

function timestamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return (
    `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
  );
}

function dateStamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return (
    `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`
  );
}

function timeStamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}

function init() {
  if (logStream) return logFilePath;
  const frameworkRoot = path.resolve(__dirname, '..');
  const logsDir = path.join(frameworkRoot, config.logsDir);
  if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });
  logFilePath = path.join(
    logsDir,
    `Logs_TestRun_${dateStamp()}_${timeStamp()}.txt`
  );
  logStream = fs.createWriteStream(logFilePath, { flags: 'a' });
  info('Log file created');
  return logFilePath;
}

function write(level, message) {
  const line = `[${timestamp()}] [${level}] ${message}`;
  // Console output (RICE-POT O-1)
  if (level === 'ERROR') {
    console.error(line);
  } else {
    console.log(line);
  }
  if (logStream) logStream.write(`${line}\n`);
}

function info(message) {
  write('INFO', message);
}

function warn(message) {
  write('WARN', message);
}

function error(message) {
  write('ERROR', message);
}

function close() {
  if (logStream) {
    logStream.end();
    logStream = null;
  }
}

module.exports = { init, info, warn, error, close, getLogFilePath: () => logFilePath };
