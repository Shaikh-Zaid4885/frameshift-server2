import rateLimit from 'express-rate-limit';

const isDevelopment = process.env.NODE_ENV !== 'production';
const devOrProd = (devValue, prodValue) => (isDevelopment ? devValue : prodValue);

/**
 * Rate limiter for conversion endpoints
 * Development is intentionally looser to avoid blocking retry-heavy debugging.
 */
export const conversionLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: devOrProd(50, 5),
  message: 'Too many conversion requests from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Rate limiter for authentication endpoints
 * Max 10 auth requests per 15 minutes
 */
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: devOrProd(100, 10),
  message: 'Too many authentication attempts from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * Rate limiter for upload endpoints
 * Max 20 uploads per hour
 */
export const uploadLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: devOrProd(100, 20),
  message: 'Upload limit exceeded from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

/**
 * General API rate limiter
 * Max 100 requests per 15 minutes
 */
export const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: devOrProd(1000, 100),
  message: 'Too many requests from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});
