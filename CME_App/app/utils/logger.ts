const isDev = __DEV__;

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  component?: string;
}

class Logger {
  private logs: LogEntry[] = [];
  private maxLogs = 100;

  private formatMessage(level: LogLevel, message: string, data?: any, component?: string): string {
    const timestamp = new Date().toISOString();
    const levelStr = LogLevel[level];
    const componentStr = component ? `[${component}]` : '';
    return `${timestamp} ${levelStr}${componentStr}: ${message}`;
  }

  private addLog(level: LogLevel, message: string, data?: any, component?: string) {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      component,
    };

    this.logs.push(logEntry);
    
    // Keep only the last maxLogs entries
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    if (isDev) {
      const formattedMessage = this.formatMessage(level, message, data, component);
      switch (level) {
        case LogLevel.DEBUG:
          console.log(formattedMessage, data || '');
          break;
        case LogLevel.INFO:
          console.info(formattedMessage, data || '');
          break;
        case LogLevel.WARN:
          console.warn(formattedMessage, data || '');
          break;
        case LogLevel.ERROR:
          console.error(formattedMessage, data || '');
          break;
      }
    }
  }

  debug(message: string, data?: any, component?: string) {
    this.addLog(LogLevel.DEBUG, message, data, component);
  }

  info(message: string, data?: any, component?: string) {
    this.addLog(LogLevel.INFO, message, data, component);
  }

  warn(message: string, data?: any, component?: string) {
    this.addLog(LogLevel.WARN, message, data, component);
  }

  error(message: string, data?: any, component?: string) {
    this.addLog(LogLevel.ERROR, message, data, component);
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }
}

export const logger = new Logger(); 