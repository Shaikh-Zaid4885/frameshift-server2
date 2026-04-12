-- Migration: Add ai_enhancing status to conversion_jobs_status_check
-- Purpose: Ensure the database allows the 'ai_enhancing' status used in the accuracy pipeline
-- Date: 2026-04-12

-- 1. Drop existing constraint
ALTER TABLE conversion_jobs
DROP CONSTRAINT IF EXISTS conversion_jobs_status_check;

-- 2. Add updated constraint including 'ai_enhancing' and 'validated'
ALTER TABLE conversion_jobs
ADD CONSTRAINT conversion_jobs_status_check
CHECK (status IN ('pending', 'analyzing', 'converting', 'ai_enhancing', 'verifying', 'completed', 'validated', 'failed'));

-- 3. Add comment
COMMENT ON COLUMN conversion_jobs.status IS 'Current status of the conversion job, including AI enhancement';
