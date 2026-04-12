import logger from '../utils/logger.js';

/**
 * Global error handling middleware
 * @param {Error} err - Error object
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const errorHandler = (err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  
  // Log error based on status code
  if (statusCode >= 500) {
    logger.error(`[500] INTERNAL ERROR: ${err.message}`, { path: req.originalUrl, stack: err.stack });
  } else {
    logger.warn(`[${statusCode}] CLIENT ERROR: ${err.message}`, { path: req.originalUrl });
  }
  const errorCode = err.code || (statusCode >= 500 ? 'INTERNAL_ERROR' : 'REQUEST_ERROR');

  // Send error response
  res.status(statusCode).json({
    success: false,
    error: {
      code: errorCode,
      message: err.message || 'Internal Server Error',
      ...(err.details && { details: err.details }),
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
    },
  });
};

export default errorHandler;
