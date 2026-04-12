import ProjectModel from '../models/project.model.js';
import storageService from '../services/storage.service.js';
import FileValidator from '../utils/fileValidator.js';
import asyncHandler from '../utils/asyncHandler.js';
import { toPositiveInt } from '../utils/helpers.js';
import path from 'path';
import fs from 'fs/promises';
import logger from '../utils/logger.js';



const SKIP_DIRS = new Set(['node_modules', '.git', '__pycache__', 'venv', '.venv']);

const analyzeProjectDirectory = async (rootPath) => {
  const summary = {
    totalFiles: 0,
    pythonFiles: 0,
    templateFiles: 0,
    staticFiles: 0,
    hasManagePy: false,
    hasSettings: false,
    hasUrls: false,
    hasModels: false,
    hasViews: false,
    detectedFramework: 'unknown',
  };

  const walk = async (currentPath) => {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (!SKIP_DIRS.has(entry.name)) {
          await walk(path.join(currentPath, entry.name));
        }
        continue;
      }

      summary.totalFiles += 1;
      const fullPath = path.join(currentPath, entry.name);
      const relativePath = path.relative(rootPath, fullPath).replace(/\\/g, '/');

      if (entry.name.endsWith('.py')) {
        summary.pythonFiles += 1;
      }

      if (entry.name.endsWith('.html')) {
        summary.templateFiles += 1;
      }

      if (/\.(css|js|png|jpg|jpeg|svg)$/i.test(entry.name)) {
        summary.staticFiles += 1;
      }

      if (relativePath === 'manage.py') {
        summary.hasManagePy = true;
      }
      if (relativePath.endsWith('/settings.py') || relativePath === 'settings.py') {
        summary.hasSettings = true;
      }
      if (relativePath.endsWith('/urls.py') || relativePath === 'urls.py') {
        summary.hasUrls = true;
      }
      if (relativePath.endsWith('/models.py') || relativePath === 'models.py') {
        summary.hasModels = true;
      }
      if (relativePath.endsWith('/views.py') || relativePath === 'views.py') {
        summary.hasViews = true;
      }
    }
  };

  await walk(rootPath);

  if (summary.hasManagePy && summary.hasSettings && summary.hasUrls) {
    summary.detectedFramework = 'django';
  }

  return summary;
};

/**
 * Upload project (ZIP file)
 * POST /api/projects/upload
 */
export const uploadProject = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const file = req.file;
  const { name } = req.body;

  if (!file) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'No file uploaded'
      }
    });
  }

  // Additional validation
  const validation = FileValidator.validate(file);
  if (!validation.valid) {
    // Delete uploaded file
    await storageService.deleteFile(file.path);

    return res.status(400).json({
      success: false,
      error: {
        message: validation.error
      }
    });
  }

  // Create project directory
  const projectPath = await storageService.createProjectDirectory(userId);

  // Extract ZIP file
  try {
    await storageService.extractZip(file.path, projectPath);

    // Get project size
    const size_bytes = await storageService.getDirectorySize(projectPath);
    const requestedName = name || path.parse(file.originalname).name;
    const uniqueName = await ProjectModel.generateUniqueActiveName(userId, requestedName);

    // Create project record
    const project = await ProjectModel.create({
      user_id: userId,
      name: uniqueName,
      source_type: 'upload',
      file_path: projectPath,
      size_bytes
    });

    // Delete uploaded ZIP file
    await storageService.deleteFile(file.path);

    logger.info(`Project uploaded: ${project.id} by user ${userId}`);

    res.status(201).json({
      success: true,
      data: {
        project
      }
    });
  } catch (error) {
    // Cleanup on error
    await storageService.deleteFile(file.path);
    await storageService.deleteDirectory(projectPath);

    logger.error('Project upload failed:', error);
    throw error;
  }
});

/**
 * Import project from GitHub
 * POST /api/projects/github
 */
export const importFromGithub = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const { repoUrl, name, description } = req.body;

  if (!repoUrl) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Repository URL is required'
      }
    });
  }

  // Create project record
  const requestedName = name || path.basename(repoUrl, '.git');
  const uniqueName = await ProjectModel.generateUniqueActiveName(userId, requestedName);

  const project = await ProjectModel.create({
    user_id: userId,
    name: uniqueName,
    description,
    source_type: 'github',
    source_url: repoUrl
  });

  logger.info(`GitHub project created: ${project.id} by user ${userId}`);

  res.status(201).json({
    success: true,
    data: {
      project
    },
    message: 'Project created. Use GitHub service to clone the repository.'
  });
});

/**
 * Get all projects for current user
 * GET /api/projects
 */
export const getUserProjects = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const page = toPositiveInt(req.query.page, 1, 1000000);
  const pageSize = toPositiveInt(req.query.pageSize, 10, 100);

  const result = await ProjectModel.getPaginated(userId, page, pageSize);

  res.json({
    success: true,
    data: result
  });
});

/**
 * Get project by ID
 * GET /api/projects/:id
 */
export const getProjectById = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const { id } = req.params;

  const project = await ProjectModel.findByIdAndUserId(id, userId);

  if (!project) {
    return res.status(404).json({
      success: false,
      error: {
        message: 'Project not found'
      }
    });
  }

  res.json({
    success: true,
    data: {
      project
    }
  });
});

/**
 * Update project
 * PATCH /api/projects/:id
 */
export const updateProject = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const { id } = req.params;
  const { name, description } = req.body;

  // Check if project exists and belongs to user
  const existingProject = await ProjectModel.findByIdAndUserId(id, userId);

  if (!existingProject) {
    return res.status(404).json({
      success: false,
      error: {
        message: 'Project not found'
      }
    });
  }

  // Update project
  const updateData = {};
  if (name) updateData.name = name;
  if (description !== undefined) updateData.description = description;

  if (Object.keys(updateData).length === 0) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'No valid fields provided for update'
      }
    });
  }

  const project = await ProjectModel.update(id, updateData);

  logger.info(`Project updated: ${id} by user ${userId}`);

  res.json({
    success: true,
    data: {
      project
    }
  });
});

/**
 * Delete project
 * DELETE /api/projects/:id
 */
export const deleteProject = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const { id } = req.params;

  // Check if project exists and belongs to user
  const project = await ProjectModel.findByIdAndUserId(id, userId);
  if (!project) {
    return res.status(404).json({
      success: false,
      error: {
        message: 'Project not found'
      }
    });
  }

  // Delete project files
  if (project.file_path) {
    await storageService.deleteDirectory(project.file_path);
  }

  // Delete project record
  await ProjectModel.delete(id);

  logger.info(`Project deleted: ${id} by user ${userId}`);

  res.json({
    success: true,
    message: 'Project deleted successfully'
  });
});

/**
 * Analyze project structure
 * GET /api/projects/:id/analyze
 */
export const analyzeProject = asyncHandler(async (req, res) => {
  const { userId } = req.user;
  const { id } = req.params;

  // Check if project exists and belongs to user
  const project = await ProjectModel.findByIdAndUserId(id, userId);

  if (!project) {
    return res.status(404).json({
      success: false,
      error: {
        message: 'Project not found'
      }
    });
  }

  if (!project.file_path) {
    return res.status(400).json({
      success: false,
      error: {
        message: 'Project does not have a local file path to analyze'
      }
    });
  }

  const analysis = await analyzeProjectDirectory(project.file_path);

  res.json({
    success: true,
    message: 'Project analysis completed',
    data: {
      projectId: id,
      projectPath: project.file_path,
      analysis
    }
  });
});
