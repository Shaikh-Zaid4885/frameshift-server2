import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs/promises';
import fsSync from 'fs';
import ConversionJobModel from '../models/conversionJob.model.js';
import ReportModel from '../models/report.model.js';
import UserModel from '../models/user.model.js';
import storageService from './storage.service.js';
import emailService from './email.service.js';
import DiffService from './diff.service.js';
import logger from '../utils/logger.js';
import { decrypt } from '../utils/encryption.js';
import { normalizeConversionMode } from '../utils/customApiConfig.js';

/**
 * Map to track active Python conversion processes
 * Key: jobId, Value: ChildProcess
 */
const activeProcesses = new Map();

/**
 * Conversion service - Node-Python bridge
 * Manages Python child processes for Django-to-Flask conversion
 */
export class ConversionService {
  /**
   * Start conversion process
   * @param {string} jobId - Conversion job ID
   * @param {string} projectPath - Path to Django project
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Conversion result
   */
  static async startConversion(
    jobId,
    projectPath,
    userId,
    useAI = true,
    conversionMode = 'default',
    customApiConfig = null,
    geminiApiKey = null
  ) {
    const resolvedMode = normalizeConversionMode(conversionMode);
    logger.info(`Starting conversion job ${jobId} (AI: ${useAI ? 'enabled' : 'disabled'}, mode: ${resolvedMode})`);

    try {
      // Create output directory
      const outputPath = await storageService.createConvertedDirectory(userId, jobId);

      // Mark job as started
      await ConversionJobModel.markAsStarted(jobId);

      const job = await ConversionJobModel.findById(jobId);
      const effectiveCustomConfig = customApiConfig || job?.custom_api_config || null;
      const effectiveMode = normalizeConversionMode(job?.conversion_mode || resolvedMode);

      // Spawn Python process with AI mode/config
      const result = await this.runPythonConversion(
        jobId,
        projectPath,
        outputPath,
        useAI,
        effectiveMode,
        effectiveCustomConfig,
        geminiApiKey
      );

      const latestJob = await ConversionJobModel.findById(jobId);
      const reportWithRuntimeSignals = this.enrichReportWithRuntimeSignals(
        result.report,
        useAI,
        latestJob?.ai_enhancements
      );

      // Mark job as completed
      await ConversionJobModel.markAsCompleted(jobId, outputPath);

      // Run report saving and diff generation in parallel for better performance
      const [reportResult, diffResult] = await Promise.allSettled([
        this.saveReport(jobId, reportWithRuntimeSignals),
        this.generateDiffs(jobId, projectPath, outputPath, reportWithRuntimeSignals)
          .catch(diffError => {
            logger.error(`Failed to generate diffs for job ${jobId}:`, diffError);
            // Don't fail the conversion if diff generation fails
            return null;
          })
      ]);

      if (reportResult.status === 'rejected') {
        logger.error(`Report saving failed for job ${jobId}:`, reportResult.reason);
      }
      if (diffResult.status === 'rejected') {
        logger.error(`Diff generation failed for job ${jobId}:`, diffResult.reason);
      }

      const validation = await this.validateConvertedOutput(outputPath);
      await this.applyValidationResult(jobId, validation, reportWithRuntimeSignals);
      await ConversionJobModel.markAsValidated(jobId);

      // Send success email
      try {
        const user = await UserModel.findById(userId);
        const job = await ConversionJobModel.findById(jobId);
        await emailService.sendConversionCompleteEmail(user, job, reportWithRuntimeSignals);
      } catch (emailError) {
        logger.error(`Failed to send completion email for job ${jobId}:`, emailError);
        // Don't fail the conversion if email fails
      }

      logger.info(`Conversion job ${jobId} completed successfully and passed validation`);

      return {
        success: true,
        jobId,
        outputPath,
        status: 'validated',
        report: reportWithRuntimeSignals,
        validation
      };
    } catch (error) {
      logger.error(`Conversion job ${jobId} failed:`, error);

      // Mark job as failed
      await ConversionJobModel.markAsFailed(jobId, error.message);

      // Send failure email
      try {
        const user = await UserModel.findById(userId);
        const job = await ConversionJobModel.findById(jobId);
        await emailService.sendConversionFailedEmail(user, job, error.message);
      } catch (emailError) {
        logger.error(`Failed to send failure email for job ${jobId}:`, emailError);
        // Don't fail further if email fails
      }

      throw error;
    }
  }

  /**
   * Detect Python executable on the system
   * @returns {string} Python executable path
   */
  static detectPython() {
    // If explicitly set in env, use it
    if (process.env.PYTHON_PATH) {
      return process.env.PYTHON_PATH;
    }

    // Prefer project-local virtual environment when available
    const localVenvPython = process.platform === 'win32'
      ? path.join(process.cwd(), 'python', '.venv', 'Scripts', 'python.exe')
      : path.join(process.cwd(), 'python', '.venv', 'bin', 'python');

    if (fsSync.existsSync(localVenvPython)) {
      return localVenvPython;
    }

    // On Windows, prefer 'python' over 'python3' (python3 is often the MS Store stub)
    if (process.platform === 'win32') {
      return 'python';
    }

    // On Unix-like systems, prefer python3
    return 'python3';
  }

  /**
   * Run Python conversion process
   * @param {string} jobId - Conversion job ID
   * @param {string} projectPath - Input Django project path
   * @param {string} outputPath - Output Flask project path
   * @param {boolean} useAI - Whether to use AI enhancement
   * @returns {Promise<Object>} Conversion result from Python
   */
  static runPythonConversion(
    jobId,
    projectPath,
    outputPath,
    useAI = true,
    conversionMode = 'default',
    customApiConfig = null,
    geminiApiKey = null
  ) {
    return new Promise((resolve, reject) => {
      const pythonPath = this.detectPython();
      const scriptPath = path.join(process.cwd(), 'python', 'main.py');

      const args = [
        scriptPath,
        '--job-id', jobId,
        '--project-path', projectPath,
        '--output-path', outputPath,
        '--use-ai', useAI.toString(),
        '--conversion-mode', normalizeConversionMode(conversionMode)
      ];

      // Add Gemini API key if available (prefer user-provided key over environment variable)
      const apiKeyToUse = geminiApiKey || process.env.GEMINI_API_KEY;
      if (apiKeyToUse) {
        args.push('--gemini-api-key', apiKeyToUse);
      }

      const pythonEnv = { ...process.env };
      if (normalizeConversionMode(conversionMode) === 'custom' && customApiConfig) {
        pythonEnv.CUSTOM_API_PROVIDER = customApiConfig.provider || '';
        pythonEnv.CUSTOM_API_KEY = customApiConfig.api_key ? decrypt(customApiConfig.api_key) : '';
        pythonEnv.CUSTOM_API_ENDPOINT = customApiConfig.endpoint || '';
        pythonEnv.CUSTOM_API_MODEL = customApiConfig.model || '';
      } else {
        delete pythonEnv.CUSTOM_API_PROVIDER;
        delete pythonEnv.CUSTOM_API_KEY;
        delete pythonEnv.CUSTOM_API_ENDPOINT;
        delete pythonEnv.CUSTOM_API_MODEL;
      }

      logger.info(`Spawning Python process for job ${jobId} in ${normalizeConversionMode(conversionMode)} mode`);

      const pythonProcess = spawn(pythonPath, args, {
        cwd: process.cwd(),
        env: pythonEnv
      });

      // Store process in activeProcesses map for cancellation support
      activeProcesses.set(jobId, pythonProcess);
      logger.info(`Stored active process for job ${jobId} (PID: ${pythonProcess.pid})`);

      // Add timeout protection - 30 minutes max
      const CONVERSION_TIMEOUT = 30 * 60 * 1000;
      let timeoutId = setTimeout(() => {
        if (!isResolved) {
          isResolved = true;
          logger.error(`Conversion job ${jobId} exceeded 30 minute timeout`);
          
          if (pythonProcess && !pythonProcess.killed) {
            pythonProcess.kill('SIGKILL');
          }
          
          activeProcesses.delete(jobId);
          reject(new Error('Conversion timeout: Process exceeded 30 minute limit'));
        }
      }, CONVERSION_TIMEOUT);

      let result = null;
      let errorOutput = '';
      let isResolved = false;

      let stdoutBuffer = '';
      // Handle stdout (progress updates and result)
      pythonProcess.stdout.on('data', async (data) => {
        stdoutBuffer += data.toString();
        
        let newlineIndex;
        while ((newlineIndex = stdoutBuffer.indexOf('\n')) !== -1) {
          const line = stdoutBuffer.slice(0, newlineIndex);
          stdoutBuffer = stdoutBuffer.slice(newlineIndex + 1);

          if (!line.trim()) continue;

          try {
            const message = JSON.parse(line);

            if (message.type === 'progress') {
              // Update database with progress
              await this.handleProgressUpdate(jobId, message);
            } else if (message.type === 'result') {
              // Store final result
              result = message.data;
              logger.info(`Conversion result received for job ${jobId}`);
            } else if (message.type === 'ai_enhancements_result') {
              // Store AI enhancements directly to database
              await this.handleAIEnhancementsResult(jobId, message.data);
              logger.info(`AI enhancements recorded for job ${jobId}`);
            } else if (message.type === 'error') {
              errorOutput = message.error;
              logger.error(`Python error for job ${jobId}: ${message.error}`);
            }
          } catch (parseError) {
            // Not JSON, could be regular log output
            logger.debug(`Python output: ${line}`);
          }
        }
      });

      // Handle stderr
      pythonProcess.stderr.on('data', (data) => {
        const errorText = data.toString();
        errorOutput += errorText;
        logger.error(`Python stderr: ${errorText}`);
      });

      // Handle process exit
      pythonProcess.on('close', (code) => {
        // Clear timeout
        clearTimeout(timeoutId);
        
        // Remove from active processes
        activeProcesses.delete(jobId);
        logger.info(`Removed process for job ${jobId} from active processes (exit code: ${code})`);

        // Prevent multiple resolve/reject calls
        if (isResolved) return;

        // Give a small delay to ensure all stdout has been processed
        setTimeout(() => {
          if (isResolved) return;
          isResolved = true;

          if (code === 0) {
            if (result) {
              logger.info(`Python process exited successfully for job ${jobId}`);
              resolve(result);
            } else {
              const error = new Error('Python process completed but no result was received');
              logger.error(`Python process failed for job ${jobId}: ${error.message}`);
              reject(error);
            }
          } else {
            const error = new Error(errorOutput || `Python process exited with code ${code}`);
            logger.error(`Python process failed for job ${jobId}: ${error.message}`);
            reject(error);
          }
        }, 100);
      });

      // Handle process error
      pythonProcess.on('error', (error) => {
        clearTimeout(timeoutId);
        if (isResolved) return;
        isResolved = true;
        logger.error(`Failed to spawn Python process for job ${jobId}:`, error);
        reject(new Error(`Failed to start Python conversion: ${error.message}`));
      });
    });
  }

  /**
   * Handle progress update from Python
   * @param {string} jobId - Conversion job ID
   * @param {Object} message - Progress message
   */
  static async handleProgressUpdate(jobId, message) {
    try {
      // Map Python steps to conversion statuses for better progress tracking
      const stepToStatus = {
        'detecting_framework': 'analyzing',
        'analyzing': 'analyzing',
        'converting_models': 'converting',
        'converting_views': 'converting',
        'converting_urls': 'converting',
        'converting_templates': 'converting',
        'copying_static': 'converting',
        'generating_skeleton': 'converting',
        'ai_full_enhancement': 'converting',
        'ai_enhancement': 'verifying',
        'verifying': 'verifying',
        'generating_report': 'verifying',
        'completed': 'completed'
      };

      const newStatus = stepToStatus[message.step];
      
      // Update database with progress
      await ConversionJobModel.updateProgress(
        jobId,
        message.progress,
        message.step
      );

      // Update status if it changed from current
      if (newStatus) {
        const job = await ConversionJobModel.findById(jobId);
        if (job && job.status !== newStatus && !['completed', 'validated', 'failed'].includes(job.status)) {
          await ConversionJobModel.updateStatus(jobId, newStatus);
          logger.info(`Job ${jobId} status updated: ${job.status} → ${newStatus}`);
        }
      }

      // Broadcast via WebSocket with both progress and status
      const { broadcastProgress } = await import('./websocket.service.js');
      broadcastProgress(jobId, {
        ...message,
        status: newStatus
      });

      logger.debug(`Progress updated for job ${jobId}: ${message.progress}% - ${message.step}`);
    } catch (error) {
      logger.error(`Failed to handle progress update for job ${jobId}:`, error);
    }
  }

  /**
   * Handle AI enhancement results from Python
   * @param {string} jobId - Conversion job ID
   * @param {Object} aiData - AI enhancement data
   */
  static async handleAIEnhancementsResult(jobId, aiData) {
    try {
      // Update report with initial AI data if report exists, otherwise store for later
      // In this architecture, it's safer to update the job model directly if possible,
      // or store in a temporary way. Assuming we might want to attach this to the eventual report.

      // Since the report is created AT THE END, we can't update it yet.
      // But we can update the ConversionJob to store this metadata temporarily or permanently.
      await ConversionJobModel.update(jobId, {
        ai_enhancements: aiData
      });

      logger.debug(`AI enhancements stored for job ${jobId}: ${aiData.length} items`);
    } catch (error) {
      logger.error(`Failed to handle AI enhancements for job ${jobId}:`, error);
    }
  }

  static enrichReportWithRuntimeSignals(report = {}, useAI, aiEnhancements = []) {
    const warnings = Array.isArray(report.warnings) ? [...report.warnings] : [];
    const summaryParts = [report.summary].filter(Boolean);

    if (useAI && (!Array.isArray(aiEnhancements) || aiEnhancements.length === 0)) {
      warnings.push('AI enhancement was enabled, but no verified AI fixes were recorded for this run.');
      summaryParts.push('AI enhancement did not contribute any recorded fixes in this run.');
    }

    return {
      ...report,
      warnings,
      summary: summaryParts.join(' ').trim()
    };
  }

  static async applyValidationResult(jobId, validation, report = {}) {
    const issues = Array.isArray(report.issues) ? [...report.issues] : [];
    const warnings = Array.isArray(report.warnings) ? [...report.warnings] : [];
    const suggestions = Array.isArray(report.suggestions) ? [...report.suggestions] : [];
    const summaryParts = [report.summary].filter(Boolean);

    if (Array.isArray(validation.warnings)) {
      warnings.push(...validation.warnings);
    }

    if (validation.passed) {
      summaryParts.push(
        `Post-conversion validation passed after checking ${validation.filesChecked} Python files.`
      );
      await ReportModel.updateByConversionId(jobId, {
        warnings,
        summary: summaryParts.join(' ').trim()
      });
      return;
    }

    if (Array.isArray(validation.issues)) {
      issues.push(...validation.issues);
    }

    suggestions.push('Review generated Flask entry points, route registration, and syntax errors before trusting this conversion output.');
    summaryParts.push('Post-conversion validation failed. The conversion output is not considered reliable.');

    await ReportModel.updateByConversionId(jobId, {
      issues,
      warnings,
      suggestions,
      summary: summaryParts.join(' ').trim()
    });

    const error = new Error(validation.issues?.[0] || 'Post-conversion validation failed');
    error.code = 'VALIDATION_FAILED';
    throw error;
  }

  static async validateConvertedOutput(outputPath) {
    const projectPath = await this.resolveConvertedProjectPath(outputPath);
    const issues = [];
    const warnings = [];

    if (!projectPath) {
      return {
        passed: false,
        issues: ['Converted project directory could not be located.'],
        warnings,
        filesChecked: 0
      };
    }

    const pythonFiles = await this.collectPythonFiles(projectPath);

    if (pythonFiles.length === 0) {
      issues.push('No Python files were generated in the converted project.');
    }

    const hasFlaskEntry = await this.hasFlaskEntryPoint(pythonFiles);
    if (!hasFlaskEntry) {
      issues.push('Converted output does not contain a detectable Flask app or Blueprint entry point.');
    }

    const compileResult = await this.runPythonCompileCheck(pythonFiles);
    if (!compileResult.success) {
      issues.push(...compileResult.errors);
    }

    return {
      passed: issues.length === 0,
      issues,
      warnings,
      filesChecked: pythonFiles.length
    };
  }

  static async resolveConvertedProjectPath(outputPath) {
    try {
      const entries = await fs.readdir(outputPath, { withFileTypes: true });
      const subdirs = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
      return subdirs.length > 0 ? path.join(outputPath, subdirs[0]) : outputPath;
    } catch (error) {
      logger.error(`Failed to resolve converted project path for ${outputPath}:`, error);
      return null;
    }
  }

  static async collectPythonFiles(dir) {
    const files = [];
    const skipDirs = new Set(['venv', 'node_modules', '__pycache__', '.git', 'migrations', 'instance', 'logs']);

    const walk = async (currentDir) => {
      const entries = await fs.readdir(currentDir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry.name);
        if (entry.isDirectory()) {
          if (!skipDirs.has(entry.name)) {
            await walk(fullPath);
          }
          continue;
        }

        if (entry.isFile() && entry.name.endsWith('.py')) {
          files.push(fullPath);
        }
      }
    };

    await walk(dir);
    return files;
  }

  static async hasFlaskEntryPoint(pythonFiles) {
    for (const filePath of pythonFiles) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        if (content.includes('Flask(') || content.includes('Blueprint(') || content.includes('Blueprint (')) {
          return true;
        }
      } catch (error) {
        logger.warn(`Failed to inspect generated file ${filePath}:`, error.message);
      }
    }

    return false;
  }

  static async runPythonCompileCheck(pythonFiles) {
    if (!pythonFiles.length) {
      return { success: false, errors: ['Converted output does not contain any Python files to validate.'] };
    }

    const pythonPath = this.detectPython();
    const errors = [];

    // py_compile only accepts ONE file at a time, so we validate each file
    // individually. To keep it efficient we still batch them but use a small
    // Python script that iterates over the file list rather than relying on
    // the py_compile module's CLI (which only compiles the first argument).
    const chunkSize = 50;

    for (let index = 0; index < pythonFiles.length; index += chunkSize) {
      const fileChunk = pythonFiles.slice(index, index + chunkSize);

      // Build a tiny script that tries to compile each file and prints errors
      const script = [
        'import sys, py_compile, json',
        'errors = []',
        'for f in sys.argv[1:]:',
        '    try:',
        '        py_compile.compile(f, doraise=True)',
        '    except py_compile.PyCompileError as e:',
        '        errors.append(str(e))',
        'if errors:',
        '    print(json.dumps(errors))',
        '    sys.exit(1)',
      ].join('\n');

      const chunkResult = await new Promise((resolve) => {
        const compileProcess = spawn(pythonPath, ['-c', script, ...fileChunk], {
          cwd: process.cwd(),
          env: process.env
        });

        let stdout = '';
        let stderr = '';

        compileProcess.stdout.on('data', (data) => {
          stdout += data.toString();
        });

        compileProcess.stderr.on('data', (data) => {
          stderr += data.toString();
        });

        compileProcess.on('close', (code) => {
          resolve({ success: code === 0, stdout, stderr });
        });

        compileProcess.on('error', (error) => {
          resolve({ success: false, stdout: '', stderr: error.message });
        });
      });

      if (!chunkResult.success) {
        // Try to parse structured error list from our script
        try {
          const parsed = JSON.parse(chunkResult.stdout.trim());
          if (Array.isArray(parsed)) {
            errors.push(...parsed.map(e => `Python syntax error: ${e}`));
            continue; // Continue checking remaining chunks
          }
        } catch {
          // fallback to stderr
        }
        errors.push(`Python syntax validation failed: ${chunkResult.stderr.trim() || chunkResult.stdout.trim() || 'Unknown compile error'}`);
        // Don't break — collect errors from all chunks
      }
    }

    return {
      success: errors.length === 0,
      errors
    };
  }

  /**
   * Save conversion report to database
   * @param {string} jobId - Conversion job ID
   * @param {Object} report - Report data from Python
   * @returns {Promise<Object>} Saved report
   */
  static async saveReport(jobId, report) {
    try {
      const reportData = {
        conversion_job_id: jobId,
        accuracy_score: report.accuracy_score || 0,
        total_files_converted: report.total_files_converted || 0,
        models_converted: report.models_converted || 0,
        views_converted: report.views_converted || 0,
        urls_converted: report.urls_converted || 0,
        forms_converted: report.forms_converted || 0,
        templates_converted: report.templates_converted || 0,
        issues: report.issues || [],
        warnings: report.warnings || [],
        suggestions: report.suggestions || [],
        gemini_verification: {
          ...(report.gemini_verification || {}),
          manual_changes_summary: report.manual_changes_summary || { total_items: 0, items: [] }
        },
        summary: report.summary || ''
      };

      const savedReport = await ReportModel.create(reportData);
      logger.info(`Report saved for job ${jobId}`);

      return savedReport;
    } catch (error) {
      logger.error(`Failed to save report for job ${jobId}:`, error);
      throw error;
    }
  }

  /**
   * Generate diffs for converted files
   * @param {string} jobId - Conversion job ID
   * @param {string} projectPath - Path to original Django project
   * @param {string} outputPath - Path to converted Flask project
   * @param {Object} report - Conversion report
   * @returns {Promise<void>}
   */
  static async generateDiffs(jobId, projectPath, outputPath, report) {
    try {
      logger.info(`Generating diffs for job ${jobId}`);

      const fileDiffs = [];

      // Find actual project directory inside the upload directory
      // The upload path may contain a single project directory (e.g., "Job Portal")
      let projectName;
      try {
        const entries = await fs.readdir(projectPath, { withFileTypes: true });
        const subdirs = entries.filter(entry => entry.isDirectory()).map(entry => entry.name);

        // Use the first subdirectory as project name, or fall back to the directory name
        projectName = subdirs.length > 0 ? subdirs[0] : path.basename(projectPath);
        logger.info(`Using project name for diffs: ${projectName}`);
      } catch (err) {
        logger.warn(`Error reading project directory ${projectPath}, using basename:`, err.message);
        projectName = path.basename(projectPath);
      }

      const convertedProjectPath = path.join(outputPath, projectName);

      // Recursively find all convertible files (Python + HTML templates) in converted directory
      const CONVERTIBLE_EXTENSIONS = new Set(['.py', '.html', '.htm', '.jinja2', '.j2']);
      const findConvertibleFiles = async (dir, baseDir) => {
        const files = [];
        try {
          const entries = await fs.readdir(dir, { withFileTypes: true });

          for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);

            if (entry.isDirectory()) {
              // Skip common directories
              if (!['venv', 'node_modules', '__pycache__', '.git', 'migrations', 'instance', 'logs'].includes(entry.name)) {
                const subFiles = await findConvertibleFiles(fullPath, baseDir);
                files.push(...subFiles);
              }
            } else if (entry.isFile()) {
              const ext = path.extname(entry.name).toLowerCase();
              if (CONVERTIBLE_EXTENSIONS.has(ext)) {
                const relativePath = path.relative(baseDir, fullPath);
                files.push(relativePath);
              }
            }
          }
        } catch (err) {
          logger.warn(`Error reading directory ${dir}:`, err.message);
        }

        return files;
      };

      // Find all convertible files in the converted project
      const convertedFiles = await findConvertibleFiles(convertedProjectPath, convertedProjectPath);

      logger.info(`Found ${convertedFiles.length} Python files in converted project`);

      // Original project path includes the project directory
      const originalProjectPath = path.join(projectPath, projectName);

      // Generate diff for each file
      for (const relativeFilePath of convertedFiles) {
        try {
          const convertedFile = path.join(convertedProjectPath, relativeFilePath);
          const originalFile = path.join(originalProjectPath, relativeFilePath);

          // Check if original file exists
          const originalExists = await fs.access(originalFile).then(() => true).catch(() => false);

          // Determine category from file path
          const category = relativeFilePath.includes('models') ? 'models' :
            relativeFilePath.includes('views') ? 'views' :
              relativeFilePath.includes('urls') || relativeFilePath.includes('routes') ? 'urls' :
                relativeFilePath.includes('forms') ? 'forms' :
                  relativeFilePath.includes('template') ? 'templates' :
                    'other';

          let diffData;

          if (originalExists) {
            // Generate diff between original and converted
            diffData = await DiffService.generateFileDiff(originalFile, convertedFile, {
              originalPath: relativeFilePath,
              convertedPath: relativeFilePath,
              category: category,
              confidence: null
            });
          } else {
            // New file (generated by converter) — still scan for manual change markers
            const convertedContent = await fs.readFile(convertedFile, 'utf-8');
            diffData = DiffService.generateDiffFromContent(
              '', convertedContent,
              relativeFilePath, relativeFilePath,
              { category, confidence: null }
            );
            diffData.isNewFile = true;
          }

          // Add unique ID
          const safeFileId = Buffer
            .from(relativeFilePath)
            .toString('base64url');
          diffData.id = `${jobId}-${safeFileId}`;

          // Detect Django-specific lines that need manual changes
          diffData.manual_changes = DiffService.findUnchangedDjangoLines(diffData);

          // Broadcast diff in real-time to client (streaming)
          try {
            const { broadcastDiffGenerated } = await import('./websocket.service.js');
            broadcastDiffGenerated(jobId, diffData);
          } catch (broadcastError) {
            logger.debug(`Failed to broadcast diff for ${relativeFilePath}:`, broadcastError.message);
            // Don't fail if broadcast fails, just continue
          }

          fileDiffs.push(diffData);
          logger.debug(`Generated diff for ${relativeFilePath} (new: ${!originalExists})`);
        } catch (fileError) {
          logger.warn(`Failed to generate diff for ${relativeFilePath}:`, fileError.message);
        }
      }

      // Update report with file_diffs (final save)
      await ReportModel.updateByConversionId(jobId, {
        file_diffs: fileDiffs
      });

      logger.info(`Generated and streamed ${fileDiffs.length} file diffs for job ${jobId}`);
    } catch (error) {
      logger.error(`Error generating diffs for job ${jobId}:`, error);
      throw error;
    }
  }

  /**
   * Get conversion status
   * @param {string} jobId - Conversion job ID
   * @returns {Promise<Object>} Job status
   */
  static async getStatus(jobId) {
    const job = await ConversionJobModel.findById(jobId);

    if (!job) {
      throw new Error('Conversion job not found');
    }

    return {
      id: job.id,
      status: job.status,
      progress: job.progress_percentage,
      currentStep: job.current_step,
      startedAt: job.started_at,
      completedAt: job.completed_at,
      error: job.error_message
    };
  }

  /**
   * Cancel conversion job
   * @param {string} jobId - Conversion job ID
   * @returns {Promise<boolean>} Success status
   */
  static async cancelConversion(jobId) {
    logger.info(`Attempting to cancel conversion job ${jobId}`);

    try {
      // Get the active process
      const pythonProcess = activeProcesses.get(jobId);

      if (pythonProcess && !pythonProcess.killed) {
        logger.info(`Found active process for job ${jobId} (PID: ${pythonProcess.pid}), terminating...`);

        // Send SIGTERM for graceful shutdown
        pythonProcess.kill('SIGTERM');

        // Force kill after 5 seconds if still running
        const forceKillTimeout = setTimeout(() => {
          if (!pythonProcess.killed) {
            logger.warn(`Force killing process for job ${jobId} after 5 second timeout`);
            pythonProcess.kill('SIGKILL');
          }
        }, 5000);

        // Wait for process to exit
        await new Promise((resolve) => {
          pythonProcess.once('close', () => {
            clearTimeout(forceKillTimeout);
            resolve();
          });

          // Ensure we don't wait forever
          setTimeout(resolve, 6000);
        });

        logger.info(`Process for job ${jobId} terminated successfully`);
      } else {
        logger.info(`No active process found for job ${jobId}, marking as cancelled in database`);
      }

      // Mark as cancelled in database
      await ConversionJobModel.markAsFailed(jobId, 'Cancelled by user');

      // Remove from active processes if still there
      activeProcesses.delete(jobId);

      // Broadcast cancellation via WebSocket
      try {
        const { broadcastConversionCancelled } = await import('./websocket.service.js');
        const job = await ConversionJobModel.findById(jobId);
        if (job) {
          broadcastConversionCancelled(job.user_id, jobId);
        }
      } catch (wsError) {
        logger.error(`Failed to broadcast cancellation for job ${jobId}:`, wsError);
        // Don't fail the cancellation if WebSocket broadcast fails
      }

      logger.info(`Conversion job ${jobId} cancelled successfully`);
      return true;
    } catch (error) {
      logger.error(`Error cancelling conversion job ${jobId}:`, error);
      throw error;
    }
  }

  /**
   * Get all active conversion processes
   * @returns {Array} Array of job IDs with active processes
   */
  static getActiveProcesses() {
    return Array.from(activeProcesses.keys());
  }

  /**
   * Cancel all active conversions (for graceful shutdown)
   * @returns {Promise<void>}
   */
  static async cancelAllConversions() {
    logger.info(`Cancelling all active conversions (${activeProcesses.size} processes)`);

    const cancellationPromises = [];

    for (const jobId of activeProcesses.keys()) {
      cancellationPromises.push(
        this.cancelConversion(jobId).catch((error) => {
          logger.error(`Failed to cancel job ${jobId} during shutdown:`, error);
        })
      );
    }

    await Promise.all(cancellationPromises);
    logger.info('All active conversions cancelled');
  }
}

export default ConversionService;
