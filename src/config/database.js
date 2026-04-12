import pg from 'pg';
import logger from '../utils/logger.js';

const { Pool } = pg;

// Create PostgreSQL connection pool
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME || 'frameshift',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD,
  max: 30, // Increased from 20 to handle peak AI processing load
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000, // Increased from 2000 to prevent timeouts during bursty updates
});

pool.on('connect', () => {
  logger.info('Connected to PostgreSQL database');
});

pool.on('error', (err) => {
  logger.error('Unexpected error on idle client', err);
});

/**
 * Execute a query
 * @param {string} text - SQL query
 * @param {Array} params - Query parameters
 * @returns {Promise} Query result
 */
export const query = (text, params) => pool.query(text, params);

/**
 * Get a client from the pool for transactions
 * @returns {Promise} Pool client
 */
export const getClient = () => pool.connect();

export default pool;
